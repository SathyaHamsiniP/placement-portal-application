from flask import Flask
from config import Config
from models.models import db, Admin
from routes.authentication import auth
from routes.admin import admin
from routes.company_portal import company
from routes.student_portal import student

app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = "sathya-key"
app.config['UPLOAD_FOLDER'] = 'static/uploads/resumes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

import os
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(company)
app.register_blueprint(student)

db.init_app(app)

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin=Admin(email='admin@placement.com', password='admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)