from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db


class User(db.Model):
    __tablename__ = 'user'
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, username, password, firstname, lastname) -> None:
        self.username = username
        self.set_password(password)
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password) -> None:
        self.password = generate_password_hash(password, method='sha256')

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname
        }


class Student(User):
    __tablename__ = 'student'
    # Fields
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # Relationships
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __init__(self, username, password, firstname, lastname):
        super().__init__(username, password, firstname, lastname)

    def __repr__(self):
        return f"<Student {self.username}>"
    def get_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname
        }


class Admin(User):
    __tablename__ = 'admin'
    # Fields
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    # Relationships
    company = db.relationship('Company', back_populates='admins')

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def __init__(self, username, password, firstname, lastname, company_id) -> None:
        super().__init__(username, password, firstname, lastname)
        self.company_id = company_id

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'company_id': self.company_id
        }

    def __repr__(self):
        return f"<Admin {self.username} Company: {self.company.name if self.company else 'None'}>"


class Staff(User):
    __tablename__ = 'staff'
    # Fields
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    # Relationships
    company = db.relationship('Company', back_populates='staff_members')

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }

    def __init__(self, username, password, firstname, lastname, company_id) -> None:
        super().__init__(username, password, firstname, lastname)
        self.company_id = company_id

    def __repr__(self) -> str:
        return f"<Staff {self.username} Company: {self.company.name if self.company else 'None'}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'company_id': self.company_id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username
        }


class Company(db.Model):
    __tablename__ = 'company'
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    # Relationships
    jobs = db.relationship('Job', back_populates='company', cascade='all, delete-orphan')
    staff_members = db.relationship('Staff', back_populates='company')
    admins = db.relationship('Admin', back_populates='company')
    applications = db.relationship('Application', back_populates='company')
    shortlists = db.relationship('Shortlist', back_populates='company', cascade='all, delete-orphan')

    def __init__(self, name, description) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"<Company {self.name}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name
        }


class Job(db.Model):
    __tablename__ = 'job'
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')
    shortlists = db.relationship('Shortlist', back_populates='job', cascade='all, delete-orphan')


    def __init__(self, company_id, title, description) -> None:
        self.company_id = company_id
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return f"<Job {self.title} - Company ID: {self.company_id}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description
        }


class Application(db.Model):
    __tablename__ = 'application'
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cover_letter = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    company = db.relationship('Company', back_populates='applications')
    shortlist = db.relationship('Shortlist', back_populates='application', cascade='all, delete-orphan')

    def __init__(self, student_id, job_id, first_name, last_name, phone, email, cover_letter) -> None:
        self.student_id = student_id
        self.job_id = job_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.cover_letter = cover_letter

    def is_shortlisted(self) -> bool:
        shortlist = Shortlist.query.filter_by(application_id=self.id).first()
        return shortlist is not None

    def __repr__(self) -> str:
        return f"<Application Student ID: {self.student_id} Job ID: {self.job_id}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id
        }


class Shortlist(db.Model):
    __tablename__ = 'shortlist'
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    # Relationships
    application = db.relationship('Application', back_populates='shortlist')
    job = db.relationship('Job', back_populates='shortlists')
    company = db.relationship('Company', back_populates='shortlists')

    def __init__(self, job_id, application_id) -> None:
        self.job_id = job_id
        self.application_id = application_id

    def __repr__(self) -> str:
        return f"<Shortlist Job ID: {self.job_id} Application ID: {self.application_id}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'job_id': self.job_id,
            'application_id': self.application_id
        }
    

__table_args__ = (
    db.UniqueConstraint('job_id', 'application_id', name='_job_application_uc'),
)
