"""
Flask extensions (initialized without app)
"""
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

mysql = MySQL()
bcrypt = Bcrypt()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
