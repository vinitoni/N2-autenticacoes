# config.py

class Config:
    SECRET_KEY = '123456789C!'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''  
    MAIL_PASSWORD = ''   
