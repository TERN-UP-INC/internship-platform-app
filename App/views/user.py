from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required,
    role_required
)

from App.models import User

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/apply', methods=['GET'])
@role_required('student')
def get_student_apply_page():
    user = User.query.get(jwt_current_user.id)
    return render_template('student/apply.html')

@user_views.route('/applications', methods=['GET'])
@role_required('student')
def get_student_applications_page():
    user = User.query.get(jwt_current_user.id)
    return render_template('student/applications.html')

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form

    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))
