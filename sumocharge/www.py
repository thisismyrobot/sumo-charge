""" Flask-based control console.
"""
# Generic imports
import base64
import collections
import flask
import threading
import SocketServer

# Create the flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # TODO: change...


# Create the socketio wrapper
import flask.ext.socketio
socketio = flask.ext.socketio.SocketIO(app)


# Thread/process-safe queue of images
image_queue = collections.deque(maxlen=30)


## URL endpoints
@app.route('/')
def index():
    """ Main page.
    """
    return flask.render_template('index.html')


## Websocket endpoints
@socketio.on('request_frame', namespace='/video')
def request_frame():
    try:
        flask.ext.socketio.emit('frame', {
            'data': image_queue.pop(),
        })
    except IndexError:
        pass


## General methods
def start_video_thread(sockio_mod):

    class Handler(SocketServer.BaseRequestHandler):

        def handle(self):
            data = self.request[0]

            # ID pic frames
            if data.startswith('<\x03\x7d'):
                image_queue.append(base64.b64encode(data[13:]))

    # Patch to recieve video packets (+ direction indicator)
    SocketServer.UDPServer.max_packet_size = 65001
    server = SocketServer.UDPServer(('127.0.0.1', 65432), Handler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()


def launch():
    # Start the thread that will emit video frames as they arrive
    start_video_thread(flask.ext.socketio)

    # Start the web app
    socketio.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    launch()
