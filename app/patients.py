# routes/patients.py
from flask import render_template, redirect, url_for, flash, request
from models import Patient, Room, db
from datetime import datetime


def view_patients(app):
    @app.route('/view_patients')
    def view_patients():
        sort_order = request.args.get('sort', 'asc')  # по умолчанию в порядке убывания
        if sort_order == 'asc':
            patients = Patient.query.order_by(Patient.last_name.asc()).all()
        else:
            patients = Patient.query.order_by(Patient.last_name.desc()).all()
        return render_template('view_patients.html', patients=patients, sort_order=sort_order)


def add_patient(app):
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


def edit_patient(app):
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


def delete_patient(app):
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
