from admissions import setup_admissions_routes
from beds import setup_beds_routes
from departments import setup_departments_routes
from doctors import setup_doctors_routes
from medical_records import setup_medical_records_routes
from medicine_inventory import setup_medicine_inventory_routes
from medicines import setup_medicine_routes
from operations import setup_operations_routes
from patients import setup_patients_routes
from prescriptions import setup_prescriptions_routes
from schedules import setup_schedules_routes
from users import setup_users_routes


def setup_routes(app):
    setup_admissions_routes(app)
    setup_beds_routes(app)
    setup_departments_routes(app)
    setup_doctors_routes(app)
    setup_medical_records_routes(app)
    setup_medicine_inventory_routes(app)
    setup_medicine_routes(app)
    setup_operations_routes(app)
    setup_patients_routes(app)
    setup_prescriptions_routes(app)
    setup_schedules_routes(app)
    setup_users_routes(app)
