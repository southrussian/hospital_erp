from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from models import Patient, db
from datetime import datetime


def setup_view_patients_routes(app):
    @app.route('/view_patients')
    def view_patients():
        try:
            sort_order = request.args.get('sort', 'asc')  # По умолчанию сортировка по возрастанию
            patients_query = Patient.query

            # Сортировка по фамилии
            if sort_order == 'asc':
                patients_query = patients_query.order_by(Patient.last_name.asc())
            else:
                patients_query = patients_query.order_by(Patient.last_name.desc())

            patients = patients_query.all()
            return render_template('view_patients.html', patients=patients, sort_order=sort_order)

        except Exception as e:
            flash(f"Ошибка при загрузке пациентов: {str(e)}", "danger")
            return redirect(url_for('index'))  # Перенаправление на главную страницу


def setup_add_patient_routes(app):
    @app.route('/add_patient', methods=['GET', 'POST'])
    def add_patient():
        if request.method == 'POST':
            try:
                # Валидация обязательных полей
                required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 'oms_number']
                for field in required_fields:
                    if not request.form.get(field):
                        flash(f"Поле '{field.replace('_', ' ').title()}' обязательно для заполнения", "danger")
                        return redirect(url_for('add_patient'))

                # Парсинг даты рождения
                birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()

                # Валидация номера телефона
                phone_number = request.form.get('phone_number', '').strip()
                if phone_number and (len(phone_number) != 11 or not phone_number.isdigit()):
                    flash("Номер телефона должен состоять из 11 цифр", "danger")
                    return redirect(url_for('add_patient'))

                # Валидация ОМС
                oms_number = request.form['oms_number'].strip()
                if len(oms_number) != 16 or not oms_number.isdigit():
                    flash("Номер ОМС должен состоять из 16 цифр", "danger")
                    return redirect(url_for('add_patient'))

                # Создание пациента
                patient = Patient(
                    first_name=request.form['first_name'].strip(),
                    middle_name=request.form.get('middle_name', '').strip() or None,
                    last_name=request.form['last_name'].strip(),
                    birth_date=birth_date,
                    gender=request.form['gender'],
                    address=request.form.get('address', '').strip() or None,
                    phone_number=phone_number or None,
                    emergency_contact=request.form.get('emergency_contact', '').strip() or None,
                    passport_series=request.form.get('passport_series', '').strip() or None,
                    passport_number=request.form.get('passport_number', '').strip() or None,
                    oms_number=oms_number
                )

                db.session.add(patient)
                db.session.commit()
                flash("Пациент успешно добавлен!", "success")
                return redirect(url_for('view_patients'))

            except IntegrityError:
                db.session.rollback()
                flash("Пациент с таким номером ОМС уже существует", "danger")
            except ValueError as e:
                db.session.rollback()
                flash(f"Ошибка в формате данных: {str(e)}", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при добавлении пациента: {str(e)}", "danger")

        return render_template('add_patient.html')


def setup_edit_patient_routes(app):
    @app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
    def edit_patient(patient_id):
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            try:
                # Валидация обязательных полей
                required_fields = ['first_name', 'last_name', 'birth_date', 'gender', 'oms_number']
                for field in required_fields:
                    if not request.form.get(field):
                        flash(f"Поле '{field.replace('_', ' ').title()}' обязательно для заполнения", "danger")
                        return redirect(url_for('edit_patient', patient_id=patient_id))

                # Обновление данных
                patient.first_name = request.form['first_name'].strip()
                patient.middle_name = request.form.get('middle_name', '').strip() or None
                patient.last_name = request.form['last_name'].strip()
                patient.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
                patient.gender = request.form['gender']
                patient.address = request.form.get('address', '').strip() or None
                patient.phone_number = request.form.get('phone_number', '').strip() or None
                patient.emergency_contact = request.form.get('emergency_contact', '').strip() or None
                patient.passport_series = request.form.get('passport_series', '').strip() or None
                patient.passport_number = request.form.get('passport_number', '').strip() or None
                patient.oms_number = request.form['oms_number'].strip()

                db.session.commit()
                flash("Данные пациента успешно обновлены!", "success")
                return redirect(url_for('view_patients'))

            except IntegrityError:
                db.session.rollback()
                flash("Пациент с таким номером ОМС уже существует", "danger")
            except ValueError as e:
                db.session.rollback()
                flash(f"Ошибка в формате данных: {str(e)}", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении данных: {str(e)}", "danger")

        return render_template('edit_patient.html', patient=patient)


def setup_delete_patient_routes(app):
    @app.route('/delete_patient/<int:patient_id>', methods=['POST'])
    def delete_patient(patient_id):
        patient = Patient.query.get_or_404(patient_id)
        try:
            db.session.delete(patient)
            db.session.commit()
            flash("Пациент успешно удален!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении пациента: {str(e)}", "danger")
        return redirect(url_for('view_patients'))
