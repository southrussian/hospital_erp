from flask import render_template, redirect, url_for, flash, request
from .models import *


def view_beds(app):
    @app.route('/view_beds')
    def view_beds():
        beds = Bed.query.all()
        return render_template('view_beds.html', beds=beds)


def add_bed(app):
    @app.route('/add_bed', methods=['GET', 'POST'])
    def add_bed():
        rooms = Room.query.all()
        patients = Patient.query.filter_by(bed=None).all()  # Только пациенты без кроватей

        if request.method == 'POST':
            room_id = request.form['room_id']
            room = Room.query.get(room_id)

            # Проверка доступности мест
            if room.is_full():
                flash('Палата полностью заполнена! Невозможно добавить койку.', 'danger')
                return redirect(url_for('add_bed'))

            patient_id = request.form.get('patient_id')  # Пациент может быть не назначен
            status = 'occupied' if patient_id else 'free'

            bed = Bed(
                room_id=room_id,
                patient_id=patient_id,
                status=status
            )

            try:
                db.session.add(bed)
                db.session.commit()
                flash('Койка успешно добавлена!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('add_bed'))

        return render_template('add_bed.html', rooms=rooms, patients=patients)


def edit_bed(app):
    @app.route('/edit_bed/<int:bed_id>', methods=['GET', 'POST'])
    def edit_bed(bed_id):
        bed = Bed.query.get_or_404(bed_id)
        rooms = Room.query.all()
        patients = Patient.query.all()

        if request.method == 'POST':
            new_room_id = request.form['room_id']
            new_room = Room.query.get(new_room_id)

            # Если меняем палату, проверяем доступность мест
            if bed.room_id != int(new_room_id) and new_room.is_full():
                flash('Новая палата полностью заполнена!', 'danger')
                return redirect(url_for('edit_bed', bed_id=bed_id))

            bed.room_id = new_room_id
            bed.patient_id = request.form.get('patient_id')
            bed.status = 'occupied' if bed.patient_id else 'free'

            try:
                db.session.commit()
                flash('Койка успешно обновлена!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('view_beds'))

        return render_template('edit_bed.html', rooms=rooms, patients=patients, bed=bed)


def delete_bed(app):
    @app.route('/delete_bed/<int:bed_id>', methods=['POST'])
    def delete_bed(bed_id):
        bed = Bed.query.get_or_404(bed_id)
        try:
            db.session.delete(bed)
            db.session.commit()
            flash("Bed deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_beds'))
