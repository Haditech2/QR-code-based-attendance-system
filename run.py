<<<<<<< HEAD
import os
from app import create_app
from config import config

app = create_app(config[os.getenv('FLASK_ENV', 'default')])

if __name__ == '__main__':
=======
import os
from app import create_app
from config import config

app = create_app(config[os.getenv('FLASK_ENV', 'default')])

if __name__ == '__main__':
>>>>>>> 5ce8070 (Update app initialization for Gunicorn deployment)
    app.run() 