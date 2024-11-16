from flask import render_template, redirect, url_for, flash, request
from models import *


def view_prescriptions(app):
    @app.route('/view_prescriptions')
    def view_prescriptions():
        prescriptions = Prescription.query.all()
        return render_template('view_prescriptions.html', prescriptions=prescriptions)


def add_prescription(app):
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

        return render_template('add_prescription.html',
                               medical_records=medical_records, medicines=medicines)


def edit_prescription(app):
    @app.route('/edit_prescription/<int:prescription_id>', methods=['GET', 'POST'])
    def edit_prescription(prescription_id):
        prescription = Prescription.query.get_or_404(prescription_id)
        medical_records = MedicalRecord.query.all()
        medicines = Medicine.query.all()

        if request.method == 'POST':
            prescription.record_id = request.form['record_id']
            prescription.medicine_id = request.form['medicine_id']
            prescription.dosage = request.form['dosage']
            prescription.duration = request.form['duration']
            prescription.instructions = request.form['instructions']

            try:
                db.session.commit()
                flash('Рецепт успешно обновлен!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('view_prescriptions'))

        return render_template('edit_prescription.html', medical_records=medical_records,
                               medicines=medicines, prescription=prescription)


def delete_prescription(app):
    @app.route('/delete_prescription/<int:prescription_id>', methods=['POST'])
    def delete_prescription(prescription_id):
        prescription = Prescription.query.get_or_404(prescription_id)
        try:
            db.session.delete(prescription)
            db.session.commit()
            flash("Doctor deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_prescriptions'))
