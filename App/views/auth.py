from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
import csv, os
from App.models.user import Student
from.index import index_views

from App.controllers import (
    login
)

from App.controllers import(
    get_user_by_username,
    create_student
    )
auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


'''
Page/Action Routes
'''

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token)
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(url_for('index_views.index_page'))
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/signup', methods=['GET'])
@jwt_required(optional=True)
def signup_page():

    if current_user:
        return redirect(url_for('index_views.index_page'))

    return render_template('signup.html')


@auth_views.route('/signup', methods=['POST'])
def signup_action():
    data = request.form
    if get_user_by_username(data['username']):
        flash('Username already exists')
        return redirect(url_for('auth_views.signup_action'))
    if get_user_by_username(data['username']):
        flash('Username already exists')
        return redirect(url_for('auth_views.signup_action'))
    if data['password'] != data['confirm_password']:
        flash('Password and Confirm Password do not match')
        return redirect(url_for('auth_views.signup_action'))
    new_student = create_student(
        username=data['username'],
        password=data['password'],
        firstname=data['FirstName'],
        lastname=data['LastName'],
    )

    csv_file_path = os.path.join(os.path.dirname(__file__), '../data/students.csv')
    with open(csv_file_path, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([new_student.id, data['username'], data['password'], data['FirstName'], data['LastName']])

    token = login(data['username'], data['password'])
    response = redirect(url_for('index_views.index_page'))
    set_access_cookies(response, token)
    flash('Signup Successful')
    return response


'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token)
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response
