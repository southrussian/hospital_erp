from flask import render_template, redirect, url_for, flash, request
from .models import *


def view_departments(app):
    @app.route('/view_departments')
    def view_departments():
        departments = Department.query.all()
        return render_template('view_departments.html', departments=departments)


def add_department(app):
    @app.route('/add_department', methods=['GET', 'POST'])
    def add_department():
        if request.method == 'POST':
            name = request.form['name']
            location = request.form['location']
            phone_number = request.form['phone_number']

            department = Department(name=name, location=location, phone_number=phone_number)

            try:
                db.session.add(department)
                db.session.commit()
                flash("Department added successfully!", "success")
                return redirect(url_for('add_department'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")
        return render_template('add_department.html')


def edit_department(app):
    @app.route('/edit_department/<int:department_id>', methods=['GET', 'POST'])
    def edit_department(department_id):
        department = Department.query.get_or_404(department_id)

        if request.method == 'POST':
            department.name = request.form['name']
            department.location = request.form['location']
            department.phone_number = request.form['phone_number']

            try:
                db.session.commit()
                flash("Department updated successfully!", "success")
                return redirect(url_for('view_departments'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")
        return render_template('edit_department.html', department=department)


def delete_department(app):
    @app.route('/delete_department/<int:department_id>', methods=['POST'])
    def delete_department(department_id):
        department = Department.query.get_or_404(department_id)
        try:
            db.session.delete(department)
            db.session.commit()
            flash("Department deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_departments'))
