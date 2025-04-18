import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize, get_all_applications, get_all_companies, get_all_jobs, get_all_students, get_all_shortlists )


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the command
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands')

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

@app.cli.command("get-companies", help="Get all companies")
def get_companies_command():
    companies = get_all_companies()
    if not companies:
        print("No companies found")
    else:
        print(companies)

@app.cli.command("get-jobs", help="Get all jobs")
def get_jobs_command():
    jobs = get_all_jobs()
    if not jobs:
        print("No jobs found")
    else:
        print(jobs)

@app.cli.command("get-students", help="Get all students")
def get_students_command():
    students = get_all_students()
    if not students:
        print("No students found")
    else:
        print(students)

@app.cli.command("get-applications", help="Get all applications")
def get_applications_command():
    applications = get_all_applications()
    if not applications:
        print("No applications found")
    else:
        print(applications)

@app.cli.command("get-shortlists", help="Get all shortlists")
def get_shortlists_command():
    shortlists = get_all_shortlists()
    if not shortlists:
        print("No shortlists found")
    else:
        print(shortlists)


'''
Test Commands
'''

test = AppGroup('test', help='Testing commands')

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)
