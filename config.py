import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eventbook-secret-key-2025')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:Razhmika#2096@localhost/event_booking_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
