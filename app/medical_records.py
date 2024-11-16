from flask import render_template, redirect, url_for, flash, request
from models import *


def view_medical_records(app):
    @app.route('/view_medical_records')
    def view_medical_records():
        records = Operation.query.all()
        return render_template('view_medical_records.html', records=records)


def add_medical_record(app):
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


def edit_medical_record(app):
    @app.route('/edit_medical_record/<int:record_id>', methods=['GET', 'POST'])
    def edit_medical_record(record_id):
        doctors = Doctor.query.all()
        patients = Doctor.query.all()
        record = MedicalRecord.query.get_or_404(record_id)

        if request.method == 'POST':
            record.patient_id = request.form['patient_id']
            record.doctor_id = request.form['doctor_id']
            record.diagnosis = request.form['diagnosis']
            record.treatment = request.form['treatment']
            record.notes = request.form['notes']
            record_date = request.form['record_date']
            record.record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

            try:
                db.session.commit()
                flash('Запись успешно обновлена!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обновлении записи: {str(e)}', 'danger')
            return redirect(url_for('view_medical_records'))

        return render_template('edit_medical_record.html', doctors=doctors, patients=patients,
                               record=record)


def delete_medical_record(app):
    @app.route('/delete_medical_record/<int:record_id>', methods=['POST'])
    def delete_medical_record(record_id):
        record = MedicalRecord.query.get_or_404(record_id)
        try:
            db.session.delete(record)
            db.session.commit()
            flash("Record deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_medical_records'))


