import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = "never-say-never-again"
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1694373074164463',
        'secret': 'b81a86062d08bac28b3397465b498e9es'
    }
    }
UPLOAD_FOLDER = os.path.join(basedir,'static/uploads/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc'])
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')