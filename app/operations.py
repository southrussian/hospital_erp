from flask import render_template, redirect, url_for, flash, request
from .models import *


def view_operations(app):
    @app.route('/view_operations')
    def view_operations():
        operations = Operation.query.all()
        return render_template('view_operations.html', operations=operations)


def add_operation(app):
    @app.route('/add_operation', methods=['GET', 'POST'])
    def add_operation():
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            patient_id = request.form['patient_id']
            doctor_id = request.form['doctor_id']
            operation_type = request.form['operation_type']
            operation_date = request.form['operation_date']
            duration = request.form['duration']
            outcome = request.form['outcome']

            operation = Operation(
                patient_id=patient_id,
                doctor_id=doctor_id,
                operation_type=operation_type,
                operation_date=operation_date,
                duration=duration,
                outcome=outcome
            )

            try:
                db.session.add(operation)
                db.session.commit()
                flash('Операция успешно добавлена!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('add_operation'))

        return render_template('add_operation.html', patients=patients, doctors=doctors)


def edit_operation(app):
    @app.route('/edit_operation/<int:operation_id>', methods=['GET', 'POST'])
    def edit_operation(operation_id):
        operation = Operation.query.get_or_404(operation_id)
        patients = Patient.query.all()
        doctors = Doctor.query.all()

        if request.method == 'POST':
            operation.patient_id = request.form['patient_id']
            operation.doctor_id = request.form['doctor_id']
            operation.operation_type = request.form['operation_type']
            operation.operation_date = request.form['operation_date']
            operation.duration = request.form['duration']
            operation.outcome = request.form['outcome']

            try:
                db.session.commit()
                flash('Операция успешно добавлена!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('view_operations'))

        return render_template('edit_operation.html', patients=patients, doctors=doctors,
                               operation=operation)


def delete_operation(app):
    @app.route('/delete_operation/<int:operation_id>', methods=['POST'])
    def delete_operation(operation_id):
        operation = Operation.query.get_or_404(operation_id)
        try:
            db.session.delete(operation)
            db.session.commit()
            flash("Operation deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_operations'))
