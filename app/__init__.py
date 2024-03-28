'''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/forumm'
app.config['UPLOAD_FOLDER'] = 'uploads'

CORS(app)

db = SQLAlchemy(app)




# Import routes here to avoid circular imports
from app.routes import user_routes, post_routes, page_routes,friend_route

'''