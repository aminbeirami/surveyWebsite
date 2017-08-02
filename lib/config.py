#Written By Amin Beirami
import os
#MySQL configuration

SERVER = '127.0.0.1'
USERNAME = "local-username"
PASSWORD = "local-password"
DATABASE = "name-of-the-local-database"

#SecretKey is used to encrypt the session cookies

SECRET_KEY = os.urandom(24)