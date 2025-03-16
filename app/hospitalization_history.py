from flask import render_template, redirect, url_for, flash, request
from models import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def setup_view_hospitalization_history_routes(app):
    @app.route('/view_hospitalization_history')
    def view_hospitalization_history():
        hospitalizations = HospitalizationHistory.query.options(
            db.joinedload(HospitalizationHistory.patient),
            db.joinedload(HospitalizationHistory.bed),
            db.joinedload(HospitalizationHistory.admission)
        ).all()
        return render_template('view_hospitalization_history.html', hospitalizations=hospitalizations)


def setup_add_hospitalization_history_routes(app):
    @app.route('/add_hospitalization_history', methods=['GET', 'POST'])
    def add_hospitalization_history():
        patients = Patient.query.all()
        beds = Bed.query.all()
        admissions = Admission.query.all()

        if request.method == 'POST':
            # Получение данных из формы
            patient_id = request.form.get('patient_id', '').strip()
            bed_id = request.form.get('bed_id', '').strip()
            admission_id = request.form.get('admission_id', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()

            errors = []

            # Валидация обязательных полей
            required_fields = {
                'patient_id': 'Пациент',
                'bed_id': 'Койка',
                'admission_id': 'Поступление',
                'start_date': 'Дата начала'
            }
            for field, name in required_fields.items():
                if not locals()[field]:
                    errors.append(f"{name} обязателен для заполнения")

            # Валидация дат
            start_date = None
            end_date = None

            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    errors.append("Неверный формат даты начала (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                    if end_date <= start_date:
                        errors.append("Дата окончания должна быть позже даты начала")
                except ValueError:
                    errors.append("Неверный формат даты окончания (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('add_hospitalization_history.html', patients=patients,
                                       beds=beds, admissions=admissions, form_data=request.form)

            try:
                # Создание новой записи о госпитализации
                hospitalization = HospitalizationHistory(
                    patient_id=patient_id,
                    bed_id=bed_id,
                    admission_id=admission_id,
                    start_date=start_date,
                    end_date=end_date
                )

                db.session.add(hospitalization)
                db.session.commit()
                flash('Запись о госпитализации успешно добавлена!', 'success')
                return redirect(url_for('view_hospitalization_history'))

            except IntegrityError as e:
                db.session.rollback()
                if 'foreign key constraint' in str(e).lower():
                    flash('Ошибка связанных данных (пациент, койка или поступление не существуют)', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('add_hospitalization_history.html', patients=patients, beds=beds,
                               admissions=admissions)


def setup_edit_hospitalization_history_routes(app):
    @app.route('/edit_hospitalization_history/<int:history_id>', methods=['GET', 'POST'])
    def edit_hospitalization_history(history_id):
        hospitalization = HospitalizationHistory.query.get_or_404(history_id)
        patients = Patient.query.all()
        beds = Bed.query.all()
        admissions = Admission.query.all()

        if request.method == 'POST':
            # Получение данных из формы
            patient_id = request.form.get('patient_id', '').strip()
            bed_id = request.form.get('bed_id', '').strip()
            admission_id = request.form.get('admission_id', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()

            errors = []

            # Валидация обязательных полей
            required_fields = {
                'patient_id': 'Пациент',
                'bed_id': 'Койка',
                'admission_id': 'Поступление',
                'start_date': 'Дата начала'
            }
            for field, name in required_fields.items():
                if not locals()[field]:
                    errors.append(f"{name} обязателен для заполнения")

            # Валидация дат
            start_date = hospitalization.start_date
            end_date = hospitalization.end_date

            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    errors.append("Неверный формат даты начала (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                    if end_date <= start_date:
                        errors.append("Дата окончания должна быть позже даты начала")
                except ValueError:
                    errors.append("Неверный формат даты окончания (используйте ГГГГ-ММ-ДД ЧЧ:ММ)")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('edit_hospitalization_history.html',
                                       hospitalization=hospitalization, patients=patients, beds=beds,
                                       admissions=admissions, form_data=request.form)

            try:
                # Обновление записи
                hospitalization.patient_id = patient_id
                hospitalization.bed_id = bed_id
                hospitalization.admission_id = admission_id
                hospitalization.start_date = start_date
                hospitalization.end_date = end_date

                db.session.commit()
                flash('Запись о госпитализации успешно обновлена!', 'success')
                return redirect(url_for('view_hospitalization_history'))

            except IntegrityError as e:
                db.session.rollback()
                if 'foreign key constraint' in str(e).lower():
                    flash('Ошибка связанных данных (пациент, койка или поступление не существуют)', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обновлении: {e}', 'danger')

        return render_template('edit_hospitalization_history.html', hospitalization=hospitalization,
                               patients=patients, beds=beds, admissions=admissions)


def setup_delete_hospitalization_history_routes(app):
    @app.route('/delete_hospitalization_history/<int:history_id>', methods=['POST'])
    def delete_hospitalization_history(history_id):
        try:
            hospitalization = HospitalizationHistory.query.get_or_404(history_id)
            db.session.delete(hospitalization)
            db.session.commit()
            flash("Запись о госпитализации успешно удалена!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Невозможно удалить запись, связанную с другими данными", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {e}", "danger")
        return redirect(url_for('view_hospitalization_history'))
