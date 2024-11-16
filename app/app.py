from models import *
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'oxxxymiron'

db.init_app(app)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Пользователь с таким именем или email уже существует.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))


@app.route('/')
def dashboard():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите для доступа к этой странице.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/view_users')
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)


@app.route('/view_doctors')
def view_doctors():
    doctors = Doctor.query.all()
    return render_template('view_doctors.html', doctors=doctors)


@app.route('/view_departments')
def view_departments():
    departments = Department.query.all()
    return render_template('view_departments.html', departments=departments)


@app.route('/view_patients')
def view_patients():
    patients = Patient.query.all()
    return render_template('view_patients.html', patients=patients)


@app.route('/view_rooms')
def view_rooms():
    rooms = Room.query.all()
    return render_template('view_rooms.html', rooms=rooms)


@app.route('/view_schedule')
def view_schedule():
    schedules = Schedule.query.all()
    return render_template('view_schedule.html', schedules=schedules)


@app.route('/view_admissions')
def view_admissions():
    admissions = Admission.query.all()
    return render_template('view_admissions.html', admissions=admissions)


@app.route('/view_medicine')
def view_medicine():
    medicines = Medicine.query.all()
    return render_template('view_medicines.html', medicines=medicines)


@app.route('/view_medicine_inventory')
def view_medicine_inventory():
    inventory = MedicineInventory.query.all()
    return render_template('view_medicine_inventory.html', inventory=inventory)


@app.route('/view_beds')
def view_beds():
    beds = Bed.query.all()
    return render_template('view_beds.html', beds=beds)


@app.route('/view_operations')
def view_operations():
    operations = Operation.query.all()
    return render_template('view_operations.html', operations=operations)


@app.route('/view_prescriptions')
def view_prescriptions():
    prescriptions = Prescription.query.all()
    return render_template('view_prescriptions.html', prescriptions=prescriptions)


@app.route('/view_medical_records')
def view_medical_records():
    records = Operation.query.all()
    return render_template('view_medical_records.html', records=records)


