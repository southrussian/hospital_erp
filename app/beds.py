from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from models import *


def setup_view_beds_routes(app):
    @app.route('/view_beds')
    def view_beds():
        try:
            # Загружаем койки с информацией о палатах и пациентах
            beds = Bed.query.options(
                db.joinedload(Bed.room),
                db.joinedload(Bed.patient)
            ).all()
            return render_template('view_beds.html', beds=beds)
        except Exception as e:
            app.logger.error(e)
            flash(f"Ошибка при загрузке данных: {str(e)}", "danger")
            return redirect(url_for('index'))


def setup_add_bed_routes(app):
    @app.route('/add_bed', methods=['GET', 'POST'])
    def add_bed():
        rooms = Room.query.all()
        patients = Patient.query.filter_by(bed=None).all()  # Только пациенты без кроватей

        if request.method == 'POST':
            try:
                room_id = int(request.form['room_id'])
                patient_id = request.form.get('patient_id')  # Может быть None

                room = Room.query.get_or_404(room_id)
                if room.available_beds() <= 0:
                    flash('Палата полностью заполнена! Невозможно добавить койку.', 'danger')
                    return redirect(url_for('add_bed'))

                # Проверка, что пациент не привязан к другой койке
                if patient_id:
                    existing_bed = Bed.query.filter_by(patient_id=patient_id).first()
                    if existing_bed:
                        flash('Этот пациент уже привязан к другой койке!', 'danger')
                        return redirect(url_for('add_bed'))

                bed = Bed(
                    room_id=room_id,
                    patient_id=patient_id
                )

                db.session.add(bed)
                db.session.commit()
                flash('Койка успешно добавлена!', 'success')
                return redirect(url_for('view_beds'))

            except ValueError as e:
                app.logger.error(e)
                db.session.rollback()
                flash("Некорректные данные в форме", "danger")
            except IntegrityError as e:
                app.logger.error(e)
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                app.logger.error(e)
                db.session.rollback()
                flash(f"Ошибка при добавлении: {str(e)}", "danger")

        return render_template('add_bed.html', rooms=rooms, patients=patients)


def setup_edit_bed_routes(app):
    @app.route('/edit_bed/<int:bed_id>', methods=['GET', 'POST'])
    def edit_bed(bed_id):
        bed = Bed.query.get_or_404(bed_id)
        rooms = Room.query.all()
        patients = Patient.query.filter_by(bed=None).all()

        if request.method == 'POST':
            try:
                new_room_id = int(request.form['room_id'])
                new_patient_id = request.form.get('patient_id')  # Может быть None

                # Проверка доступности мест в новой палате
                if bed.room_id != new_room_id:
                    new_room = Room.query.get_or_404(new_room_id)
                    if new_room.available_beds() <= 0:
                        flash('Новая палата полностью заполнена!', 'danger')
                        return redirect(url_for('edit_bed', bed_id=bed_id))

                # Проверка, что новый пациент не привязан к другой койке
                if new_patient_id and new_patient_id != bed.patient_id:
                    existing_bed = Bed.query.filter_by(patient_id=new_patient_id).first()
                    if existing_bed:
                        flash('Этот пациент уже привязан к другой койке!', 'danger')
                        return redirect(url_for('edit_bed', bed_id=bed_id))

                # Обновление данных
                bed.room_id = new_room_id
                bed.patient_id = new_patient_id

                db.session.commit()
                flash('Койка успешно обновлена!', 'success')
                return redirect(url_for('view_beds'))

            except ValueError as e:
                app.logger.error(e)
                db.session.rollback()
                flash("Некорректные данные в форме", "danger")
            except IntegrityError as e:
                app.logger.error(e)
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении: {str(e)}", "danger")

        return render_template('edit_bed.html',
                               rooms=rooms,
                               patients=patients,
                               bed=bed)


def setup_delete_bed_routes(app):
    @app.route('/delete_bed/<int:bed_id>', methods=['POST'])
    def delete_bed(bed_id):
        bed = Bed.query.get_or_404(bed_id)
        try:
            if bed.patient_id:
                flash('Невозможно удалить занятую койку!', 'danger')
                return redirect(url_for('view_beds'))

            db.session.delete(bed)
            db.session.commit()
            flash('Койка успешно удалена!', 'success')
        except IntegrityError as e:
            app.logger.error(e)
            db.session.rollback()
            flash(f"Ошибка целостности данных: {str(e)}", "danger")
        except Exception as e:
            app.logger.error(e)
            db.session.rollback()
            flash(f"Ошибка при удалении: {str(e)}", "danger")

        return redirect(url_for('view_beds'))
