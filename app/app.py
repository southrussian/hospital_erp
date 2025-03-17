from flask import Flask, render_template, redirect, url_for, flash, session
import logging
from logging.handlers import RotatingFileHandler
from models import *

from users import setup_register_routes, setup_login_routes, setup_logout_routes, setup_view_users_routes
from patients import (setup_view_patients_routes, setup_add_patient_routes, setup_edit_patient_routes,
                      setup_delete_patient_routes, setup_patient_details_routes)
from doctors import (setup_view_doctors_routes, setup_add_doctor_routes, setup_edit_doctor_routes,
                     setup_delete_doctor_routes)
from departments import (setup_view_departments_routes, setup_add_department_routes, setup_edit_department_routes,
                         setup_delete_department_routes)
from rooms import setup_view_rooms_routes, setup_add_room_routes, setup_edit_room_routes, setup_delete_room_routes
from schedules import (setup_view_schedule_routes, setup_add_schedule_routes, setup_edit_schedule_routes,
                       setup_delete_schedule_routes)
from admissions import (setup_view_admissions_routes, setup_add_admission_routes, setup_edit_admission_routes,
                        setup_delete_admission_routes, setup_analyze_admissions_routes)
from medicines import (setup_view_medicine_routes, setup_add_medicine_routes, setup_edit_medicine_routes,
                       setup_delete_medicine_routes)
from medicine_inventory import (setup_view_medicine_inventory_routes, setup_add_medicine_inventory_routes,
                                setup_edit_medicine_inventory_routes, setup_delete_medicine_inventory_routes)
from beds import setup_view_beds_routes, setup_add_bed_routes, setup_edit_bed_routes, setup_delete_bed_routes
from operations import (setup_view_operations_routes, setup_add_operation_routes, setup_edit_operation_routes,
                        setup_delete_operation_routes)
from prescriptions import (setup_view_prescriptions_routes, setup_add_prescription_routes,
                           setup_edit_prescription_routes, setup_delete_prescription_routes,
                           setup_prescription_analytics_routes)
from medical_records import (setup_view_medical_records_routes, setup_add_medical_record_routes,
                             setup_edit_medical_record_routes, setup_delete_medical_record_routes)
from hospitalization_history import (setup_view_hospitalization_history_routes,
                                     setup_add_hospitalization_history_routes,
                                     setup_edit_hospitalization_history_routes,
                                     setup_delete_hospitalization_history_routes)
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

setup_register_routes(app)
setup_login_routes(app)
setup_logout_routes(app)
setup_view_users_routes(app)

setup_view_patients_routes(app)
setup_add_patient_routes(app)
setup_edit_patient_routes(app)
setup_delete_patient_routes(app)
setup_patient_details_routes(app)

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

setup_view_schedule_routes(app)
setup_add_schedule_routes(app)
setup_edit_schedule_routes(app)
setup_delete_schedule_routes(app)

setup_view_admissions_routes(app)
setup_add_admission_routes(app)
setup_edit_admission_routes(app)
setup_delete_admission_routes(app)
setup_analyze_admissions_routes(app)

setup_view_medicine_routes(app)
setup_add_medicine_routes(app)
setup_edit_medicine_routes(app)
setup_delete_medicine_routes(app)

setup_view_medicine_inventory_routes(app)
setup_add_medicine_inventory_routes(app)
setup_edit_medicine_inventory_routes(app)
setup_delete_medicine_inventory_routes(app)

setup_view_beds_routes(app)
setup_add_bed_routes(app)
setup_edit_bed_routes(app)
setup_delete_bed_routes(app)

setup_view_operations_routes(app)
setup_add_operation_routes(app)
setup_edit_operation_routes(app)
setup_delete_operation_routes(app)

setup_view_prescriptions_routes(app)
setup_add_prescription_routes(app)
setup_edit_prescription_routes(app)
setup_delete_prescription_routes(app)
setup_prescription_analytics_routes(app)

setup_view_medical_records_routes(app)
setup_add_medical_record_routes(app)
setup_edit_medical_record_routes(app)
setup_delete_medical_record_routes(app)

setup_view_hospitalization_history_routes(app)
setup_add_hospitalization_history_routes(app)
setup_edit_hospitalization_history_routes(app)
setup_delete_hospitalization_history_routes(app)


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
