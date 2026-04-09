from flask import Blueprint, request, redirect, url_for, render_template, session, current_app, flash
from models.models import db, Student, Job, Application, Company
import os
from werkzeug.utils import secure_filename

student = Blueprint('student_portal', __name__)

def student_access():
    if not session.get("student_id"):
        return redirect(url_for("authentication.login"))
    return None

@student.route("/student/home")
def student_home():
    check = student_access()
    if check:
        return check
    
    student_id = session.get("student_id")
    curr_student = Student.query.get(student_id)
    # applications with respective job and company data
    apps = Application.query.filter_by(student_id=student_id).all()
    
    analysis = {
        "applied": len(apps),
        "shortlisted": len([a for a in apps if a.status == "Shortlisted"]),
        "placed": len([a for a in apps if a.status == "Placed"]),
        "pending": len([a for a in apps if a.status == "Applied" or a.status == "Review Pending"])
    }
    
    return render_template("/student/home.html", student=curr_student, applications=apps, analysis=analysis)

@student.route("/student/profile/update", methods=["GET", "POST"])
def update_profile():
    check = student_access()
    if check:
        return check
        
    student_id = session.get("student_id")
    curr_student = Student.query.get(student_id)
    
    if request.method == "POST":
        curr_student.name = request.form.get("name")
        curr_student.branch = request.form.get("branch")
        curr_student.skills = request.form.get("skills")
        curr_student.phone = request.form.get("phone")
        curr_student.cgpa = float(request.form.get("cgpa"))
        curr_student.grad_year = int(request.form.get("grad_year"))
        
        # Sync session name
        session["student_name"] = curr_student.name
        
        # Handle Resume Update
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filename = f"{curr_student.email.split('@')[0]}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                curr_student.resume = filename
                
        db.session.commit()
        return redirect(url_for("student_portal.student_home"))
    
    return render_template("/student/update_profile.html", student=curr_student)

@student.route("/student/show-jobs")
def show_jobs():
    check = student_access()
    if check:
        return check
        
    student_id = session.get("student_id")
    query = request.args.get('q', '')
    # show only verified and open jobs
    jobs_search = Job.query.filter_by(admin_approval="Verified", status='Accepting Applications')
    
    if query:
        # Search by title, company name, or skills
        jobs_search = jobs_search.join(Job.company).filter(
            (Job.title.ilike(f'%{query}%')) | 
            (Company.name.ilike(f'%{query}%')) |
            (Job.skills.ilike(f'%{query}%'))
        )
    
    eligible_jobs = [job for job in jobs_search if job.min_cgpa <= Student.query.get(student_id).cgpa]
    
    # get IDs of jobs the student has already applied to
    applied_jobs = [app.job_id for app in Application.query.filter_by(student_id=student_id).all()]
    
    is_placed = block_application()
    
    return render_template("/student/show_jobs.html", jobs=eligible_jobs, applied_ids=applied_jobs, query=query, is_placed=is_placed)

@student.route("/student/jobs/<job_id>/submit-application", methods=["POST"])
def submit_application(job_id):
    check = student_access()
    if check:
        return check
        
    student_id = session.get("student_id")
    
    # check for duplicate
    existing = Application.query.filter_by(student_id=student_id, job_id=job_id).first()
    if existing:
        return redirect(url_for("student_portal.show_jobs"))
    if block_application():
        flash("You cannot apply for more jobs once placed.", "warning")
        return redirect(url_for("student_portal.student_home"))
    new_app = Application(student_id=student_id, job_id=job_id, status='Applied')
    db.session.add(new_app)
    db.session.commit()
    
    return redirect(url_for("student_portal.student_home"))

def block_application():
    student_id = session.get("student_id")
    apps = Application.query.join(Job).filter(Application.student_id==student_id).all()
    for app in apps:
        if app.status == 'Placed':
            return True
    return False