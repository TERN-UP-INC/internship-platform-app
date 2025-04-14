from .user import create_user, create_student, create_admin, create_staff
from .company import create_company, add_student_to_shortlist, create_job, create_application
from App.database import db
import csv
import os


def initialize():
    db.drop_all()
    db.create_all()

    project_root = os.path.dirname(os.path.abspath(__file__))

    # Students
    csv_path = os.path.join(project_root, '../data/students.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_student(username=row['username'], password=row['password'], firstname=row['firstname'], lastname=row['lastname'])

    # Companies
    csv_path = os.path.join(project_root, '../data/companies.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_company(name=row['name'], description=row['description'])

    # Admins
    csv_path = os.path.join(project_root, '../data/admins.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_admin(company_id=row['id'], username=row['username'], password=row['password'], firstname=row['firstname'], lastname=row['lastname'])

    # Staff
    csv_path = os.path.join(project_root, '../data/staff.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_staff(company_id=row['id'], username=row['username'], password=row['password'], firstname=row['firstname'], lastname=row['lastname'])

    # Jobs
    csv_path = os.path.join(project_root, '../data/jobs.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_job(company_id=row['id'], title=row['title'], description=row['description'])

    # Applications
    csv_path = os.path.join(project_root, '../data/applications.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            create_application(
                student_id=row['student_id'],
                job_id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                email=row['email'],
                cover_letter=row['cover_letter']
            )

    # Shortlist
    csv_path = os.path.join(project_root, '../data/shortlists.csv')
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            add_student_to_shortlist(job_id=row['id'], application_id=row['application_id'])


