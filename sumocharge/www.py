""" Flask-based control console.
"""
import flask
import sumopy


app = flask.Flask(__name__)


@app.route('/')
def index():
    """ Main page.
    """
    return flask.render_template('index.html')


def gen(controller):
    """ Generator to return images.
    """
    while True:
        frame = controller.get_pic()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/drone_live')
def drone_live():
    """ MJPEG server.

        http://blog.miguelgrinberg.com/post/video-streaming-with-flask
    """
    return flask.Response(
            gen(sumopy.SumoController()),
            mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
