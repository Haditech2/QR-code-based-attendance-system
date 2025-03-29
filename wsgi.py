<<<<<<< HEAD
from app import create_app
from config import config
import os

app = create_app(config[os.getenv('FLASK_ENV', 'default')])

if __name__ == "__main__":
    app.run()
=======
from run import app

if __name__ == "__main__":
    app.run() 
>>>>>>> 5ce8070 (Update app initialization for Gunicorn deployment)
