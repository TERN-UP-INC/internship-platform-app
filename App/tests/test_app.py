import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Admin, Staff, Company, Job, Application, Shortlist
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass", "Bob", "Smith")
        assert user.username == "bob"
        assert user.firstname == "Bob"
        assert user.lastname == "Smith"


    # pure function no side effects or integrations called
    def test_get_json(self):
        user = User("bob", "bobpass", "Bob", "Smith")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id":None, "username":"bob", "firstname":"Bob", "lastname":"Smith"})

    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password, "Bob", "Smith")
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password, "Bob", "Smith")
        assert user.check_password(password)

class StudentUnitTests(unittest.TestCase):

    def test_student_creation(self):
        student = Student("bob", "bobpass", "John", "Doe")
        assert student.username == "bob"
        assert student.firstname == "John"
        assert student.lastname == "Doe"

    def test_create_application(self):
        student = Student(username="bob1", password="bobpass", firstname="John", lastname="Doe")
        db.session.add(student)
        db.session.commit()

        company = Company(name="Tech Corp")
        db.session.add(company)
        db.session.commit()

        job = Job(company_id=1, title="Software Engineer", description="Develop software.")
        db.session.add(job)
        db.session.commit()

        result = student.create_application(job.id)
        assert result

    def test_delete_application(self):
        student = Student("bob2", "bobpass", "John", "Doe")
        db.session.add(student)
        db.session.commit()

        company = Company(name="Tech Corp")
        db.session.add(company)
        db.session.commit()

        job = Job(company_id=1, title="Software Engineer", description="Develop software.")
        db.session.add(job)
        db.session.commit()

        student.create_application(job.id)
        application = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
        assert application is not None

        result = student.delete_application(job.id)
        assert result


class AdminUnitTests(unittest.TestCase):
    company: Company = None

    def setUp(self):
        self.company = Company(name="Tech Corp")
        db.session.add(self.company)
        db.session.commit()

        self.company = Company.query.get(1)
        assert self.company.id == 1
        assert self.company.name == "Tech Corp"

    def test_admin_creation(self):
        admin = Admin(company_id=1, username="admin1", password="bobpass", firstname="Admin", lastname="User")
        assert admin.username == "admin1"
        assert admin.firstname == "Admin"
        assert admin.lastname == "User"
        assert admin.company_id == 1

    def test_repr(self):
        admin = Admin(company_id=1, username="admin2", password="bobpass", firstname="Admin", lastname="User")
        assert admin.__repr__() == "<Admin admin2 Company: None>"

    def test_get_json(self):
        admin = Admin(company_id=1, username="admin3", password="bobpass", firstname="Admin", lastname="User")
        admin_json = admin.get_json()
        self.assertDictEqual(admin_json, {
            "id": None,
            "username": "admin3",
            "firstname": "Admin",
            "lastname": "User",
            "company_id": 1
        })


class StaffUnitTests(unittest.TestCase):
    company: Company = None
    staff: Staff = None
    job: Job = None

    def setUp(self):
        self.company = Company(name="Rain Corp")
        db.session.add(self.company)
        db.session.commit()

        existing_staff = Staff.query.filter_by(username="staff3").first()
        if not existing_staff:
            self.staff = Staff(company_id=self.company.id, username="staff3", password="bobpass", firstname="Staff", lastname="User")
            db.session.add(self.staff)
            db.session.commit()
        else:
            self.staff = existing_staff

        self.company = Company.query.filter_by(name="Rain Corp").first()
        self.staff = Staff.query.filter_by(username="staff3").first()

        job = Job(company_id=self.company.id, title="Software Engineer", description="Develop software.")
        db.session.add(job)
        db.session.commit()

        self.job = Job.query.get(1)
        assert self.job.id == 1

        assert self.staff.company_id == self.company.id
        assert self.company.id == 6
        assert self.company.name == "Rain Corp"
        assert self.staff.__repr__() == "<Staff staff3 Company: Rain Corp>"


    def test_staff_creation(self):
        staff = Staff(company_id=self.company.id, username="staff2", password="bobpass", firstname="Staff", lastname="User")

        db.session.add(staff)
        db.session.commit()

        assert staff.company_id == self.company.id
        assert staff.username == "staff2"
        assert staff.firstname == "Staff"
        assert staff.lastname == "User"
        assert staff.__repr__() == "<Staff staff2 Company: Rain Corp>"

    def test_add_to_shortlist(self):
        self.job = Job.query.get(1)
        assert self.job.id == 1

        student = Student("jd", "bobpass", "John", "Doe")
        db.session.add(student)
        db.session.commit()
        student = Student.query.filter_by(username="jd").first()
        assert student.username == "jd"

        result = self.staff.add_to_shortlist(self.job.id, student.id)
        assert result

    def test_remove_from_shortlist(self):
        student = Student("john_doe", "bobpass", "John", "Doe")
        db.session.add(student)
        db.session.commit()

        self.staff.add_to_shortlist(self.job.id, student.id)
        shortlist = Shortlist.query.filter_by(job_id=self.job.id, student_id=student.id).first()
        assert shortlist is not None
        assert shortlist.job_id == self.job.id
        assert shortlist.__repr__() == f"<Shortlist Job ID: {self.job.id} Student ID: {student.id}>"

        result = self.staff.remove_from_shortlist(self.job.id, student.id)
        assert result

    def test_get_json(self):
        staff_json = self.staff.get_json()
        self.assertDictEqual(staff_json, {
            "id": self.staff.id,
            "username": "staff3",
            "firstname": "Staff",
            "lastname": "User",
            "company_id": 6
        })


