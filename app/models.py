from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="doctor")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))

    user = db.relationship('User', backref=db.backref('doctor', uselist=False))
    department = db.relationship('Department', backref='doctors')


class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))


class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(100))
    passport_series = db.Column(db.String(10))
    passport_number = db.Column(db.String(10))
    oms_number = db.Column(db.String(16), unique=True)


class Admission(db.Model):
    __tablename__ = 'admissions'
    admission_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    discharge_date = db.Column(db.DateTime)
    reason_for_admission = db.Column(db.String(150))
    admitted_by = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))

    patient = db.relationship('Patient', backref='admissions')
    doctor = db.relationship('Doctor', backref='admissions')


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    diagnosis = db.Column(db.String(200))
    treatment = db.Column(db.String(200))
    notes = db.Column(db.Text)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref='medical_records')
    doctor = db.relationship('Doctor', backref='medical_records')


class Operation(db.Model):
    __tablename__ = 'operations'
    operation_id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.admission_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    operation_type = db.Column(db.String(100))
    operation_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer)
    outcome = db.Column(db.String(150))

    admission = db.relationship('Admission', backref='operations')
    doctor = db.relationship('Doctor', backref='operations')


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    prescription_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.record_id'), nullable=False)
    medicine_name = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    instructions = db.Column(db.Text)

    record = db.relationship('MedicalRecord', backref='prescriptions')


class Schedule(db.Model):
    __tablename__ = 'schedules'
    schedule_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    day_of_week = db.Column(db.String(20))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    doctor = db.relationship('Doctor', backref='schedules')


class Room(db.Model):
    __tablename__ = 'rooms'
    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    capacity = db.Column(db.Integer)

    department = db.relationship('Department', backref='rooms')
