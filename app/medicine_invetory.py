from flask import render_template, redirect, url_for, flash, request
from models import *


def view_medicine_inventory(app):
    @app.route('/view_medicine_inventory')
    def view_medicine_inventory():
        inventory = MedicineInventory.query.all()
        return render_template('view_medicine_inventory.html', inventory=inventory)


def add_medicine_inventory(app):
    @app.route('/add_medicine_inventory', methods=['GET', 'POST'])
    def add_medicine_inventory():
        medicines = Medicine.query.all()

        if request.method == 'POST':
            medicine_id = request.form['medicine_id']
            quantity = request.form['quantity']
            last_updated = request.form['last_updated']

            inventory = MedicineInventory(
                medicine_id=medicine_id,
                quantity=quantity,
                last_updated=last_updated
            )

            try:
                db.session.add(inventory)
                db.session.commit()
                flash('Инвентарь лекарств успешно добавлен!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('add_medicine_inventory'))

        return render_template('add_medicine_inventory.html', medicines=medicines)


def edit_medicine_inventory(app):
    @app.route('/edit_medicine_inventory/<int:inventory_id>', methods=['GET', 'POST'])
    def edit_medicine_inventory(inventory_id):
        inventory = MedicineInventory.query.get_or_404(inventory_id)
        medicines = Medicine.query.all()

        if request.method == 'POST':
            inventory.medicine_id = request.form['medicine_id']
            inventory.quantity = request.form['quantity']
            inventory.last_updated = request.form['last_updated']

            try:
                db.session.commit()
                flash('Инвентарь лекарств успешно обновлен!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Произошла ошибка: {e}', 'danger')

            return redirect(url_for('view_medicine_inventory'))

        return render_template('edit_medicine_inventory.html', medicines=medicines, inventory=inventory)


def delete_medicine_inventory(app):
    @app.route('/delete_medicine_inventory/<int:inventory_id>', methods=['POST'])
    def delete_inventory(inventory_id):
        inventory = MedicineInventory.query.get_or_404(inventory_id)
        try:
            db.session.delete(inventory)
            db.session.commit()
            flash("Doctor deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_medicine_inventory'))
