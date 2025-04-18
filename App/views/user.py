from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from werkzeug.datastructures import FileStorage

from.index import index_views

from App.controllers import *

from App.models import User, Company, Job, Student, Staff, Admin, Application, Shortlist

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/apply', methods=['GET'])
@user_views.route('/apply/<int:id>', methods=['GET'])
@roles_required(['student'])
def get_student_apply_page(id: int = None):
    user: User = User.query.get(jwt_current_user.id)

    jobs = Job.query.all()
    job = None

    if id:
        job = Job.query.get(id)
        if not job:
            flash(f"Job with id {id} not found")
            return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    return render_template('student/apply.html', jobs=jobs, selected_job=job)

@user_views.route('/apply/<int:job_id>', methods=['POST'])
@roles_required(['student'])
def post_student_apply_page(job_id: int = None):
    student: Student = get_student(jwt_current_user.id)
    job = Job.query.get(job_id)

    if not job or not student:
        flash("Invalid job or student")
        return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    data = request.form
    file: FileStorage = request.files.get('resume')

    print(file)

    if not file:
        flash("Resume file is required")
        return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    result: bool = create_application(
        student_id=student.id,
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

    if not student.upload_resume(file):
        db.session.rollback()
        flash("Failed to upload resume")
        return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

    flash(f"Application for {job.title} submitted!")
    return redirect(request.referrer or url_for('user_views.get_student_apply_page'))

@user_views.route('/applications', methods=['GET'])
@roles_required(['student'])
def get_student_applications_page():
    student = Student.query.get(jwt_current_user.id)
    applications = [application for application in student.applications]

    return render_template('student/applications.html', applications=applications)

@user_views.route('/applications/delete/<int:application_id>', methods=['POST'])
@roles_required(['student', 'admin'])
def delete_student_application_action(application_id: int):
    application = Application.query.get(application_id)
    if not application:
        flash("Application not found")
        return redirect(request.referrer or url_for('user_views.get_student_applications_page'))

    result: bool = delete_application(application_id)
    if not result:
        flash("Failed to delete application")
    else:
        flash("Application deleted!")

    return redirect(request.referrer or url_for('user_views.get_student_applications_page'))

@user_views.route('/jobs/delete/<int:job_id>', methods=['POST'])
@roles_required(['admin'])
def delete_job_action(job_id: int):
    job = Job.query.get(job_id)
    if not job:
        flash("Job not found")
        return redirect(request.referrer or url_for('user_views.get_job_page'))

    result: bool = delete_job(job_id)

    if not result:
        flash("Failed to delete job")
    else:
        flash("Job deleted!")

    return redirect(request.referrer or url_for('user_views.get_job_page'))


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


@user_views.route('/new-job', methods=['GET'])
@roles_required(['admin'])
def get_shortlists_page():
    user = User.query.get(jwt_current_user.id)
    return render_template('admin/new-job.html')

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form

    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/jobs', methods=['POST'])
@roles_required(['admin'])
def create_job_action():
    data = request.form

    user = get_admin(jwt_current_user.id)

    result: bool = create_job(
        company_id=user.company_id,
        title=data.get('title'),
        description=data.get('description')
    )

    if not result:
        flash("Failed to create job")
        return redirect(request.referrer or url_for('user_views.get_job_page'))

    flash(f"Job {data['title']} created!")
    return redirect(request.referrer or url_for('user_views.get_job_page'))

@user_views.route('/shortlists/<int:application_id>', methods=['POST'])
@roles_required(["admin", "staff"])
def create_shortlist_action(application_id: int):
    data = request.form
    job_id, method = data.get('job_id'), data.get('method')
    application = Application.query.get(application_id)

    if not job_id or not application:
        flash("Invalid application")
        return redirect(request.referrer or url_for('user_views.get_shortlists_page'))

    if method == 'POST':
        result: bool = create_shortlist(
            job_id=job_id,
            application_id=application_id
        )

        if not result:
            flash("Failed to create shortlist")
        else:
            flash("Shortlist created!")
    elif method == 'DELETE':
        shortlist = Shortlist.query.filter_by(application_id=application_id).first()

        if shortlist:
            result: bool = delete_shortlist(shortlist.id)
            if not result:
                flash("Failed to delete shortlist")
            else:
                flash("Shortlist deleted!")
        else:
            flash("Shortlist not found")
    else:
        flash("Invalid method")

    return redirect(request.referrer or url_for('user_views.get_shortlists_page'))
