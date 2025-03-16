from flask import render_template, redirect, url_for, flash, request
from models import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta


def setup_view_prescriptions_routes(app):
    @app.route('/view_prescriptions')
    def view_prescriptions():
        prescriptions = Prescription.query.options(
            db.joinedload(Prescription.patient),
            db.joinedload(Prescription.medicine),
            db.joinedload(Prescription.doctor)
        ).all()
        return render_template('view_prescriptions.html', prescriptions=prescriptions)


def setup_add_prescription_routes(app):
    @app.route('/add_prescription', methods=['GET', 'POST'])
    def add_prescription():
        patients = Patient.query.all()
        doctors = Doctor.query.all()
        medicines = Medicine.query.all()

        if request.method == 'POST':
            patient_id = request.form.get('patient_id', '').strip()
            medicine_id = request.form.get('medicine_id', '').strip()
            doctor_id = request.form.get('doctor_id', '').strip()
            dosage = request.form.get('dosage', '').strip()
            frequency = request.form.get('frequency', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            status = request.form.get('status', 'active').strip()
            instructions = request.form.get('instructions', '').strip()

            errors = []

            required_fields = {
                'patient_id': 'Пациент',
                'medicine_id': 'Лекарство',
                'doctor_id': 'Врач',
                'dosage': 'Дозировка'
            }

            for field, name in required_fields.items():
                if not locals()[field]:
                    errors.append(f"{name} обязателен для заполнения")

            try:
                patient = Patient.query.get(int(patient_id))
                if not patient:
                    errors.append("Указанный пациент не существует")
            except ValueError:
                errors.append("Неверный ID пациента")

            try:
                medicine = Medicine.query.get(int(medicine_id))
                if not medicine:
                    errors.append("Указанное лекарство не существует")
            except ValueError:
                errors.append("Неверный ID лекарства")

            try:
                doctor = Doctor.query.get(int(doctor_id))
                if not doctor:
                    errors.append("Указанный врач не существует")
            except ValueError:
                errors.append("Неверный ID врача")

            start_date = datetime.now()
            end_date = None

            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                    if start_date < datetime.now() - timedelta(minutes=5):
                        errors.append("Дата начала не может быть в прошлом")
                except ValueError:
                    errors.append("Неверный формат даты начала")

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                    if end_date <= start_date:
                        errors.append("Дата окончания должна быть позже даты начала")
                except ValueError:
                    errors.append("Неверный формат даты окончания")

            valid_statuses = ['active', 'completed', 'cancelled']
            if status not in valid_statuses:
                errors.append("Неверный статус рецепта")

            dosage_int = int(dosage)

            try:
                if dosage_int <= 0:
                    errors.append("Дозировка должна быть положительным числом")
            except ValueError:
                errors.append("Некорректное значение дозировки")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('add_prescription.html',
                                       patients=patients,
                                       doctors=doctors,
                                       medicines=medicines,
                                       form_data=request.form)

            try:
                inventory = MedicineInventory.query.filter_by(medicine_id=medicine_id).first()
                if not inventory or inventory.quantity < dosage_int:
                    flash('Недостаточно лекарств на складе!', 'danger')
                    return render_template('add_prescription.html',
                                           patients=patients,
                                           doctors=doctors,
                                           medicines=medicines,
                                           form_data=request.form)

                # Создание рецепта
                prescription = Prescription(
                    patient_id=patient_id,
                    medicine_id=medicine_id,
                    doctor_id=doctor_id,
                    dosage=dosage,
                    frequency=frequency or None,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                    instructions=instructions or None
                )

                # Обновление инвентаря
                inventory.quantity -= dosage_int
                inventory.last_updated = datetime.now()

                db.session.add(prescription)
                db.session.commit()
                flash('Рецепт успешно создан!', 'success')
                return redirect(url_for('view_prescriptions'))

            except IntegrityError as e:
                db.session.rollback()
                flash('Ошибка целостности данных: проверьте правильность введенных данных', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('add_prescription.html',
                               patients=patients,
                               doctors=doctors,
                               medicines=medicines)


def setup_edit_prescription_routes(app):
    @app.route('/edit_prescription/<int:prescription_id>', methods=['GET', 'POST'])
    def edit_prescription(prescription_id):
        prescription = Prescription.query.get_or_404(prescription_id)
        patients = Patient.query.all()
        doctors = Doctor.query.all()
        medicines = Medicine.query.all()

        if request.method == 'POST':
            # Получение данных
            medicine_id = request.form.get('medicine_id', '').strip()
            dosage = request.form.get('dosage', '').strip()
            frequency = request.form.get('frequency', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            status = request.form.get('status', '').strip()
            instructions = request.form.get('instructions', '').strip()

            errors = []
            original_medicine_id = prescription.medicine_id
            original_dosage = prescription.dosage

            dosage_int = int(dosage)

            try:
                if dosage_int <= 0:
                    errors.append("Дозировка должна быть положительным числом")
            except ValueError:
                errors.append("Некорректное значение дозировки")

            # Валидация даты окончания
            end_date = prescription.end_date
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                    if end_date <= prescription.start_date:
                        errors.append("Дата окончания должна быть позже даты начала")
                except ValueError:
                    errors.append("Неверный формат даты окончания")

            # Валидация статуса
            valid_statuses = ['active', 'completed', 'cancelled']
            if status not in valid_statuses:
                errors.append("Неверный статус рецепта")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('edit_prescription.html',
                                       prescription=prescription,
                                       patients=patients,
                                       doctors=doctors,
                                       medicines=medicines,
                                       form_data=request.form)

            try:
                # Обновление инвентаря при изменении лекарства или дозировки
                if medicine_id != str(original_medicine_id) or dosage_int != original_dosage:
                    # Возврат предыдущего количества
                    old_inventory = MedicineInventory.query.filter_by(medicine_id=original_medicine_id).first()
                    if old_inventory:
                        old_inventory.quantity += original_dosage
                        old_inventory.last_updated = datetime.now()

                    # Проверка нового количества
                    new_inventory = MedicineInventory.query.filter_by(medicine_id=medicine_id).first()
                    if not new_inventory or new_inventory.quantity < dosage_int:
                        flash('Недостаточно лекарств на складе!', 'danger')
                        return render_template('edit_prescription.html',
                                               prescription=prescription,
                                               patients=patients,
                                               doctors=doctors,
                                               medicines=medicines,
                                               form_data=request.form)

                    new_inventory.quantity -= dosage_int
                    new_inventory.last_updated = datetime.now()

                prescription.medicine_id = medicine_id
                prescription.dosage = dosage_int
                prescription.frequency = frequency or None
                prescription.end_date = end_date
                prescription.status = status
                prescription.instructions = instructions or None

                db.session.commit()
                flash('Рецепт успешно обновлен!', 'success')
                return redirect(url_for('view_prescriptions'))

            except IntegrityError:
                db.session.rollback()
                flash('Ошибка целостности данных при обновлении', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обновлении: {e}', 'danger')

        return render_template('edit_prescription.html',
                               prescription=prescription,
                               patients=patients,
                               doctors=doctors,
                               medicines=medicines)


def setup_delete_prescription_routes(app):
    @app.route('/delete_prescription/<int:prescription_id>', methods=['POST'])
    def delete_prescription(prescription_id):
        try:
            prescription = Prescription.query.get_or_404(prescription_id)

            # Возврат лекарства в инвентарь
            if prescription.status == 'active':
                inventory = MedicineInventory.query.filter_by(medicine_id=prescription.medicine_id).first()
                if inventory:
                    inventory.quantity += prescription.dosage
                    inventory.last_updated = datetime.now()

            db.session.delete(prescription)
            db.session.commit()
            flash("Рецепт успешно удален!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Невозможно удалить рецепт, связанный с другими записями", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {e}", "danger")
        return redirect(url_for('view_prescriptions'))
