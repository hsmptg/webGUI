from flask_socketio import SocketIO
#from flask.ext.socketio import SocketIO, emit
from flask import Flask, render_template

#===============================================================================
# import sys #exit
# import signal #signal
#===============================================================================

import sys
import boards
            
class WebGUI():
    def __init__(self):
        print("Started WebGUI")
        print 'Number of arguments:', len(sys.argv), 'arguments.'
        print 'Argument List:', str(sys.argv)
        app = Flask(__name__)
        app.config['DEBUG'] = False
        self.socketio = SocketIO(app)
        self.counter = -1;
                
        @app.before_first_request
        def initialize():
            print('Called only once, when the first request comes in')
            
        @app.route('/')
        def index():
            print("render index.html")
            return render_template('index.html')
        
        @self.socketio.on('connect', namespace='/test')
        def test_connect():
            if self.counter < 0:
                print("create socket")
                self.board = boards.Raspi()
                self.board.onMsg = self.onMsg
                self.counter = 0
            if self.counter == 0:
                print("connect socket")
                self.board.connect('192.168.1.93', 12345)
            self.counter += 1
            print("Counter= {0}".format(self.counter))
            print('Client connected')
        
        @self.socketio.on('disconnect', namespace='/test')
        def test_disconnect():
            self.counter -= 1
            if self.counter == 0:
                self.board.disconnect()
            print("Counter= {0}".format(self.counter))
            print('Client disconnected')
            
        @self.socketio.on('getVersion', namespace='/test')
        def getVersion():
            self.board.sendCmd('v')
                                        
        @self.socketio.on('ledRCtrl', namespace='/test')
        def ledRCtrl(message):
            print(message['led'])
            self.board.sendCmd('l1' if message['led'] else 'l0')
                                        
        self.socketio.run(app, host = '0.0.0.0', port = 5001)

    def onMsg(self, msg):
        print(msg)
        if msg[0] == 'b':
            state = True if msg=='b1' else False
            self.socketio.emit('but', {'state': state}, namespace='/test')
        elif msg[0] == 'v':
            self.socketio.emit('setVersion', {'version': msg}, namespace='/test')
        
if __name__ == '__main__':
    gui = WebGUI()