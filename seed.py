import os
from app import app
from models.models import db, Admin, Company, Student, Job, Application, Placement
from datetime import datetime, timedelta

def seed_data():
    with app.app_context():
        print(f"DEBUG: Seeding to {app.config['SQLALCHEMY_DATABASE_URI']}")
        # Clear existing data (except Admin)
        print("Clearing existing data...")
        Placement.query.delete()
        Application.query.delete()
        Job.query.delete()
        Student.query.delete()
        Company.query.delete()
        
        db.session.commit()

        print("Seeding Companies...")
        industries = ["Software", "Hardware", "Finance", "Consulting", "Cloud", "AI", "E-commerce", "HealthTech", "EdTech", "Logistics"]
        companies = []
        for i in range(1, 11):
            status = "Verified"
            active = True
            if i == 8: status = "Pending"
            if i == 9: status = "Rejected"
            if i == 10: active = False
            
            c = Company(
                name=f"Company {i} Inc.",
                email=f"company{i}@demo.com",
                password="Demo123",
                industry=industries[i-1],
                website=f"https://company{i}.com",
                admin_approval=status,
                active=active
            )
            db.session.add(c)
            companies.append(c)
        
        db.session.commit()

        print("Seeding Students...")
        branches = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Chemical Engineering"]
        students = []
        for i in range(1, 21):
            active = True
            if i == 20: active = False 
            
            s = Student(
                name=f"Student {i}",
                email=f"student{i}@demo.com",
                password="Demo123",
                phone=f"98765432{i:02d}",
                branch=branches[i % 5],
                cgpa=round(7.0 + (i % 3) + (i * 0.05), 2),
                grad_year=2024 + (i % 2),
                skills="Python, SQL, Communication",
                active=active
            )
            db.session.add(s)
            students.append(s)
        
        db.session.commit()

        print("Seeding Jobs...")
        jobs = []
        for i in range(7): 
            co = companies[i]
            for j in range(1, 3):
                job_status = "Accepting Applications"
                admin_job_status = "Verified"
                
                if i == 0 and j == 1: job_status = "Closed"
                if i == 6: admin_job_status = "Pending"

                job = Job(
                    title=f"{co.industry} Role {j}",
                    about=f"Exciting opportunity at {co.name} for a {co.industry} enthusiast.",
                    salary=f"{5 + i + j} LPA",
                    location="Hybrid" if j % 2 == 0 else "Remote",
                    skills="Technical Skills, Problem Solving",
                    experience="0-2 years",
                    min_cgpa=6.5 + (j * 0.1),
                    deadline=datetime.now() + timedelta(days=15),
                    status=job_status,
                    admin_approval=admin_job_status,
                    company_id=co.id
                )
                db.session.add(job)
                jobs.append(job)
        
        db.session.commit()

        print("Seeding Applications...")
        # Standardized Statuses: Applied, Review Pending, Shortlisted, Interviewed, Offered, Placed, Rejected
        app_statuses = ["Applied", "Review Pending", "Shortlisted", "Interviewed", "Offered", "Placed", "Rejected"]
        
        # Student 1 has a variety
        for j_idx in range(len(app_statuses)):
            status = app_statuses[j_idx]
            new_app = Application(
                student_id=students[0].id,
                job_id=jobs[j_idx].id,
                status=status
            )
            db.session.add(new_app)
            
            # If status is Placed, create Placement record
            if status == "Placed":
                p = Placement(
                    student_id=students[0].id,
                    job_id=jobs[j_idx].id,
                    placement_date=datetime.now()
                )
                db.session.add(p)

        # Others
        for s_idx in range(1, 15):
            for j_idx in [(s_idx*2) % len(jobs), (s_idx*3) % len(jobs)]:
                existing = Application.query.filter_by(student_id=students[s_idx].id, job_id=jobs[j_idx].id).first()
                if not existing:
                    new_app = Application(
                        student_id=students[s_idx].id,
                        job_id=jobs[j_idx].id,
                        status="Applied"
                    )
                    db.session.add(new_app)
        
        db.session.commit()
        print("Successfully seeded data with standardized statuses and placements!")

if __name__ == "__main__":
    seed_data()
