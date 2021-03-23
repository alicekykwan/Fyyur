import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL - DONE
database_username = os.environ.get('database_username')
database_password = os.environ.get('database_password')
database_username = 'testuser'
database_password = ''
database_name = 'fyyur'
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(database_username,database_password,'localhost:5432',database_name)
