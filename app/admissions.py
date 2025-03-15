from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
import pandas as pd
import plotly.express as px
from models import *


def setup_view_admissions_routes(app):
    @app.route('/view_admissions')
    def view_admissions():
        try:
            admissions = Admission.query.options(
                joinedload(Admission.patient),
                joinedload(Admission.user)
            ).order_by(Admission.admission_date.desc()).all()
            return render_template('view_admissions.html',
                                   admissions=admissions)
        except Exception as e:
            flash(f"Ошибка загрузки данных: {str(e)}", "danger")
            return redirect(url_for('index'))


def setup_add_admission_routes(app):
    @app.route('/add_admission', methods=['GET', 'POST'])
    def add_admission():
        if request.method == 'POST':
            try:
                # Валидация обязательных полей
                required_fields = ['patient_id', 'admission_date', 'reason', 'admitted_by']
                for field in required_fields:
                    if not request.form.get(field):
                        flash(f"Поле '{field}' обязательно для заполнения", "danger")
                        return redirect(url_for('add_admission'))

                # Парсинг данных
                admission_date = datetime.fromisoformat(request.form['admission_date'])
                discharge_date = datetime.fromisoformat(request.form['discharge_date']) if request.form[
                    'discharge_date'] else None

                # Проверка существования пациента и пользователя
                patient = Patient.query.get(request.form['patient_id'])
                if not patient:
                    flash("Указанный пациент не существует", "danger")
                    return redirect(url_for('add_admission'))

                user = User.query.get(request.form['admitted_by'])
                if not user or user.role not in ['doctor', 'admin']:
                    flash("Некорректный пользователь для оформления поступления", "danger")
                    return redirect(url_for('add_admission'))

                # Создание объекта
                admission = Admission(
                    patient_id=patient.patient_id,
                    admission_date=admission_date,
                    discharge_date=discharge_date,
                    reason=request.form['reason'],
                    admitted_by=user.user_id,
                    diagnosis=request.form.get('diagnosis'),
                    is_active=discharge_date is None
                )

                db.session.add(admission)
                db.session.commit()
                flash("Поступление успешно оформлено!", "success")
                return redirect(url_for('view_admissions'))

            except ValueError as e:
                db.session.rollback()
                flash(f"Ошибка формата данных: {str(e)}", "danger")
            except IntegrityError:
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при создании: {str(e)}", "danger")

        # Для GET-запроса
        patients = Patient.query.order_by(Patient.last_name).all()
        doctors = User.query.filter(User.role.in_(['doctor', 'admin'])).all()
        return render_template('add_admission.html',
                               patients=patients,
                               doctors=doctors)


def setup_edit_admission_routes(app):
    @app.route('/edit_admission/<int:admission_id>', methods=['GET', 'POST'])
    def edit_admission(admission_id):
        admission = Admission.query.options(
            joinedload(Admission.patient),
            joinedload(Admission.user)
        ).get_or_404(admission_id)

        if request.method == 'POST':
            try:
                # Обновление данных
                admission.admission_date = datetime.fromisoformat(request.form['admission_date'])
                admission.discharge_date = datetime.fromisoformat(request.form['discharge_date']) if request.form[
                    'discharge_date'] else None
                admission.reason = request.form['reason']
                admission.diagnosis = request.form.get('diagnosis')
                admission.is_active = admission.discharge_date is None

                # Обновление пользователя
                new_user = User.query.get(request.form['admitted_by'])
                if new_user and new_user.role in ['doctor', 'admin']:
                    admission.admitted_by = new_user.user_id
                else:
                    flash("Некорректный пользователь", "danger")
                    return redirect(url_for('edit_admission', admission_id=admission_id))

                db.session.commit()
                flash("Данные поступления обновлены!", "success")
                return redirect(url_for('view_admissions'))

            except ValueError as e:
                db.session.rollback()
                flash(f"Ошибка формата данных: {str(e)}", "danger")
            except IntegrityError:
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении: {str(e)}", "danger")

        patients = Patient.query.order_by(Patient.last_name).all()
        doctors = User.query.filter(User.role.in_(['doctor', 'admin'])).all()
        return render_template('edit_admission.html',
                               admission=admission,
                               patients=patients,
                               doctors=doctors)


def setup_delete_admission_routes(app):
    @app.route('/delete_admission/<int:admission_id>', methods=['POST'])
    def delete_admission(admission_id):
        admission = Admission.query.get_or_404(admission_id)
        try:
            # Проверка связанных записей
            if admission.hospitalizations:
                flash("Невозможно удалить поступление с привязанными госпитализациями", "danger")
                return redirect(url_for('view_admissions'))

            db.session.delete(admission)
            db.session.commit()
            flash("Поступление успешно удалено!", "success")
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка целостности данных: {str(e)}", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {str(e)}", "danger")

        return redirect(url_for('view_admissions'))


def setup_analyze_admissions_routes(app):
    @app.route('/analyze_admissions')
    def analyze_admissions():
        try:
            admissions = Admission.query.options(
                joinedload(Admission.patient),
                joinedload(Admission.user).joinedload(User.doctor)  # Добавляем загрузку Doctor
            ).all()

            # Подготовка данных
            admission_data = [{
                'date': a.admission_date.date(),
                'reason': a.reason,
                'doctor': f"{a.user.doctor.last_name} {a.user.doctor.first_name}" if a.user.doctor else "Неизвестно",
                'hour': a.admission_date.hour,
                'los': (a.discharge_date - a.admission_date).days if a.discharge_date else 0,
                'age': (a.admission_date.date() - a.patient.birth_date).days // 365,
                'gender': a.patient.gender
            } for a in admissions]

            # Генерация графиков
            figures = {
                'by_date': px.bar(
                    pd.DataFrame(admission_data),
                    x='date',
                    title='Поступления по датам'
                ),
                'by_reason': px.pie(
                    names=[d['reason'] for d in admission_data],
                    title='Распределение по причинам'
                ),
                'by_doctor': px.bar(
                    x=[d['doctor'] for d in admission_data],
                    title='Поступления по врачам'
                ),
                'by_hour': px.bar(
                    x=[d['hour'] for d in admission_data],
                    title='Поступления по времени суток'
                ),
                'los_dist': px.histogram(
                    x=[d['los'] for d in admission_data if d['los'] > 0],
                    title='Распределение длительности госпитализации'
                ),
                'age_dist': px.histogram(
                    x=[d['age'] for d in admission_data],
                    title='Распределение по возрастам'
                ),
                'gender_dist': px.pie(
                    names=[d['gender'] for d in admission_data],
                    title='Распределение по полу'
                )
            }

            graphs = {k: v.to_html(full_html=False) for k, v in figures.items()}
            return render_template('analyze_admissions.html', **graphs)

        except Exception as e:
            # Добавьте логирование ошибки
            app.logger.error(f"Ошибка анализа: {str(e)}", exc_info=True)
            flash("Невозможно построить графики. Проверьте данные.", "danger")
            return render_template('analyze_admissions.html')  # Возвращаем пустую страницу
