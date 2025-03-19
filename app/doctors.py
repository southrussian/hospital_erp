from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from models import *
from datetime import datetime


def setup_view_doctors_routes(app):
    @app.route('/view_doctors')
    def view_doctors():
        sort_order = request.args.get('sort', 'asc')  # По умолчанию сортировка по возрастанию
        search_query = request.args.get('search', '').strip()  # Получаем поисковый запрос
        doctors_query = Doctor.query

        if search_query:
            doctors_query = doctors_query.filter(
                (Doctor.last_name.ilike(f'%{search_query}%')) |
                (Doctor.first_name.ilike(f'%{search_query}%'))
            )

        if sort_order == 'asc':
            doctors_query = doctors_query.order_by(Doctor.last_name.asc())
        else:
            doctors_query = doctors_query.order_by(Doctor.last_name.desc())

        doctors = doctors_query.all()

        return render_template('view_doctors.html', doctors=doctors,
                               search_query=search_query, sort_order=sort_order)


def setup_add_doctor_routes(app):
    @app.route('/add_doctor', methods=['GET', 'POST'])
    def add_doctor():
        users = User.query.filter_by(role='doctor').all()
        departments = Department.query.all()

        if request.method == 'POST':
            # Обязательные поля
            required_fields = ['user_id', 'first_name', 'last_name', 'birth_date']
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    flash(f"Field {field.replace('_', ' ').title()} is required.", "danger")
                    return redirect(url_for('add_doctor'))

            user_id = request.form['user_id']
            first_name = request.form['first_name'].strip()
            middle_name = request.form.get('middle_name', '').strip()
            last_name = request.form['last_name'].strip()
            specialization = request.form.get('specialization', '').strip()
            birth_date_str = request.form['birth_date']
            phone_number = request.form.get('phone_number', '').strip()
            department_id = request.form.get('department_id')

            # Проверка пользователя
            user = User.query.get(user_id)
            if not user or user.role != 'doctor':
                flash("Invalid user selected.", "danger")
                return redirect(url_for('add_doctor'))

            # Проверка уникальности user_id
            if Doctor.query.filter_by(user_id=user_id).first():
                flash("This user is already registered as a doctor.", "danger")
                return redirect(url_for('add_doctor'))

            # Парсинг даты
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format. Use YYYY-MM-DD.", "danger")
                return redirect(url_for('add_doctor'))

            # Валидация номера телефона
            if phone_number and len(phone_number) != 11:
                flash("Phone number must be 11 digits.", "danger")
                return redirect(url_for('add_doctor'))

            # Обработка department_id
            department_id = int(department_id) if department_id else None
            if department_id and not Department.query.get(department_id):
                flash("Invalid department selected.", "danger")
                return redirect(url_for('add_doctor'))

            doctor = Doctor(
                user_id=user_id,
                first_name=first_name,
                middle_name=middle_name or None,  # Сохраняем None если пусто
                last_name=last_name,
                specialization=specialization or None,
                birth_date=birth_date,
                phone_number=phone_number or None,
                department_id=department_id
            )

            try:
                db.session.add(doctor)
                db.session.commit()
                flash("Doctor added successfully!", "success")
                return redirect(url_for('view_doctors'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error adding doctor: {str(e)}", "danger")

        return render_template('add_doctor.html', users=users, departments=departments)


def setup_edit_doctor_routes(app):
    @app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
    def edit_doctor(doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        users = User.query.filter_by(role='doctor').all()
        departments = Department.query.all()

        if request.method == 'POST':
            try:
                # Логируем входящие данные
                app.logger.info(f"Received form data: {request.form}")

                # Проверка обязательных полей
                required_fields = ['first_name', 'last_name', 'birth_date']
                for field in required_fields:
                    if field not in request.form or not request.form[field].strip():
                        flash(f"Поле {field.replace('_', ' ').title()} обязательно для заполнения.", "danger")
                        app.logger.warning(f"Missing or empty required field: {field}")
                        return redirect(url_for('edit_doctor', doctor_id=doctor_id))

                # Обновление данных врача
                doctor.first_name = request.form['first_name'].strip()
                doctor.middle_name = request.form.get('middle_name', '').strip() or None
                doctor.last_name = request.form['last_name'].strip()
                doctor.specialization = request.form.get('specialization', '').strip() or None

                # Валидация даты рождения
                try:
                    doctor.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
                except ValueError as e:
                    flash("Неверный формат даты. Используйте YYYY-MM-DD.", "danger")
                    app.logger.error(f"Invalid date format: {request.form['birth_date']}")
                    return redirect(url_for('edit_doctor', doctor_id=doctor_id))

                # Валидация номера телефона
                phone_number = request.form.get('phone_number', '').strip()
                if phone_number and len(phone_number) != 11:
                    flash("Номер телефона должен состоять из 11 цифр.", "danger")
                    app.logger.warning(f"Invalid phone number: {phone_number}")
                    return redirect(url_for('edit_doctor', doctor_id=doctor_id))
                doctor.phone_number = phone_number or None

                # Назначение отделения
                department_id = request.form.get('department_id')
                doctor.department_id = int(department_id) if department_id else None

                # Сохранение изменений
                db.session.commit()
                flash("Данные врача успешно обновлены!", "success")
                app.logger.info(f"Doctor {doctor_id} updated successfully.")
                return redirect(url_for('view_doctors'))

            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении данных врача: {str(e)}", "danger")
                app.logger.error(f"Error updating doctor {doctor_id}: {str(e)}", exc_info=True)
                return redirect(url_for('edit_doctor', doctor_id=doctor_id))

        return render_template('edit_doctor.html', doctor=doctor, users=users, departments=departments)


def setup_delete_doctor_routes(app):
    @app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
    def delete_doctor(doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        try:
            db.session.delete(doctor)
            db.session.commit()
            flash("Doctor deleted successfully!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Cannot delete doctor. There are related records in the system.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting doctor: {str(e)}", "danger")
        return redirect(url_for('view_doctors'))
