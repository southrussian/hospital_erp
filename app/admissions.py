from flask import render_template, redirect, url_for, flash, request
from models import *
from datetime import datetime


def view_admissions(app):
    @app.route('/view_admissions')
    def view_admissions():
        admissions = Admission.query.all()
        return render_template('view_admissions.html', admissions=admissions)


def add_admission(app):
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


def edit_admission(app):
    @app.route('/edit_admission/<int:admission_id>', methods=['GET', 'POST'])
    def edit_admission(admission_id):
        admission = Admission.query.get_or_404(admission_id)
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            admission.patient_id = request.form['patient_id']
            admission.admission_date = request.form['admission_date']
            admission.discharge_date = request.form['discharge_date']
            admission.reason_for_admission = request.form['reason_for_admission']
            admission.admitted_by = request.form['admitted_by']

            admission.admission_date = datetime.strptime(admission.admission_date, "%Y-%m-%dT%H:%M")
            if admission.discharge_date:
                admission.discharge_date = datetime.strptime(admission.discharge_date, "%Y-%m-%dT%H:%M")
            else:
                admission.discharge_date = None

            try:
                db.session.commit()
                flash('Поступление успешно обновлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Произошла ошибка при обновлении поступления. Попробуйте снова.', 'danger')

            return redirect(url_for('view_admissions'))

        return render_template('edit_admission.html', patients=patients, doctors=doctors, admission=admission)


def delete_admission(app):
    @app.route('/delete_admission/<int:admission_id>', methods=['POST'])
    def delete_admission(admission_id):
        admission = Admission.query.get_or_404(admission_id)
        try:
            db.session.delete(admission)
            db.session.commit()
            flash("Admission deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_admissions'))
