from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from datetime import datetime
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)
messageList = ['Bạn là nhất!', 'Nhất bạn rồi.', 'Bạn đúng là nhất rồi.']


@app.route('/')
def sessions():
    return render_template('index.html')

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('templates/assets', path)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    response = random.choice(messageList)
    current_time = datetime.now().strftime("%H:%M")
    print('received my event: ' + json['message'])
    socketio.emit('my response', {'message': json['message'], 'time': current_time}, callback=messageReceived)
    socketio.emit('bot response', {
        'response': response,
        'time': current_time
    })


@socketio.on('connected')
def handle_connected(json, methods=['GET', 'POST']):
    print('Recieved from client: ' + str(json))


if __name__ == '__main__':
    socketio.run(app, debug=True)
