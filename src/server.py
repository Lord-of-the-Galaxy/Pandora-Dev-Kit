import os
import json
from functools import lru_cache

from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit

import colorama

colorama.init()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
app.config['GAME_LOGS'] = os.path.join(os.getcwd(), 'game_logs')

socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', games=get_games())


@app.route('/<game_id>')
def game(game_id):
    if game_id in get_games():
        return render_template('game.html', game_id=game_id)
    else:
        return redirect(url_for('index'))


def get_games():
    return [f[5:-5] for f in os.listdir(app.config['GAME_LOGS']) if f[:5] == 'game_' and f[-5:] == '.plog']


@lru_cache(maxsize=3)
def get_game_log(game_id):
    with open(os.path.join(app.config['GAME_LOGS'], "game_{}.plog".format(game_id))) as f:
        log = json.load(f)
    return log


@socketio.event
def get_game_info(data):
    game_id = data['game_id']
    try:
        log = get_game_log(game_id)
        game_info = log['info']
        emit('game_info', game_info)
    except EnvironmentError:
        print("Error getting game", game_id)


@socketio.event
def get_frame(data):
    game_id = data['game_id']
    frame_num = data['frame_num']
    try:
        log = get_game_log(game_id)
        frame = log['frames'][frame_num]
        emit('frame', {'game_id': game_id, 'frame_num': frame_num, 'frame': frame})
    except EnvironmentError:
        print("Error getting game", game_id)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