@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        phone_number = request.form['phone_number']

        department = Department(name=name, location=location, phone_number=phone_number)

        try:
            db.session.add(department)
            db.session.commit()
            flash("Department added successfully!", "success")
            return redirect(url_for('add_department'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
    return render_template('add_department.html')


@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    departments = Department.query.all()

    if request.method == 'POST':
        room_number = request.form['room_number']
        department_id = request.form['department_id']
        capacity = request.form['capacity']

        room = Room(room_number=room_number, department_id=department_id, capacity=capacity)

        try:
            db.session.add(room)
            db.session.commit()
            flash("Room added successfully!", "success")
            return redirect(url_for('add_room'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('add_room.html', departments=departments)


@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    users = User.query.filter_by(role='doctor').all()
    departments = Department.query.all()

    if request.method == 'POST':
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        specialization = request.form['specialization']
        birth_date_str = request.form['birth_date']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        phone_number = request.form['phone_number']
        department_id = request.form['department_id']

        doctor = Doctor(
            user_id=user_id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            specialization=specialization,
            birth_date=birth_date,
            phone_number=phone_number,
            department_id=department_id
        )

        try:
            db.session.add(doctor)
            db.session.commit()
            flash("Doctor added successfully!", "success")
            return redirect(url_for('add_doctor'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('add_doctor.html', users=users, departments=departments)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    rooms = Room.query.all()
    if request.method == 'POST':

        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']

        birth_date_str = request.form['birth_date']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        gender = request.form['gender']
        address = request.form['address']
        phone_number = request.form['phone_number']
        emergency_contact = request.form['emergency_contact']
        passport_series = request.form['passport_series']
        passport_number = request.form['passport_number']
        oms_number = request.form['oms_number']
        room_id = request.form['room_id']

        patient = Patient(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            phone_number=phone_number,
            emergency_contact=emergency_contact,
            passport_series=passport_series,
            passport_number=passport_number,
            oms_number=oms_number,
            room_id=room_id
        )

        try:
            db.session.add(patient)
            db.session.commit()
            flash("Patient added successfully!", "success")
            return redirect(url_for('view_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('add_patient.html', rooms=rooms)


@app.route('/add_admission', methods=['GET', 'POST'])
def add_admission():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        admission_date = request.form['admission_date']
        discharge_date = request.form['discharge_date']
        reason_for_admission = request.form['reason_for_admission']
        admitted_by = request.form['admitted_by']

        admission_date = datetime.strptime(admission_date, "%Y-%m-%dT%H:%M")
        if discharge_date:
            discharge_date = datetime.strptime(discharge_date, "%Y-%m-%dT%H:%M")
        else:
            discharge_date = None

        admission = Admission(
            patient_id=patient_id,
            admission_date=admission_date,
            discharge_date=discharge_date,
            reason_for_admission=reason_for_admission,
            admitted_by=admitted_by
        )

        try:
            db.session.add(admission)
            db.session.commit()
            flash('Поступление успешно добавлено!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при добавлении поступления. Попробуйте снова.', 'danger')

        return redirect(url_for('add_admission'))

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template('add_admission.html', patients=patients, doctors=doctors)


@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        start_time = datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.strptime(end_time, '%H:%M').time()

        schedule = Schedule(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )

        try:
            db.session.add(schedule)
            db.session.commit()
            flash('Расписание успешно добавлено!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении расписания: {str(e)}', 'danger')

        return redirect(url_for('add_schedule'))

    doctors = Doctor.query.all()
    return render_template('add_schedule.html', doctors=doctors)


@app.route('/add_medical_record', methods=['GET', 'POST'])
def add_medical_record():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        notes = request.form['notes']
        record_date = request.form['record_date']
        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

        medical_record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=doctor_id,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes,
            record_date=record_date
        )

        try:
            db.session.add(medical_record)
            db.session.commit()
            flash('Запись успешно добавлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении записи: {str(e)}', 'danger')
        return redirect(url_for('add_medical_record'))

    doctors = Doctor.query.all()
    patients = Doctor.query.all()

    return render_template('add_medical_record.html', doctors=doctors, patients=patients)


@app.route('/add_bed', methods=['GET', 'POST'])
def add_bed():
    rooms = Room.query.all()
    patients = Patient.query.filter_by(bed=None).all()  # Только пациенты без кроватей

    if request.method == 'POST':
        room_id = request.form['room_id']
        patient_id = request.form.get('patient_id')  # Пациент может быть не назначен
        status = 'occupied' if patient_id else 'free'

        bed = Bed(
            room_id=room_id,
            patient_id=patient_id,
            status=status
        )

        try:
            db.session.add(bed)
            db.session.commit()
            flash('Койка успешно добавлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('add_bed'))

    return render_template('add_bed.html', rooms=rooms, patients=patients)


@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        dosage_form = request.form['dosage_form']

        medicine = Medicine(
            name=name,
            description=description,
            dosage_form=dosage_form
        )

        try:
            db.session.add(medicine)
            db.session.commit()
            flash('Лекарство успешно добавлено!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('add_medicine'))

    return render_template('add_medicine.html')


@app.route('/add_medicine_inventory', methods=['GET', 'POST'])
def add_medicine_inventory():
    medicines = Medicine.query.all()

    if request.method == 'POST':
        medicine_id = request.form['medicine_id']
        quantity = request.form['quantity']
        last_updated = request.form['last_updated']

        inventory = MedicineInventory(
            medicine_id=medicine_id,
            quantity=quantity,
            last_updated=last_updated
        )

        try:
            db.session.add(inventory)
            db.session.commit()
            flash('Инвентарь лекарств успешно добавлен!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('add_medicine_inventory'))

    return render_template('add_medicine_inventory.html', medicines=medicines)


@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    medical_records = MedicalRecord.query.all()
    medicines = Medicine.query.all()

    if request.method == 'POST':
        record_id = request.form['record_id']
        medicine_id = request.form['medicine_id']
        dosage = request.form['dosage']
        duration = request.form['duration']
        instructions = request.form['instructions']

        prescription = Prescription(
            record_id=record_id,
            medicine_id=medicine_id,
            dosage=dosage,
            duration=duration,
            instructions=instructions
        )

        try:
            db.session.add(prescription)
            db.session.commit()
            flash('Рецепт успешно добавлен!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('add_prescription'))

    return render_template('add_prescription.html', medical_records=medical_records, medicines=medicines)


@app.route('/add_operation', methods=['GET', 'POST'])
def add_operation():
    patients = Patient.query.all()
    doctors = Doctor.query.all()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        operation_type = request.form['operation_type']
        operation_date = request.form['operation_date']
        duration = request.form['duration']
        outcome = request.form['outcome']

        operation = Operation(
            patient_id=patient_id,
            doctor_id=doctor_id,
            operation_type=operation_type,
            operation_date=operation_date,
            duration=duration,
            outcome=outcome
        )

        try:
            db.session.add(operation)
            db.session.commit()
            flash('Операция успешно добавлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('add_operation'))

    return render_template('add_operation.html', patients=patients, doctors=doctors)


@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    rooms = Room.query.all()

    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.middle_name = request.form['middle_name']
        patient.last_name = request.form['last_name']
        patient.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        patient.gender = request.form['gender']
        patient.address = request.form['address']
        patient.phone_number = request.form['phone_number']
        patient.emergency_contact = request.form['emergency_contact']
        patient.passport_series = request.form['passport_series']
        patient.passport_number = request.form['passport_number']
        patient.oms_number = request.form['oms_number']
        patient.room_id = request.form['room_id']

        try:
            db.session.commit()
            flash("Patient updated successfully!", "success")
            return redirect(url_for('view_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('edit_patient.html', patient=patient, rooms=rooms)


@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    users = User.query.filter_by(role='doctor').all()
    departments = Department.query.all()

    if request.method == 'POST':
        doctor.user_id = request.form['user_id']
        doctor.first_name = request.form['first_name']
        doctor.middle_name = request.form['middle_name']
        doctor.last_name = request.form['last_name']
        doctor.specialization = request.form['specialization']
        doctor.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        doctor.phone_number = request.form['phone_number']
        doctor.department_id = request.form['department_id']

        try:
            db.session.commit()
            flash("Doctor updated successfully!", "success")
            return redirect(url_for('view_doctors'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('edit_doctor.html', doctor=doctor, users=users, departments=departments)


@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        flash("Doctor deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('view_doctors'))


@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash("Patient deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for('view_patients'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
