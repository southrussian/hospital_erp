from flask import render_template, redirect, url_for, flash, request
from .models import *


def view_medicine(app):
    @app.route('/view_medicine')
    def view_medicine():
        medicines = Medicine.query.all()
        return render_template('view_medicines.html', medicines=medicines)


def add_medicine(app):
    @app.route('/add_medicine', methods=['GET', 'POST'])
    def add_medicine():
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            dosage_form = request.form['dosage_form']

            medicine = Medicine(
                name=name,
                description=description,
                dosage_form=dosage_form
            )

            try:
                db.session.add(medicine)
                db.session.commit()
                flash('Лекарство успешно добавлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('add_medicine'))

        return render_template('add_medicine.html')


def edit_medicine(app):
    @app.route('/edit_medicine/<int:medicine_id>', methods=['GET', 'POST'])
    def edit_medicine(medicine_id):
        medicine = Medicine.query.get_or_404(medicine_id)
        if request.method == 'POST':
            medicine.name = request.form['name']
            medicine.description = request.form['description']
            medicine.dosage_form = request.form['dosage_form']

            try:
                db.session.commit()
                flash('Лекарство успешно обновлено!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('view_medicine'))

        return render_template('edit_medicine.html', medicine=medicine)


def delete_medicine(app):
    @app.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
    def delete_medicine(medicine_id):
        medicine = Medicine.query.get_or_404(medicine_id)
        try:
            db.session.delete(medicine)
            db.session.commit()
            flash("Medicine deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_medicine'))
