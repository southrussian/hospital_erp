from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index, CheckConstraint, UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="doctor")
    created_at = db.Column(db.DateTime, default=datetime.now())

    doctor = db.relationship('Doctor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    specialization = db.Column(db.String(50))
    phone_number = db.Column(db.String(11))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))

    user = db.relationship('User', back_populates='doctor')

    department = db.relationship(
        'Department',
        foreign_keys=[department_id],  # Явное указание ключа
        backref=db.backref('doctors', lazy=True)
    )


class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(300))
    phone_number = db.Column(db.String(11))
    emergency_contact = db.Column(db.String(100))
    passport_series = db.Column(db.String(4))
    passport_number = db.Column(db.String(6))
    oms_number = db.Column(db.String(16), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())


class Room(db.Model):
    __tablename__ = 'rooms'
    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(20))  # Например: общая, индивидуальная и т.д.

    department = db.relationship('Department', backref='rooms')
    beds = db.relationship('Bed', backref='room', lazy='joined', cascade='all, delete-orphan')

    def available_beds(self):
        return self.capacity - self.occupied_beds_count()

    def occupied_beds_count(self):
        return len([bed for bed in self.beds if bed.patient_id is not None])

    def occupancy_rate(self):
        occupied = self.occupied_beds_count()
        return f"{occupied}/{self.capacity}"


class Bed(db.Model):
    __tablename__ = 'beds'
    bed_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))

    patient = db.relationship('Patient', backref='bed')
    __table_args__ = (
        Index('idx_bed_room_status', 'room_id', 'patient_id'),
        UniqueConstraint('patient_id', name='uq_bed_patient'),
    )


class Admission(db.Model):  # госпитализация
    __tablename__ = 'admissions'
    admission_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    admission_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    discharge_date = db.Column(db.DateTime)
    reason = db.Column(db.String(200), nullable=False)
    admitted_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    diagnosis = db.Column(db.String(200))

    patient = db.relationship('Patient', backref='admissions')
    user = db.relationship('User')


class HospitalizationHistory(db.Model):
    __tablename__ = 'hospitalization_history'
    history_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey('beds.bed_id'), nullable=False)
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.admission_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)

    patient = db.relationship('Patient', backref='hospitalizations')
    bed = db.relationship('Bed')
    admission = db.relationship('Admission')


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.admission_id'))
    record_type = db.Column(db.String(20), nullable=False)  # diagnosis, note, procedure
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    patient = db.relationship('Patient', backref='medical_records')
    doctor = db.relationship('Doctor', backref='medical_records')
    admission = db.relationship('Admission')


class Medicine(db.Model):
    __tablename__ = 'medicines'
    medicine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    dosage_form = db.Column(db.String(50))
    atc_code = db.Column(db.String(10))  # Код ATC классификации


class MedicineInventory(db.Model):
    __tablename__ = 'medicine_inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.Date)
    last_updated = db.Column(db.DateTime, default=datetime.now())

    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_quantity_positive'),
    )

    medicine = db.relationship('Medicine')


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.medicine_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, default=datetime.now())
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    instructions = db.Column(db.Text)

    patient = db.relationship('Patient', backref='prescriptions')
    medicine = db.relationship('Medicine')
    doctor = db.relationship('Doctor')


class Schedule(db.Model):
    __tablename__ = 'schedules'
    schedule_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    day_of_week = db.Column(db.Integer)  # 1-7 (понедельник-воскресенье)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    doctor = db.relationship('Doctor', backref='schedules')


class Operation(db.Model):
    __tablename__ = 'operations'
    operation_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    operation_date = db.Column(db.DateTime, default=datetime.now())
    type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer)  # В минутах
    outcome = db.Column(db.String(150))
    notes = db.Column(db.Text)

    patient = db.relationship('Patient', backref='operations')
    doctor = db.relationship('Doctor', backref='operations')


# Дополнительные индексы для часто используемых запросов
Index('idx_patient_oms', Patient.oms_number)
Index('idx_admission_active', Admission.is_active)
Index('idx_inventory_expiration', MedicineInventory.expiration_date)
