from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    get_user,
    get_all_jobs,
    get_job_by_id,
    jwt_required,
    roles_required,
    create_application
)

from App.models import User, Company, Job, Student, Staff, Admin

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/apply', methods=['GET'])
@user_views.route('/apply/<int:id>', methods=['GET'])
@roles_required(['student'])
def get_student_apply_page(id: int = None):
    user: User = User.query.get(jwt_current_user.id)

    jobs = Job.query.all()
    job = None

    if id:
        print(f"ID: {id}")
        job = Job.query.get(id)
        if not job:
            flash(f"Job with id {id} not found")
            return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    return render_template('student/apply.html', jobs=jobs, selected_job=job)

@user_views.route('/apply/<int:id>', methods=['POST'])
@roles_required(['student'])
def post_student_apply_page(id: int = None):
    user: User = User.query.get(jwt_current_user.id)
    job = Job.query.get(id)

    if not job or not user:
        flash("Invalid job or user")
        return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    data = request.form

    result: bool = create_application(
        student_id=user.id,
        job_id=job.id,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        cover_letter=data.get('cover_letter')
    )

    if not result:
        flash("Failed to create application")
        return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    flash(f"Application for {job.title} submitted!")
    return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

@user_views.route('/applications', methods=['GET'])
@roles_required(['student'])
def get_student_applications_page():
    student = Student.query.get(jwt_current_user.id)
    applications = [application for application in student.applications]

    print(f"Applications: {applications}")

    return render_template('student/applications.html', applications=applications)

@user_views.route('/jobs', methods=['GET'])
@user_views.route('/jobs/<int:id>', methods=['GET'])
@roles_required(['admin', 'staff'])
def get_job_page(id: int = None):
    user = get_user(jwt_current_user.id)

    if user.type == 'admin':
        user = Admin.query.get(user.id)
    elif user.type == 'staff':
        user = Staff.query.get(user.id)

    jobs = get_all_jobs(user.company_id)
    jobs = [job for job in jobs]

    if id:
        selected_job = get_job_by_id(id)
        return render_template(f'{user.type}/jobs.html', jobs=jobs, selected_job=selected_job)

    return render_template(f'{user.type}/jobs.html', jobs=jobs)

@user_views.route('/shortlists', methods=['GET'])
@roles_required(['admin'])
def get_shortlists_page():
    user = User.query.get(jwt_current_user.id)
    return render_template('admin/shortlists.html')

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form

    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))
