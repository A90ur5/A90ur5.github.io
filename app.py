#-*- coding: utf-8 -*-
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from flask import Flask, session, redirect, render_template, request, flash, url_for, json
from flask_socketio import SocketIO, emit, join_room
from functools import wraps
from datetime import datetime
import base64
import os
import uuid
import io

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = str(os.urandom(12).hex())  # Change this!
socketio = SocketIO(app)
async_mode = "eventlet"


def to_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        get_fun = func(*args, **kwargs)
        return json.dumps(get_fun)

    return wrapper

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return render_template("index.html", **locals())

@socketio.on('join')
def join(message):
    join_room(message['room'])
    print('join')


@socketio.on('connect')
def test_connect():
    print('connect')

'''
@socketio.on('sendInquiry')
def send_inquiry(msg):
    user_id = session.get('user_id')
    create_date = datetime.now()

    data_message = Message(
        user_name=user_id,
        messages=msg['msg'],
        create_date=create_date
    )
    db.session.add(data_message)
    db.session.commit()
    #mug_shot = UserAccounts.query.filter_by(UserName=user_id).first().MugShot
    data = {
        'time': create_date.strftime('%H:%M'),
        'Name': user_id,
        'PictureUrl': "0.jpg",
        'msg': msg['msg'],
    }
    emit('getInquiry', data, room=msg['room'])
'''
@app.route('/pushdataWRYYYYYYYYYYYYYYY', methods=['GET'])
def pushingData():
    create_date = datetime.now()
    b32_data = request.args.get('msg')
    b32_player = request.args.get('player')
    b32_sign = request.args.get('sign')

    try:
        pushing_player = base64.b32decode(b32_player)
        pushing_data = base64.b32decode(b32_data)
        sign = base64.b32decode(b32_sign)

    except TypeError:
        print("b32decode Error")
        return ''

    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(pushing_player+pushing_data)
    is_verify = verifier.verify(digest, sign)
    if not is_verify:
        print("signature error, drop the message")
        print("player: " + pushing_player.decode('utf-8'))
        print("message: " + pushing_data.decode('utf-8'))
    else:
        try:
            data = {
                'time': create_date.strftime('%H:%M'),
                'msg': pushing_data.decode('utf-8'),
                'player' : pushing_player.decode('utf-8'),
            }
            socketio.emit('getInquiry', data, room='A_Room')
        except UnicodeDecodeError:
            print("UnicodeDecodeError")
    return ''


if __name__ == '__main__':
    
    with open('../connection-public.pem', 'r') as f:
        key = f.read()
    rsakey = RSA.importKey(key)
    socketio.run(app, host='0.0.0.0', port = 80)
