from App.models import User, Student, Staff, Admin, Company
from App.database import db

def create_user(username, password, firstname, lastname):
    newuser = User(username=username, password=password, firstname=firstname, lastname=lastname)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def create_student(username, password, firstname, lastname):
    student = Student(username=username, password=password, firstname=firstname, lastname=lastname)
    db.session.add(student)
    db.session.commit()
    return student

def create_staff(company_id, username, password, firstname, lastname):
    staff = Staff(company_id=company_id, username=username, password=password, firstname=firstname, lastname=lastname)
    db.session.add(staff)
    db.session.commit()
    return staff

def create_admin(company_id, username, password, firstname, lastname):
    admin = Admin(company_id=company_id, username=username, password=password, firstname=firstname, lastname=lastname)
    db.session.add(admin)
    db.session.commit()
    return admin

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_admin(id) -> Admin:
    return Admin.query.get(id)

def get_user(id):
    return User.query.get(id)

def get_student(id):
    return Student.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None
