from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from models import *


def setup_medical_records_routes(app):
    @app.route('/medical_records')
    def view_medical_records():
        try:
            records = MedicalRecord.query.options(
                joinedload(MedicalRecord.patient),
                joinedload(MedicalRecord.doctor),
                joinedload(MedicalRecord.admission)
            ).order_by(MedicalRecord.created_at.desc()).all()
            return render_template('view_medical_records.html', records=records)
        except Exception as e:
            app.logger.error(f"Ошибка загрузки записей: {str(e)}")  # Добавьте логирование
            flash("Ошибка загрузки данных", "danger")
            return redirect(url_for('dashboard'))

    @app.route('/medical_records/add', methods=['GET', 'POST'])
    def add_medical_record():
        if request.method == 'POST':
            try:
                # Валидация обязательных полей
                required_fields = ['patient_id', 'record_type', 'content']
                for field in required_fields:
                    if not request.form.get(field):
                        flash(f"Поле '{field}' обязательно для заполнения", "danger")
                        return redirect(url_for('add_medical_record'))

                # Создание записи
                record = MedicalRecord(
                    patient_id=int(request.form['patient_id']),
                    doctor_id=int(request.form['doctor_id']) if request.form['doctor_id'] else None,
                    admission_id=int(request.form['admission_id']) if request.form['admission_id'] else None,
                    record_type=request.form['record_type'],
                    content=request.form['content']
                )

                db.session.add(record)
                db.session.commit()
                flash("Медицинская запись успешно создана!", "success")
                return redirect(url_for('view_medical_records'))

            except ValueError:
                db.session.rollback()
                flash("Некорректный формат данных", "danger")
            except IntegrityError as e:
                db.session.rollback()
                flash("Ошибка целостности данных: проверьте существование связанных записей", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при создании записи: {str(e)}", "danger")

        # GET-запрос
        patients = Patient.query.order_by(Patient.last_name).all()
        doctors = Doctor.query.order_by(Doctor.last_name).all()
        record_types = ['diagnosis', 'note', 'procedure']

        return render_template('add_medical_record.html',
                               patients=patients,
                               doctors=doctors,
                               record_types=record_types)

    @app.route('/medical_records/edit/<int:record_id>', methods=['GET', 'POST'])
    def edit_medical_record(record_id):
        record = MedicalRecord.query.options(
            joinedload(MedicalRecord.patient),
            joinedload(MedicalRecord.doctor),
            joinedload(MedicalRecord.admission)
        ).get_or_404(record_id)

        if request.method == 'POST':
            try:
                # Обновление данных
                record.patient_id = int(request.form['patient_id'])
                record.doctor_id = int(request.form['doctor_id']) if request.form['doctor_id'] else None
                record.admission_id = int(request.form['admission_id']) if request.form['admission_id'] else None
                record.record_type = request.form['record_type']
                record.content = request.form['content']

                db.session.commit()
                flash("Запись успешно обновлена!", "success")
                return redirect(url_for('view_medical_records'))

            except ValueError:
                db.session.rollback()
                flash("Некорректный формат данных", "danger")
            except IntegrityError as e:
                db.session.rollback()
                flash("Ошибка целостности данных: проверьте существование связанных записей", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении записи: {str(e)}", "danger")

        patients = Patient.query.order_by(Patient.last_name).all()
        doctors = Doctor.query.order_by(Doctor.last_name).all()
        record_types = ['diagnosis', 'note', 'procedure']
        admissions = Admission.query.filter_by(patient_id=record.patient_id).all()

        return render_template('edit_medical_record.html',
                               record=record,
                               patients=patients,
                               doctors=doctors,
                               admissions=admissions,
                               record_types=record_types)

    @app.route('/medical_records/delete/<int:record_id>', methods=['POST'])
    def delete_medical_record(record_id):
        record = MedicalRecord.query.get_or_404(record_id)
        try:
            db.session.delete(record)
            db.session.commit()
            flash("Медицинская запись успешно удалена!", "success")
        except IntegrityError as e:
            db.session.rollback()
            flash("Невозможно удалить запись, связанные данные существуют", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении записи: {str(e)}", "danger")

        return redirect(url_for('view_medical_records'))
