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

        # Проверка на существующего пользователя
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Пользователь с таким именем или email уже существует.', 'danger')
            return redirect(url_for('register'))

        # Создание нового пользователя
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

        # Проверка пользователя
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


@app.route('/dashboard')
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
    # Получаем список всех врачей
    schedules = Schedule.query.all()
    return render_template('view_schedule.html', schedules=schedules)


@app.route('/add_department', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        phone_number = request.form['phone_number']

        new_department = Department(name=name, location=location, phone_number=phone_number)

        try:
            db.session.add(new_department)
            db.session.commit()
            flash("Department added successfully!", "success")
            return redirect(url_for('add_department'))  # Redirect to the same form or another page
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

        # Create a new Room instance
        new_room = Room(room_number=room_number, department_id=department_id, capacity=capacity)

        try:
            # Add to the database session and commit
            db.session.add(new_room)
            db.session.commit()
            flash("Room added successfully!", "success")
            return redirect(url_for('add_room'))
        except Exception as e:
            # Rollback and show error if any
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    # Render the form with departments for GET requests
    return render_template('add_room.html', departments=departments)


@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    users = User.query.filter_by(role='doctor').all()  # Fetch all users with role 'doctor'
    departments = Department.query.all()  # Fetch all departments for the dropdown

    if request.method == 'POST':
        # Collect data from the form
        user_id = request.form['user_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        specialization = request.form['specialization']
        phone_number = request.form['phone_number']
        department_id = request.form['department_id']

        # Create a new Doctor instance
        new_doctor = Doctor(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            specialization=specialization,
            phone_number=phone_number,
            department_id=department_id
        )

        try:
            # Add to the database session and commit
            db.session.add(new_doctor)
            db.session.commit()
            flash("Doctor added successfully!", "success")
            return redirect(url_for('add_doctor'))
        except Exception as e:
            # Rollback and show error if any
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    # Render the form with users and departments for GET requests
    return render_template('add_doctor.html', users=users, departments=departments)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        # Collect data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Convert birth_date to a date object
        birth_date_str = request.form['birth_date']
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        gender = request.form['gender']
        address = request.form['address']
        phone_number = request.form['phone_number']
        emergency_contact = request.form['emergency_contact']
        passport_series = request.form['passport_series']
        passport_number = request.form['passport_number']
        oms_number = request.form['oms_number']

        # Create a new Patient instance
        new_patient = Patient(
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            phone_number=phone_number,
            emergency_contact=emergency_contact,
            passport_series=passport_series,
            passport_number=passport_number,
            oms_number=oms_number
        )

        try:
            db.session.add(new_patient)
            db.session.commit()
            flash("Patient added successfully!", "success")
            return redirect(url_for('view_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")

    return render_template('add_patient.html')


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

        new_admission = Admission(
            patient_id=patient_id,
            admission_date=admission_date,
            discharge_date=discharge_date,
            reason_for_admission=reason_for_admission,
            admitted_by=admitted_by
        )

        try:
            db.session.add(new_admission)
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

        # Создаем новый объект Schedule
        new_schedule = Schedule(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )

        try:
            # Добавляем в сессию
            db.session.add(new_schedule)
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
        record_id = request.form['record_id']
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        diagnosis = request.form['diagnosis']
        treatment = request.form['treatment']
        notes = request.form['notes']
        record_date = request.form['record_date']
        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

        medical_record = MedicalRecord(
            record_id=record_id,
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


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
