from App.models import Company, Application, Job, Student, Shortlist
from App.database import db


def create_company(name, description) -> Company:
    company = Company(name=name, description=description)
    db.session.add(company)
    db.session.commit()
    return company

def add_student_to_shortlist(job_id, application_id) -> bool:
    job = Job.query.get(job_id)
    application = Application.query.get(application_id)
    if job and application:
        shortlist = Shortlist(job_id=job.id, application_id=application.id)
        db.session.add(shortlist)
        db.session.commit()
        return True
    return False

def create_shortlist(job_id, application_id) -> bool:
    try:
        job = Job.query.get(job_id)
        application = Application.query.get(application_id)
        if job and application:
            shortlist = Shortlist(job_id=job.id, application_id=application.id)
            db.session.add(shortlist)
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating shortlist for job_id={job_id}, application_id={application_id}: {e}")
    return False

def create_application(student_id, job_id, first_name, last_name, phone, email, cover_letter):
    try:
        student = Student.query.get(student_id)
        job = Job.query.get(job_id)
        if student and job:
            application = Application(
                job_id=job.id,
                student_id=student.id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                cover_letter=cover_letter
            )
            db.session.add(application)
            db.session.commit()
            return application
    except Exception as e:
        db.session.rollback()
        print(f"Error creating application for student_id={student_id}, job_id={job_id}: {e}")
    return None

def create_job(company_id, title, description) -> bool:
    try:
        company = Company.query.get(company_id)
        if company:
            job = Job(company_id=company.id, title=title, description=description)
            db.session.add(job)
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating job for company_id={company_id}, title={title}: {e}")

    return False

def delete_job(job_id) -> bool:
    try:
        job = Job.query.get(job_id)
        if job:
            db.session.delete(job)
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting job with id={job_id}: {e}")
    return False

def delete_shortlist(shortlist_id) -> bool:
    try:
        shortlist = Shortlist.query.get(shortlist_id)
        if shortlist:
            db.session.delete(shortlist)
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting shortlist with id={shortlist_id}: {e}")
    return False

def delete_application(application_id) -> bool:
    try:
        application = Application.query.get(application_id)
        if application:
            db.session.delete(application)
            db.session.commit()
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting application with id={application_id}: {e}")
    return False


def get_all_companies() -> list[Company]:
    return Company.query.all()

def get_all_jobs(company_id) -> list[Job]:
    jobs = Job.query.filter_by(company_id=company_id).all()
    return jobs

def get_job_by_id(job_id) -> Job:
    job = Job.query.get(job_id)
    return job

def get_all_students():
    return Student.query.all()

def get_all_applications() -> list[Application]:
    return Application.query.all()

def get_all_shortlists() -> list[Shortlist]:
    return Shortlist.query.all()
