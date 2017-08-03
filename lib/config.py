#Written By Amin Beirami
import os
#MySQL configuration

SERVER = '127.0.0.1'
USERNAME = "amin"
PASSWORD = "amin123"
DATABASE = "survey"

#SecretKey is used to encrypt the session cookies

SECRET_KEY = os.urandom(24)