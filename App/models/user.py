from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, username, password, firstname, lastname):
        self.username = username
        self.password = 
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self):
        return f"<User {self.username}>"

    def check_password(self, password):
        return self.password == password  

    



class Student(User):
    __tablename__ = 'student'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __init__(self, username, password, firstname, lastname):
        super().__init__(username, password, firstname, lastname)

    def __repr__(self):
        return f"<Student {self.username}>"



class Admin(User):
    __tablename__ = 'admin'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    company = db.relationship('Company', back_populates='admins')

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __init__(self, username, password, firstname, lastname):
        super().__init__(username, password, firstname, lastname)
        self.company = company

    def __repr__(self):
        return f"<Admin {self.username} - Company: {self.company.name if self.company else 'None'}>"




class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    company = db.relationship('Company', back_populates='staff_members')

    def add_to_shortlist(self, job_id, student_id):
        shortlist = Shortlist(job_id=job_id, student_id=student_id)
        db.session.add(shortlist)
        db.session.commit()

    def remove_from_shortlist(self, job_id, student_id):
        Shortlist.query.filter_by(job_id=job_id, student_id=student_id).delete()
        db.session.commit()



class Company(db.Model):
    __tablename__ = 'company'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    jobs = db.relationship('Job', back_populates='company', cascade='all, delete-orphan')
    staff_members = db.relationship('Staff', back_populates='company')
    admins = db.relationship('Admin', back_populates='company')



class Job(db.Model):
    __tablename__ = 'job'
    job_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')
    shortlist = db.relationship('Shortlist', back_populates='job', uselist=False, cascade='all, delete-orphan')



class Application(db.Model):
    __tablename__ = 'application'
    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.user_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'))

    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')


#
class Shortlist(db.Model):
    __tablename__ = 'shortlist'
    shortlist_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'))
    student_id = db.Column(db.Integer)

    job = db.relationship('Job', back_populates='shortlist')
