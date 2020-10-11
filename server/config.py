import os


class Config:
    SECRET_KEY = os.environ.get('VENOM_SECRET_KEY') or 'test'
