from flask import Flask, render_template, redirect, url_for, flash, session
import logging
from logging.handlers import RotatingFileHandler
from models import *

from users import register, login, logout, view_users
from patients import view_patients, add_patient, edit_patient, delete_patient
from doctors import view_doctors, add_doctor, edit_doctor, delete_doctor
from departments import view_departments, add_department, edit_department, delete_department
from rooms import view_rooms, add_room, edit_room, delete_room
from schedules import view_schedule, add_schedule, edit_schedule, delete_schedule
from admissions import view_admissions, add_admission, edit_admission, delete_admission, analyze_admissions
from medicines import view_medicine, add_medicine, edit_medicine, delete_medicine
from medicine_invetory import (view_medicine_inventory, add_medicine_inventory, edit_medicine_inventory,
                               delete_medicine_inventory)
from beds import view_beds, add_bed, edit_bed, delete_bed
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

view_patients(app)
add_patient(app)
edit_patient(app)
delete_patient(app)

view_doctors(app)
add_doctor(app)
edit_doctor(app)
delete_doctor(app)

view_departments(app)
add_department(app)
edit_department(app)
delete_department(app)

view_rooms(app)
add_room(app)
edit_room(app)
delete_room(app)

view_schedule(app)
add_schedule(app)
edit_schedule(app)
delete_schedule(app)

view_admissions(app)
add_admission(app)
edit_admission(app)
delete_admission(app)
analyze_admissions(app)

view_medicine(app)
add_medicine(app)
edit_medicine(app)
delete_medicine(app)

view_medicine_inventory(app)
add_medicine_inventory(app)
edit_medicine_inventory(app)
delete_medicine_inventory(app)

view_beds(app)
add_bed(app)
edit_bed(app)
delete_bed(app)

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
