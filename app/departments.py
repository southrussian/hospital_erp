from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from models import *


def setup_view_departments_routes(app):
    @app.route('/view_departments')
    def view_departments():
        departments = Department.query.all()
        return render_template('view_departments.html', departments=departments)


def setup_add_department_routes(app):
    @app.route('/add_department', methods=['GET', 'POST'])
    def add_department():
        if request.method == 'POST':
            if not request.form.get('name'):
                flash("Name is required", "danger")
                return redirect(url_for('add_department'))

            name = request.form['name'].strip()

            department = Department(name=name)

            try:
                db.session.add(department)
                db.session.commit()
                flash("Department created!", "success")
                return redirect(url_for('view_departments'))
            except IntegrityError:
                db.session.rollback()
                flash("Department exists", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "danger")

        return render_template('add_department.html')  # Убрали doctors


def setup_edit_department_routes(app):
    @app.route('/edit_department/<int:department_id>', methods=['GET', 'POST'])
    def edit_department(department_id):
        department = Department.query.get_or_404(department_id)

        if request.method == 'POST':
            if not request.form.get('name'):
                flash("Name required", "danger")
                return redirect(url_for('edit_department', department_id=department_id))

            department.name = request.form['name'].strip()

            try:
                db.session.commit()
                flash("Updated!", "success")
                return redirect(url_for('view_departments'))
            except IntegrityError:
                db.session.rollback()
                flash("Name exists", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "danger")

        return render_template('edit_department.html', department=department)


def setup_delete_department_routes(app):
    @app.route('/delete_department/<int:department_id>', methods=['POST'])
    def delete_department(department_id):
        department = Department.query.get_or_404(department_id)

        try:
            # Если осталась связь с Doctor
            if hasattr(department, 'doctors') and department.doctors:
                flash("Delete doctors first", "danger")
                return redirect(url_for('view_departments'))

            db.session.delete(department)
            db.session.commit()
            flash("Deleted!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

        return redirect(url_for('view_departments'))
