""" Flask-based control console.

    Testing:
        ../venv/bin/gunicorn -w 4 --worker-class socketio.sgunicorn.GeventSocketIOWorker -b 0.0.0.0:5000 www:app

"""
# Generic imports
import base64
import flask
import xmlrpclib

# Create the flask app
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # TODO: change...

# Create the socketio wrapper
import flask.ext.socketio
socketio = flask.ext.socketio.SocketIO(app)

# Create the sumo client
sumoclient = xmlrpclib.ServerProxy('http://127.0.0.1:8000')


## Websocket endpoints
@socketio.on('request_frame', namespace='/video')
def request_frame():
    frame = None
    try:
        frame = sumoclient.pic()
    except Exception:
        return
    if frame is None:
        return
    flask.ext.socketio.emit('frame', {
        'data': base64.b64encode(frame.data),
    })


## URL endpoints
@app.route('/')
def index():
    """ Main page.
    """
    return flask.render_template('index.html')


def launch():
    socketio.run(app)


if __name__ == '__main__':
    launch()
