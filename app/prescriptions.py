from flask import render_template, redirect, url_for, flash, request
from .models import Prescription, MedicineInventory, MedicalRecord, Medicine, db
from datetime import datetime


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
                # Найти запись в инвентаре и уменьшить количество
                inventory = MedicineInventory.query.filter_by(medicine_id=medicine_id).first()
                if inventory and inventory.quantity >= int(dosage):
                    inventory.quantity -= int(dosage)
                    inventory.last_updated = datetime.utcnow()
                    db.session.add(prescription)
                    db.session.commit()
                    flash('Рецепт успешно добавлен!', 'success')
                else:
                    flash('Недостаточно лекарств на складе!', 'danger')
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
            record_id = request.form['record_id']
            medicine_id = request.form['medicine_id']
            dosage = request.form['dosage']
            duration = request.form['duration']
            instructions = request.form['instructions']

            try:
                # Найти запись в инвентаре и уменьшить количество
                inventory = MedicineInventory.query.filter_by(medicine_id=medicine_id).first()
                if inventory and inventory.quantity >= int(dosage):
                    inventory.quantity -= int(dosage)
                    inventory.last_updated = datetime.utcnow()
                    prescription.record_id = record_id
                    prescription.medicine_id = medicine_id
                    prescription.dosage = dosage
                    prescription.duration = duration
                    prescription.instructions = instructions
                    db.session.commit()
                    flash('Рецепт успешно обновлен!', 'success')
                else:
                    flash('Недостаточно лекарств на складе!', 'danger')
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
            flash("Рецепт успешно удален!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка: {e}", "danger")
        return redirect(url_for('view_prescriptions'))
