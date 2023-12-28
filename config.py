import os

class Config:
    MTA_API_KEY = os.environ.get('MTA_API_KEY')
    DEBUG_LEVEL = os.environ.get('DEBUG_LEVEL', 'DEBUG')