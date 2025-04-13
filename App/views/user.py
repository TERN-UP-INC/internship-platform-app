from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    roles_required
)

from App.models import User, Company, Job

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

@user_views.route('/applications', methods=['GET'])
@roles_required(['student'])
def get_student_applications_page():
    user = User.query.get(jwt_current_user.id)
    return render_template('student/applications.html')

@user_views.route('/jobs', methods=['GET'])
@roles_required(['admin', 'staff'])
def get_job_page():
    user = User.query.get(jwt_current_user.id)
    return render_template(f'{user.type}/jobs.html')

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
