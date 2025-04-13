from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from App.models import User
from flask import jsonify, render_template

def login(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    print(user.username)
    return create_access_token(identity=str(user.id))
  return None


def setup_jwt(app):
  jwt = JWTManager(app)

  # # configure's flask jwt to resolve get_current_identity() to the corresponding user's ID
  # @jwt.user_identity_loader
  # def user_identity_lookup(identity):
  #   user = User.query.filter_by(username=identity).one_or_none()
  #   if user:
  #       return user.id
  #   return None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = get_jwt_identity()
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)

def roles_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({"msg": "User not found"}), 404
            if user.type not in required_roles:
                return render_template("401.html"), 401
            return fn(*args, **kwargs)
        return wrapper
    return decorator
