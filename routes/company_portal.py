from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from models.models import db, Company, Job, Application, Student, Placement
from sqlalchemy import func
from datetime import datetime

company = Blueprint('company_workspace', __name__)

def only_company():
    if not session.get("company_id"):
        return redirect(url_for("authentication.login"))
    return None

@company.route("/company/home")
def company_home():
    access = only_company()
    if access:
        return access
    
    company_id = session.get("company_id")
    company_name = Company.query.get(company_id).name
    industry = Company.query.get(company_id).industry
    # Only show students who are not placed OR placed by THIS company
    placed_student_ids_subquery = db.session.query(Application.student_id).filter(Application.status == 'Placed').join(Job).filter(Job.company_id != company_id).subquery()
    
    analysis = {
        "total_jobs" : Job.query.filter_by(company_id=company_id).count(),
        "verified_jobs" : Job.query.filter_by(company_id=company_id, admin_approval="Verified").count(),
        "waiting_jobs" : Job.query.filter_by(company_id=company_id, admin_approval="Pending").count(),
        "total_applications" : Application.query.join(Job).filter(Job.company_id == company_id).filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "review_pending" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Review Pending").filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "shortlisted" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Shortlisted").filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "interviewed" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Interviewed").filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "offered" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Offered").filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "rejected" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Rejected").filter(~Application.student_id.in_(placed_student_ids_subquery)).count(),
        "placed" : Application.query.join(Job).filter(Job.company_id == company_id, Application.status == "Placed").count(),
    }

    jobs = Job.query.filter_by(company_id=company_id).all()
    
    # Application trend over months
    all_apps = Application.query.join(Job).filter(Job.company_id == company_id).all()
    
    monthly_counts = {
        'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0, 
        'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0
    }
 
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Now loop through each application and increment the month count
    for app in all_apps:
        if app.applied:
            # We get the month number (1-12)
            month_num = int(app.applied.strftime("%m"))
            # Get the name from our list (index is month_num - 1)
            name = month_names[month_num - 1]
            # Increment 
            monthly_counts[name] = monthly_counts[name] + 1
            
    # Prepare the final lists for the chart
    trend_labels = []
    trend_data = []
    
    # Use the ordered list to make sure the chart is in the right order
    for month in month_names:
        trend_labels.append(month)
        # count from our dictionary
        count_val = monthly_counts[month]
        trend_data.append(count_val)

    return render_template("/company/home.html", 
                         analysis=analysis, 
                         jobs=jobs, 
                         company_name=company_name, 
                         industry=industry,
                         trend_labels=trend_labels,
                         trend_data=trend_data)


@company.route('/company/job/create', methods=['GET', 'POST'])
def create_job():
    access = only_company()
    if access:
        return access
    if request.method == 'POST':
        title = request.form.get("title")
        about = request.form.get("about")
        salary = request.form.get("salary")
        location = request.form.get("location")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        deadline = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d")
        min_cgpa = request.form.get("min_cgpa")
        company_id = session.get("company_id")
        job = Job(title=title, about=about, salary=salary, location=location, 
                  skills=skills, experience=experience, deadline=deadline, min_cgpa=min_cgpa,
                  company_id=company_id)
        db.session.add(job)
        db.session.commit()
        return redirect(url_for("company_workspace.company_home"))
    return render_template("/company/create_job.html")

@company.route('/company/job/<int:id>/change')
def change_job_status(id):
    access = only_company()
    if access:
        return access
    job = Job.query.get(id)
    if job and job.company_id == session.get("company_id") and job.admin_approval == "Verified":
        job.status = "Closed" if job.status == "Accepting Applications" else "Accepting Applications"
        db.session.commit()
    return redirect(url_for("company_workspace.job_list"))

@company.route('/company/application/<int:id>/change-status/<string:new_status>')
def change_application_status(id, new_status):
    access = only_company()
    if access:
        return access
    app = Application.query.get(id)
    if app and app.job.status != "Closed" and app.job.company_id == session.get("company_id"):
        # Check if student is already placed by ANY other job
        existing_placement = Application.query.filter(Application.student_id == app.student_id, Application.status == "Placed").first()
        if existing_placement and existing_placement.job_id != app.job_id:
            flash("This candidate has already been placed in another company.", "warning")
            return redirect(url_for("company_workspace.applications", id=app.job_id))

        if (app.status == "Placed") and new_status != "Placed":
            flash("You cannot change the status of a placed candidate.", "warning")
            return redirect(url_for("company_workspace.applications", id=app.job_id))
            
        app.status = new_status
        
        # If new status is Placed, also create a record in Placement table
        if new_status == "Placed":
            # Check if record exists in Placement table
            place_rec = Placement.query.filter_by(student_id=app.student_id).first()
            if not place_rec:
                place_rec = Placement(
                    student_id=app.student_id,
                    job_id=app.job_id,
                    placement_date=datetime.now()
                )
                db.session.add(place_rec)

        db.session.commit()
        return redirect(url_for("company_workspace.applications", id=app.job_id))
    flash("Action Not Allowed", "warning")
    return redirect(url_for("company_workspace.company_home"))

@company.route('/company/job/<int:id>/applications')
def applications(id):
    access = only_company()
    if access:
        return access
    company_id = session.get("company_id")
    # Student record visibility
    placed_somewhere_else = db.session.query(Application.student_id).filter(Application.status == 'Placed').join(Job).filter(Job.company_id != company_id).subquery()
    applications = Application.query.filter_by(job_id=id).filter(~Application.student_id.in_(placed_somewhere_else)).all()
    return render_template("/company/applications.html", applications=applications)

@company.route('/company/job/list')
def job_list():
    access = only_company()
    if access:
        return access
    company_id = session.get("company_id")
    jobs = Job.query.filter_by(company_id=company_id).all()
    return render_template("/company/job_list.html", jobs=jobs)

@company.route('/company/applications/all')
def view_all_applications():
    access = only_company()
    if access:
        return access
    company_id = session.get("company_id")
    # VISIBILITY FILTER
    placed_somewhere_else = db.session.query(Application.student_id).filter(Application.status == 'Placed').join(Job).filter(Job.company_id != company_id).subquery()
    applications = Application.query.join(Job).filter(Job.company_id == company_id, Job.admin_approval=="Verified").filter(~Application.student_id.in_(placed_somewhere_else)).all()
    return render_template("/company/applications.html", applications=applications, title="All Applications")

@company.route('/company/shortlisted')
def shortlisted():
    access = only_company()
    if access:
        return access
    company_id = session.get("company_id")
    # VISIBILITY FILTER
    placed_somewhere_else = db.session.query(Application.student_id).filter(Application.status == 'Placed').join(Job).filter(Job.company_id != company_id).subquery()
    applications = Application.query.join(Job).filter(Job.company_id == company_id).filter(Application.status.in_(['Shortlisted', 'Interviewed', 'Offered', 'Placed'])).filter(~Application.student_id.in_(placed_somewhere_else)).all()
    return render_template("/company/shortlisted.html", applications=applications)