from flask import render_template, redirect, url_for, flash, request
from models import *
from datetime import datetime


def view_doctors(app):
    @app.route('/view_doctors')
    def view_doctors():
        doctors = Doctor.query.all()
        return render_template('view_doctors.html', doctors=doctors)


def add_doctor(app):
    @app.route('/add_doctor', methods=['GET', 'POST'])
    def add_doctor():
        users = User.query.filter_by(role='doctor').all()
        departments = Department.query.all()

        if request.method == 'POST':
            user_id = request.form['user_id']
            first_name = request.form['first_name']
            middle_name = request.form['middle_name']
            last_name = request.form['last_name']
            specialization = request.form['specialization']
            birth_date_str = request.form['birth_date']
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            phone_number = request.form['phone_number']
            department_id = request.form['department_id']

            doctor = Doctor(
                user_id=user_id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                specialization=specialization,
                birth_date=birth_date,
                phone_number=phone_number,
                department_id=department_id
            )

            try:
                db.session.add(doctor)
                db.session.commit()
                flash("Doctor added successfully!", "success")
                return redirect(url_for('add_doctor'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")

        return render_template('add_doctor.html', users=users, departments=departments)


def edit_doctor(app):
    @app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
    def edit_doctor(doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        users = User.query.filter_by(role='doctor').all()
        departments = Department.query.all()

        if request.method == 'POST':
            doctor.user_id = request.form['user_id']
            doctor.first_name = request.form['first_name']
            doctor.middle_name = request.form['middle_name']
            doctor.last_name = request.form['last_name']
            doctor.specialization = request.form['specialization']
            doctor.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
            doctor.phone_number = request.form['phone_number']
            doctor.department_id = request.form['department_id']

            try:
                db.session.commit()
                flash("Doctor updated successfully!", "success")
                return redirect(url_for('view_doctors'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")

        return render_template('edit_doctor.html', doctor=doctor, users=users, departments=departments)


def delete_doctor(app):
    @app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
    def delete_doctor(doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        try:
            db.session.delete(doctor)
            db.session.commit()
            flash("Doctor deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_doctors'))