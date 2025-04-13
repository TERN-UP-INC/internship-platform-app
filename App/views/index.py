from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user, verify_jwt_in_request
from App.models import User


index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()

    if user_id:
        current_user = User.query.get(user_id)
        return render_template(f'{current_user.type}/index.html')

    return render_template('index.html')
