from flask import Blueprint, request, redirect, url_for, render_template, session, current_app
from models.models import db, Student, Company, Admin
import os
from werkzeug.utils import secure_filename

auth = Blueprint('authentication', __name__)

@auth.route("/")
def index():
    return render_template("index.html")

@auth.route("/student/signup", methods=["GET","POST"])
def student_signup():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        branch = request.form.get("branch")
        cgpa = request.form.get("cgpa")
        grad_year = request.form.get("grad_year")
        skills = request.form.get("skills")

        duplicate_student = Student.query.filter_by(email=email).first()
        if duplicate_student:
            return "Email already exists"

        # File uploading
        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Email prefix to get unique filename
                filename = f"{email.split('@')[0]}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                resume_filename = filename

        student = Student(name=name, email=email, password=password, 
                         phone=phone, branch=branch, cgpa=cgpa, 
                         grad_year=grad_year, skills=skills, resume=resume_filename)
        db.session.add(student)
        db.session.commit()

        return redirect('/login')

    return render_template("/auth/student_signup.html")


@auth.route("/company/signup", methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        industry = request.form.get("industry")
        website = request.form.get("website")

        duplicate_company = Company.query.filter_by(email=email).first()
        if duplicate_company:
            return "Company email already exists"

        company=Company(name=name, email=email, password=password, admin_approval="Pending", industry=industry)
        db.session.add(company)
        db.session.commit()

        return redirect('/login')

    return render_template("/auth/company_signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        if role == "admin":
            admin = Admin.query.filter_by(email=email).first()
            if admin and admin.password == password:
                session.permanent = True
                session["admin_id"] = admin.id
                session["admin_name"] = "Administrator"
                return redirect("/admin/panel")
            else:
                return render_template("/auth/login.html", error="Invalid admin email or password.")

        elif role == "student":
            student = Student.query.filter_by(email=email).first()
            if student and student.password == password:
                if not student.active:
                    return render_template("/auth/login.html", error="Your account has been deactivated.")
                session.permanent = True
                session["student_id"] = student.id
                session["student_name"] = student.name
                return redirect("/student/home")
            else:
                return render_template("/auth/login.html", error="Invalid student email or password.")

        elif role == "company":
            company = Company.query.filter_by(email=email).first()
            if company and company.password == password:
                if company.admin_approval == "Pending":
                    return render_template("/auth/login.html", error="Company not approved yet.")
                if not company.active:
                    return render_template("/auth/login.html", error="Your account has been deactivated.")
                
                session.permanent = True
                session["company_id"] = company.id
                session["company_name"] = company.name
                return redirect("/company/home")
            else:
                return render_template("/auth/login.html", error="Invalid company email or password.")

    return render_template("/auth/login.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("authentication.login"))