class CompanyUnitTests(unittest.TestCase):

    def test_company_creation(self):
        company = Company(name="Tech Corp")
        assert company.name == "Tech Corp"

    def test_get_json(self):
        company = Company(name="Tech Corp")

        company_json = company.get_json()
        self.assertDictEqual(company_json, {"id": None, "name": "Tech Corp"})


class JobUnitTests(unittest.TestCase):
    company: Company = None

    def setUp(self):
        self.company = Company(name="Tech Corp")
        db.session.add(self.company)
        db.session.commit()

        self.company = Company.query.get(1)
        assert self.company.id == 1
        assert self.company.name == "Tech Corp"

    def test_job_creation(self):
        job = Job(company_id=self.company.id, title="Software Engineer", description="Develop software.")
        assert job.title == "Software Engineer"
        assert job.description == "Develop software."
        assert job.company_id == self.company.id

    def test_get_json(self):
        company = Company(name="Tech Corp")
        db.session.add(company)
        db.session.commit()

        job = Job(company_id=company.id, title="Software Engineer", description="Develop software.")
        job_json = job.get_json()
        self.assertDictEqual(job_json, {
            "id": None,
            "company_id": company.id,
            "title": "Software Engineer",
            "description": "Develop software."
        })


class ApplicationUnitTests(unittest.TestCase):
    company: Company = None
    student: Student = None
    job: Job = None


    def setUp(self):
        self.company = Company(name="Tech Corp")
        db.session.add(self.company)
        db.session.commit()

        self.company = Company.query.get(1)
        assert self.company.id == 1
        assert self.company.name == "Tech Corp"

        existing_student = Student.query.filter_by(username="bob1").first()
        if not existing_student:
            self.student = Student("bob1", "bob1pass", "John", "Doe")
            db.session.add(self.student)
            db.session.commit()
        else:
            self.student = existing_student

        self.job = Job(company_id=self.company.id, title="Software Engineer", description="Develop software.")
        db.session.add(self.job)
        db.session.commit()

        self.job = Job.query.get(1)
        assert self.job.title == "Software Engineer"

    def test_application_creation(self):
        application = Application(student_id=self.student.id, job_id=self.job.id)
        assert application.student_id == self.student.id
        assert application.job_id == self.job.id

    def test_repr(self):
        application = Application(student_id=self.student.id, job_id=self.job.id)
        assert application.__repr__() == f"<Application Student ID: {self.student.id} Job ID: {self.job.id}>"

    def test_get_json(self):
        application = Application(student_id=self.student.id, job_id=self.job.id)
        application_json = application.get_json()
        self.assertDictEqual(application_json, {"id": None, "student_id": self.student.id, "job_id": self.job.id})


class ShortlistUnitTests(unittest.TestCase):

    job: Job = None
    student: Student = None

    def setUp(self):
        self.job = Job(company_id=1, title="Software Engineer", description="Develop software.")
        db.session.add(self.job)
        db.session.commit()

        existing_student = Student.query.filter_by(username="john_doe").first()
        if not existing_student:
            self.student = Student("john_doe", "bobpass", "John", "Doe")
            db.session.add(self.student)
            db.session.commit()
        else:
            self.student = existing_student

    def test_shortlist_creation(self):
        shortlist = Shortlist(job_id=self.job.id, student_id=self.student.id)
        assert shortlist.job_id == self.job.id
        assert shortlist.student_id == self.student.id

    def test_get_json(self):
        shortlist = Shortlist(job_id=self.job.id, student_id=self.student.id)
        shortlist_json = shortlist.get_json()
        self.assertDictEqual(shortlist_json, {"id": None, "job_id": self.job.id, "student_id": self.student.id})

'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and reused for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

def test_authenticate():
    user = create_user("bob", "bobpass", "Bob", "Smith")
    assert login("bob", "bobpass") != None
