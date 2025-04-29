from flask import render_template, redirect, url_for, flash, request
from models import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def setup_operations_routes(app):
    @app.route('/view_operations')
    def view_operations():
        operations = Operation.query.options(
            db.joinedload(Operation.patient),
            db.joinedload(Operation.doctor)
        ).all()
        return render_template('view_operations.html', operations=operations)

    @app.route('/add_operation', methods=['GET', 'POST'])
    def add_operation():
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            patient_id = request.form.get('patient_id', '').strip()
            doctor_id = request.form.get('doctor_id', '').strip()
            operation_type = request.form.get('type', '').strip()
            operation_date_str = request.form.get('operation_date', '').strip()
            duration = request.form.get('duration', '').strip()
            outcome = request.form.get('outcome', '').strip()
            notes = request.form.get('notes', '').strip()

            errors = []

            try:
                patient = Patient.query.get(int(patient_id))
                if not patient:
                    errors.append("Пациент не найден")
            except (ValueError, TypeError):
                errors.append("Неверный ID пациента")

            try:
                doctor = Doctor.query.get(int(doctor_id))
                if not doctor:
                    errors.append("Врач не найден")
            except (ValueError, TypeError):
                errors.append("Неверный ID врача")

            if not operation_type:
                errors.append("Тип операции обязателен для заполнения")
            elif len(operation_type) > 100:
                errors.append("Тип операции не должен превышать 100 символов")

            operation_date = datetime.now()
            if operation_date_str:
                try:
                    operation_date = datetime.strptime(operation_date_str, '%Y-%m-%dT%H:%M')
                    if operation_date > datetime.now():
                        errors.append("Дата операции не может быть в будущем")
                except ValueError:
                    errors.append("Неверный формат даты (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            duration_int = None
            if duration:
                try:
                    duration_int = int(duration)
                    if duration_int < 0:
                        errors.append("Длительность не может быть отрицательной")
                except ValueError:
                    errors.append("Некорректное значение длительности")

            if outcome and len(outcome) > 150:
                errors.append("Исход не должен превышать 150 символов")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('add_operation.html',
                                       patients=patients,
                                       doctors=doctors,
                                       form_data=request.form)

            try:
                operation = Operation(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    type=operation_type,
                    operation_date=operation_date,
                    duration=duration_int,
                    outcome=outcome if outcome else None,
                    notes=notes if notes else None
                )

                db.session.add(operation)
                db.session.commit()
                flash('Операция успешно добавлена!', 'success')
                return redirect(url_for('view_operations'))

            except IntegrityError as e:
                db.session.rollback()
                if 'foreign key constraint' in str(e).lower():
                    flash('Ошибка связанных данных (пациент или врач не существуют)', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('add_operation.html',
                               patients=patients,
                               doctors=doctors)

    @app.route('/edit_operation/<int:operation_id>', methods=['GET', 'POST'])
    def edit_operation(operation_id):
        operation = Operation.query.get_or_404(operation_id)
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            patient_id = request.form.get('patient_id', '').strip()
            doctor_id = request.form.get('doctor_id', '').strip()
            operation_type = request.form.get('type', '').strip()
            operation_date_str = request.form.get('operation_date', '').strip()
            duration = request.form.get('duration', '').strip()
            outcome = request.form.get('outcome', '').strip()
            notes = request.form.get('notes', '').strip()

            errors = []

            try:
                patient = Patient.query.get(int(patient_id))
                if not patient:
                    errors.append("Пациент не найден")
            except (ValueError, TypeError):
                errors.append("Неверный ID пациента")

            try:
                doctor = Doctor.query.get(int(doctor_id))
                if not doctor:
                    errors.append("Врач не найден")
            except (ValueError, TypeError):
                errors.append("Неверный ID врача")

            if not operation_type:
                errors.append("Тип операции обязателен для заполнения")
            elif len(operation_type) > 100:
                errors.append("Тип операции не должен превышать 100 символов")

            # Валидация даты операции
            operation_date = operation.operation_date
            if operation_date_str:
                try:
                    operation_date = datetime.strptime(operation_date_str, '%Y-%m-%dT%H:%M')
                    if operation_date > datetime.now():
                        errors.append("Дата операции не может быть в будущем")
                except ValueError:
                    errors.append("Неверный формат даты (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            duration_int = operation.duration
            if duration:
                try:
                    duration_int = int(duration)
                    if duration_int < 0:
                        errors.append("Длительность не может быть отрицательной")
                except ValueError:
                    errors.append("Некорректное значение длительности")

            if outcome and len(outcome) > 150:
                errors.append("Исход не должен превышать 150 символов")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('edit_operation.html',
                                       operation=operation,
                                       patients=patients,
                                       doctors=doctors,
                                       form_data=request.form)

            try:
                operation.patient_id = patient_id
                operation.doctor_id = doctor_id
                operation.type = operation_type
                operation.operation_date = operation_date
                operation.duration = duration_int
                operation.outcome = outcome if outcome else None
                operation.notes = notes if notes else None

                db.session.commit()
                flash('Операция успешно обновлена!', 'success')
                return redirect(url_for('view_operations'))

            except IntegrityError as e:
                db.session.rollback()
                if 'foreign key constraint' in str(e).lower():
                    flash('Ошибка связанных данных (пациент или врач не существуют)', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('edit_operation.html',
                               operation=operation,
                               patients=patients,
                               doctors=doctors)

    @app.route('/delete_operation/<int:operation_id>', methods=['POST'])
    def delete_operation(operation_id):
        try:
            operation = Operation.query.get_or_404(operation_id)
            db.session.delete(operation)
            db.session.commit()
            flash("Операция успешно удалена!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Невозможно удалить операцию, так как она связана с другими записями", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {e}", "danger")
        return redirect(url_for('view_operations'))
