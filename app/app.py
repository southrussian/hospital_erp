from flask import Flask, render_template, redirect, url_for, flash, session
import logging
from logging.handlers import RotatingFileHandler
from models import *

from users import register, login, logout, view_users
from patients import (setup_view_patients_routes, setup_add_patient_routes, setup_edit_patient_routes,
                      setup_delete_patient_routes)
from doctors import (setup_view_doctors_routes, setup_add_doctor_routes, setup_edit_doctor_routes,
                     setup_delete_doctor_routes)
from departments import (setup_view_departments_routes, setup_add_department_routes, setup_edit_department_routes,
                         setup_delete_department_routes)
from rooms import setup_view_rooms_routes, setup_add_room_routes, setup_edit_room_routes, setup_delete_room_routes
from schedules import view_schedule, add_schedule, edit_schedule, delete_schedule
from admissions import (setup_view_admissions_routes, setup_add_admission_routes, setup_edit_admission_routes,
                        setup_delete_admission_routes, setup_analyze_admissions_routes)
from medicines import view_medicine, add_medicine, edit_medicine, delete_medicine
from medicine_invetory import (view_medicine_inventory, add_medicine_inventory, edit_medicine_inventory,
                               delete_medicine_inventory)
from beds import setup_view_beds_routes, setup_add_bed_routes, setup_edit_bed_routes, setup_delete_bed_routes
from operations import view_operations, add_operation, edit_operation, delete_operation
from prescriptions import view_prescriptions, add_prescription, edit_prescription, delete_prescription
from medical_records import view_medical_records, add_medical_record, edit_medical_record, delete_medical_record
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5896@localhost:5432/hospital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'oxxxymiron'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
file_handler = RotatingFileHandler('hospital_app.log', maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

app.logger.info("Приложение Flask запущено.")

db.init_app(app)
migrate = Migrate(app, db)

register(app)
login(app)
logout(app)
view_users(app)

setup_view_patients_routes(app)
setup_add_patient_routes(app)
setup_edit_patient_routes(app)
setup_delete_patient_routes(app)

setup_view_doctors_routes(app)
setup_add_doctor_routes(app)
setup_edit_doctor_routes(app)
setup_delete_doctor_routes(app)

setup_view_departments_routes(app)
setup_add_department_routes(app)
setup_edit_department_routes(app)
setup_delete_department_routes(app)

setup_view_rooms_routes(app)
setup_add_room_routes(app)
setup_edit_room_routes(app)
setup_delete_room_routes(app)

view_schedule(app)
add_schedule(app)
edit_schedule(app)
delete_schedule(app)

setup_view_admissions_routes(app)
setup_add_admission_routes(app)
setup_edit_admission_routes(app)
setup_delete_admission_routes(app)
setup_analyze_admissions_routes(app)

view_medicine(app)
add_medicine(app)
edit_medicine(app)
delete_medicine(app)

view_medicine_inventory(app)
add_medicine_inventory(app)
edit_medicine_inventory(app)
delete_medicine_inventory(app)

setup_view_beds_routes(app)
setup_add_bed_routes(app)
setup_edit_bed_routes(app)
setup_delete_bed_routes(app)

view_operations(app)
add_operation(app)
edit_operation(app)
delete_operation(app)

view_prescriptions(app)
add_prescription(app)
edit_prescription(app)
delete_prescription(app)

view_medical_records(app)
add_medical_record(app)
edit_medical_record(app)
delete_medical_record(app)


@app.route('/')
def dashboard():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице.', 'warning')
        return redirect(url_for('login'))
    app.logger.info(f"Доступ к панели управления пользователем ID: {session['user_id']}.")
    return render_template('dashboard.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
