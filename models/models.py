from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(200), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    active = db.Column(db.Boolean, default=True)
    admin_approval = db.Column(db.String(20), default="Pending")

    jobs = db.relationship('Job', backref='company')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15))
    cgpa = db.Column(db.Float)
    branch = db.Column(db.String(100))
    grad_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume = db.Column(db.String(200))
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    active = db.Column(db.Boolean, default=True)

    applications = db.relationship('Application', backref='student')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    about = db.Column(db.Text)
    salary = db.Column(db.String(20))
    location = db.Column(db.String(100))
    skills = db.Column(db.Text)
    experience = db.Column(db.String(100))
    min_cgpa = db.Column(db.Float)
    deadline = db.Column(db.DateTime, default=db.func.current_timestamp())
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(20), default="Accepting Applications")
    admin_approval = db.Column(db.String(20), default="Pending")

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    applications = db.relationship('Application', backref='job')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default="Applied")
    applied = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    __table_args__ = (
    db.UniqueConstraint('student_id', 'job_id', name='unique_application'),
)

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placement_date = db.Column(db.DateTime)
    join_date=db.Column(db.DateTime)

    student = db.relationship('Student', backref='placement')
    job = db.relationship('Job', backref='placement')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))