from App.models import Company, Application, Job, Student, Shortlist
from App.database import db


def create_company(name, description) -> Company:
    company = Company(name=name)
    db.session.add(company)
    db.session.commit()
    return company

def add_student_to_shortlist(job_id, student_id) -> bool:
    job = Job.query.get(job_id)
    student = Student.query.get(student_id)
    if job and student:
        shortlist = Shortlist(job_id=job.id, student_id=student.id)
        db.session.add(shortlist)
        db.session.commit()
        return True
    return False

def create_application(job_id, student_id) -> bool:
    job = Job.query.get(job_id)
    student = Student.query.get(student_id)
    if job and student:
        application = Application(job_id=job.id, student_id=student.id)
        db.session.add(application)
        db.session.commit()
        return True
    return False

def create_job(company_id, title, description) -> bool:
    company = Company.query.get(company_id)
    if company:
        job = Job(company_id=company.id, title=title, description=description)
        db.session.add(job)
        db.session.commit()
        return True
    return False

def get_all_companies():
    return Company.query.all()

def get_all_jobs():
    return Job.query.all()

def get_all_students():
    return Student.query.all()

def get_all_applications():
    return Application.query.all()

def get_all_shortlists():
    return Shortlist.query.all()
