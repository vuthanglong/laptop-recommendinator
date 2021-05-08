from flask import Flask, render_template
from flask_socketio import SocketIO
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
messageList = ['Bạn là nhất!', 'Nhất bạn rồi.', 'Bạn đúng là nhất rồi.']


@app.route('/')
def sessions():
    return render_template('session.html')


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
    socketio.emit('bot response', {
        'response': random.choice(messageList)
    })


@socketio.on('connected')
def handle_connected(json, methods=['GET', 'POST']):
    print('Recieved from client: ' + str(json))


if __name__ == '__main__':
    socketio.run(app, debug=True)
