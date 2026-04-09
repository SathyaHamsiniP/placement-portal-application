from flask import Blueprint, request, redirect, session, render_template, url_for
from models.models import db, Student, Company, Job, Application, Placement

from sqlalchemy import func
admin = Blueprint('admin', __name__)


# Only admin access
def only_admin():
    if not session.get("admin_id"):
        return redirect(url_for("authentication.login"))
    return None


@admin.route("/admin/panel")
def admin_panel():
    if "admin_id" not in session:
        return redirect("/login")

    access = only_admin()
    if access:
        return access

    from datetime import date
    today = date.today()

    analysis = {
        "total_students": Student.query.count(),
        "accepted_companies" : Company.query.filter_by(admin_approval='Verified').count(),
        "waiting_companies" : Company.query.filter_by(admin_approval='Pending').count(),
        "accepted_jobs" : Job.query.filter_by(admin_approval='Verified').count(),
        "waiting_jobs" : Job.query.filter_by(admin_approval='Pending').count(),
        "applications_received": Application.query.count(),
        "placements_done":Placement.query.filter(Placement.placement_date != None).count(),
        "apps_today": Application.query.filter(func.date(Application.applied) == today).count(),
        "jobs_today": Job.query.filter(func.date(Job.created) == today).count(),
        "students_today": Student.query.filter(func.date(Student.created) == today).count()
    }

    # Branch distribution across entire platform
    branch_stats = db.session.query(Student.branch, func.count(Application.id))\
        .join(Application, Student.id == Application.student_id)\
        .group_by(Student.branch).all()
    
    branch_labels = [row[0] or "General" for row in branch_stats]
    branch_counts = [row[1] for row in branch_stats]

    return render_template("admin/panel.html", 
                         analysis=analysis,
                         branch_labels=branch_labels,
                         branch_counts=branch_counts)

# Approve/reject companies
@admin.route('/admin/companies/waiting')
def companies_waiting():

    access = only_admin()
    if access:
        return access

    companies = Company.query.filter_by(admin_approval='Pending').all()

    return render_template(
        "admin/companies_waiting.html",
        companies=companies
    )


@admin.route('/admin/accept/company/<int:id>')
def company_accept(id):

    access = only_admin()
    if access:  
        return access

    company = Company.query.get(id)

    if company is None:
        return {"error": "Company does not exist"}, 404

    company.admin_approval = 'Verified'
    db.session.commit()

    return redirect(url_for("admin.companies_waiting"))


@admin.route('/admin/reject/company/<int:id>')
def company_reject(id):

    access = only_admin()
    if access:
        return access

    company = Company.query.get(id)

    if company is None:
        return {"error": "Company does not exist"}, 404

    db.session.delete(company)
    db.session.commit()

    return redirect(url_for("admin.companies_waiting"))

# Approve/reject jobs
@admin.route('/admin/jobs/waiting')
def jobs_waiting():

    access = only_admin()
    if access:
        return access

    jobs = Job.query.filter_by(admin_approval='Pending').all()

    return render_template(
        "admin/jobs_waiting.html",
        jobs=jobs
    )


@admin.route('/admin/jobs/accept/<int:id>')
def job_accept(id):

    access = only_admin()
    if access:
        return access

    job = Job.query.get(id)

    if job is None:
        return {"error": "No Such Job"}, 404

    job.admin_approval = 'Verified'
    db.session.commit()

    return redirect(url_for("admin.jobs_waiting"))


@admin.route('/admin/jobs/reject/<int:id>')
def job_reject(id): 

    access = only_admin()
    if access:
        return access

    job = Job.query.get(id)

    if job is None:
        return {"error": "No Such Job"}, 404

    db.session.delete(job)
    db.session.commit()

    return redirect(url_for("admin.jobs_waiting"))


# View students/companies/jobs/applications
@admin.route('/admin/student-list')
def list_students():

    access = only_admin()
    if access:
        return access

    q = request.args.get('q', '').strip()

    if q:
        filters = (
            Student.name.ilike(f'%{q}%') |
            Student.email.ilike(f'%{q}%')
        )
        if q.isdigit():
            filters = filters | (Student.id == int(q))
        data = Student.query.filter(filters).all()
    else:
        data = Student.query.all()

    return render_template(
        "admin/list_students.html",
        students=data,
        query=q
    )



@admin.route('/admin/company-list')
def list_companies():

    access = only_admin()
    if access:
        return access

    q = request.args.get('q', '').strip()

    if q:
        filters = (
            Company.name.ilike(f'%{q}%') |
            Company.industry.ilike(f'%{q}%')
        )
        if q.isdigit():
            filters = filters | (Company.id == int(q))
        data = Company.query.filter(filters).all()
    else:
        data = Company.query.all()

    return render_template(
        "admin/list_companies.html",
        companies=data,
        query=q
    )


@admin.route('/admin/job-list')
def list_jobs():

    access = only_admin()
    if access:
        return access

    data = Job.query.all()

    return render_template(
        "admin/list_jobs.html",
        jobs=data
    )


@admin.route('/admin/application-list')
def list_applications():

    access = only_admin()
    if access:
        return access

    data = Application.query.all()

    return render_template(
        "admin/list_applications.html",
        applications=data
    )


# blacklist students/companies
@admin.route("/admin/students/blacklist/<int:id>")
def blacklist_student(id):

    access = only_admin()
    if access:
        return access

    student = Student.query.get(id)

    if student is None:
        return {"error": "Student not found"}, 404

    student.active = False
    db.session.commit()

    return redirect(url_for("admin.list_students"))


@admin.route("/admin/companies/blacklist/<int:id>")
def blacklist_company(id):

    access = only_admin()
    if access:
        return access

    company = Company.query.get(id)

    if company is None:
        return {"error": "Company not found"}, 404

    company.active = False
    db.session.commit()

    return redirect(url_for("admin.list_companies"))