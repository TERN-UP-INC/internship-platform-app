import os
from sqlalchemy import event
from App import app
from App.models import Application
from App.controllers import get_student

@event.listens_for(Application, 'after_delete')
def delete_resume_file(mapper, connection, target):
    student = get_student(target.student_id)
    if student.resume:
        filepath = os.path.join(app.config.get('UPLOAD_FOLDER'), student.resume)

    try:
        os.remove(filepath)
    except FileNotFoundError:
        print(f"File {filepath} not found.")
