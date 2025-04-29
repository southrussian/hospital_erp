from flask import render_template, redirect, url_for, flash, request
from models import *


def setup_schedules_routes(app):
    @app.route('/view_schedule')
    def view_schedule():
        doctor_id = request.args.get('doctor_id')
        if doctor_id:
            schedules = Schedule.query.filter_by(doctor_id=doctor_id).all()
        else:
            schedules = Schedule.query.all()
        doctors = Doctor.query.all()
        return render_template('view_schedule.html', schedules=schedules, doctors=doctors, selected_doctor_id=doctor_id)

    @app.route('/add_schedule', methods=['GET', 'POST'])
    def add_schedule():
        if request.method == 'POST':
            doctor_id = request.form['doctor_id']
            day_of_week = request.form['day_of_week']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            start_time = datetime.strptime(start_time, '%H:%M').time()
            end_time = datetime.strptime(end_time, '%H:%M').time()

            schedule = Schedule(
                doctor_id=doctor_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )

            try:
                db.session.add(schedule)
                db.session.commit()
                flash('Расписание успешно добавлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при добавлении расписания: {str(e)}', 'danger')

            return redirect(url_for('add_schedule'))

        doctors = Doctor.query.all()
        return render_template('add_schedule.html', doctors=doctors)

    @app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
    def edit_schedule(schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        doctors = Doctor.query.all()

        if request.method == 'POST':
            schedule.doctor_id = request.form['doctor_id']
            schedule.day_of_week = request.form['day_of_week']
            schedule.start_time = request.form['start_time']
            schedule.end_time = request.form['end_time']

            schedule.start_time = datetime.strptime(schedule.start_time, '%H:%M').time()
            schedule.end_time = datetime.strptime(schedule.end_time, '%H:%M').time()

            try:
                db.session.commit()
                flash('Расписание успешно обновлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при обновлении расписания: {str(e)}', 'danger')

            return redirect(url_for('view_schedule'))

        return render_template('edit_schedule.html', schedule=schedule, doctors=doctors)

    @app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
    def delete_schedule(schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        try:
            db.session.delete(schedule)
            db.session.commit()
            flash("Sc deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_schedule'))
