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
        """Initialize a User object with username, password, firstname, and lastname."""
        self.username = username
        self.set_password(password)
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self) -> str:
        """Return a string representation of the User object."""
        return f"<User {self.username}>"

    def check_password(self, password) -> bool:
        """Check if the provided password matches the stored hashed password."""
        return check_password_hash(self.password, password)

    def set_password(self, password) -> None:
        """Set the password for the user, hashing it before storing."""
        self.password = generate_password_hash(password, method='sha256')

    def get_json(self) -> dict:
        """Return a JSON representation of the User object."""
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

    def create_application(self, job_id) -> bool:
        """Create an application for a specific job."""
        if not job_id:
            return False

        try:
            application = Application(student_id=self.id, job_id=job_id)
            db.session.add(application)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error creating application: {e}")
            return False

    def delete_application(self, job_id) -> bool:
        """Delete an application for a specific job."""
        if not job_id:
            return False

        try:
            application = Application.query.filter_by(student_id=self.id, job_id=job_id).first()
            if application:
                db.session.delete(application)
                db.session.commit()
                return True
            else:
                print("Application not found.")
                return False
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting application: {e}")
            return False



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
        """Initialize an Admin object with username, password, firstname, lastname, and company."""
        super().__init__(username, password, firstname, lastname)
        self.company_id = company_id

    def get_json(self) -> dict:
        """Return a JSON representation of the Admin object."""
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
        """Initialize a Staff object with company_id."""
        super().__init__(username, password, firstname, lastname)
        self.company_id = company_id

    def __repr__(self) -> str:
        return f"<Staff {self.username} Company: {self.company.name if self.company else 'None'}>"

    def get_json(self) -> dict:
        """Return a JSON representation of the Staff object."""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username
        }

    def add_to_shortlist(self, job_id, student_id) -> bool:
        """Add a student to the shortlist for a specific job."""
        if not job_id or not student_id:
            return False

        try:
            shortlist = Shortlist(job_id=job_id, student_id=student_id)
            db.session.add(shortlist)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error adding to shortlist: {e}")
            return False

    def remove_from_shortlist(self, job_id, student_id) -> bool:
        """Remove a student from the shortlist for a specific job."""
        shortlist = Shortlist.query.filter_by(job_id=job_id, student_id=student_id)
        if not shortlist:
            return False

        try:
            shortlist.delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error removing from shortlist: {e}")
            return False


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

    def __init__(self, name) -> None:
        """Initialize a Company object with name."""
        self.name = name

    def __repr__(self) -> str:
        return f"<Company {self.name}>"

    def get_json(self) -> dict:
        """Return a JSON representation of the Company object."""
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
    shortlist = db.relationship('Shortlist', back_populates='job', cascade='all, delete-orphan')

    def __init__(self, company_id, title, description) -> None:
        """Initialize a Job object with company_id, title, and description."""
        self.company_id = company_id
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        """Return a string representation of the Job object."""
        return f"<Job {self.title} - Company ID: {self.company_id}>"

    def get_json(self) -> dict:
        """Return a JSON representation of the Job object."""
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

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')

    def __init__(self, student_id, job_id) -> None:
        """Initialize an Application object with student_id and job_id."""
        self.student_id = student_id
        self.job_id = job_id

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
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    job = db.relationship('Job', back_populates='shortlist')
    student = db.relationship('Student')

    def __init__(self, job_id, student_id) -> None:
        """Initialize a Shortlist object with job_id and student_id."""
        self.job_id = job_id
        self.student_id = student_id

    def __repr__(self) -> str:
        return f"<Shortlist Job ID: {self.job_id} Student ID: {self.student_id}>"

    def get_json(self) -> dict:
        return {
            'id': self.id,
            'job_id': self.job_id,
            'student_id': self.student_id
        }
