from flask import render_template, redirect, url_for, flash, request
from models import *
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def setup_view_medicine_inventory_routes(app):
    @app.route('/view_medicine_inventory')
    def view_medicine_inventory():
        inventory = MedicineInventory.query.all()
        return render_template('view_medicine_inventory.html', inventory=inventory)


def setup_add_medicine_inventory_routes(app):
    @app.route('/add_medicine_inventory', methods=['GET', 'POST'])
    def add_medicine_inventory():
        medicines = Medicine.query.all()

        if request.method == 'POST':
            medicine_id = request.form.get('medicine_id', '').strip()
            quantity = request.form.get('quantity', '').strip()
            expiration_date_str = request.form.get('expiration_date', '').strip()
            last_updated = datetime.now()

            errors = []

            # Валидация medicine_id
            if not medicine_id:
                errors.append("Необходимо выбрать лекарство")
            else:
                try:
                    medicine_id = int(medicine_id)
                    if not Medicine.query.get(medicine_id):
                        errors.append("Указанное лекарство не существует")
                except ValueError:
                    errors.append("Некорректный ID лекарства")

            # Валидация quantity
            try:
                quantity = int(quantity)
                if quantity < 0:
                    errors.append("Количество не может быть отрицательным")
            except ValueError:
                errors.append("Некорректное значение количества")

            # Валидация expiration_date
            expiration_date = None
            if expiration_date_str:
                try:
                    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                    if expiration_date < datetime.now().date():
                        errors.append("Дата истечения срока не может быть в прошлом")
                except ValueError:
                    errors.append("Некорректный формат даты (используйте ГГГГ-ММ-ДД)")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('add_medicine_inventory.html',
                                       medicines=medicines,
                                       selected_medicine_id=medicine_id,
                                       quantity=quantity,
                                       expiration_date=expiration_date_str)

            try:
                inventory = MedicineInventory(
                    medicine_id=medicine_id,
                    quantity=quantity,
                    expiration_date=expiration_date,
                    last_updated=last_updated
                )

                db.session.add(inventory)
                db.session.commit()
                flash('Запись инвентаря успешно добавлена!', 'success')
                return redirect(url_for('view_medicine_inventory'))

            except IntegrityError as e:
                db.session.rollback()
                if 'check_quantity_positive' in str(e):
                    flash('Количество не может быть отрицательным', 'danger')
                elif 'foreign key constraint' in str(e):
                    flash('Выбрано несуществующее лекарство', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('add_medicine_inventory.html', medicines=medicines)


def setup_edit_medicine_inventory_routes(app):
    @app.route('/edit_medicine_inventory/<int:inventory_id>', methods=['GET', 'POST'])
    def edit_medicine_inventory(inventory_id):
        inventory = MedicineInventory.query.get_or_404(inventory_id)
        medicines = Medicine.query.all()

        if request.method == 'POST':
            medicine_id = request.form.get('medicine_id', '').strip()
            quantity = request.form.get('quantity', '').strip()
            expiration_date_str = request.form.get('expiration_date', '').strip()

            errors = []

            if not medicine_id:
                errors.append("Необходимо выбрать лекарство")
            else:
                try:
                    medicine_id = int(medicine_id)
                    if not Medicine.query.get(medicine_id):
                        errors.append("Указанное лекарство не существует")
                except ValueError:
                    errors.append("Некорректный ID лекарства")

            try:
                quantity = int(quantity)
                if quantity < 0:
                    errors.append("Количество не может быть отрицательным")
            except ValueError:
                errors.append("Некорректное значение количества")

            expiration_date = None
            if expiration_date_str:
                try:
                    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date()
                    if expiration_date < datetime.now().date():
                        errors.append("Дата истечения срока не может быть в прошлом")
                except ValueError:
                    errors.append("Некорректный формат даты (используйте ГГГГ-ММ-ДД)")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('edit_medicine_inventory.html',
                                       inventory=inventory,
                                       medicines=medicines,
                                       selected_medicine_id=medicine_id,
                                       quantity=quantity,
                                       expiration_date=expiration_date_str)

            try:
                inventory.medicine_id = medicine_id
                inventory.quantity = quantity
                inventory.expiration_date = expiration_date
                inventory.last_updated = datetime.now()

                db.session.commit()
                flash('Запись инвентаря успешно обновлена!', 'success')
                return redirect(url_for('view_medicine_inventory'))

            except IntegrityError as e:
                db.session.rollback()
                if 'check_quantity_positive' in str(e):
                    flash('Количество не может быть отрицательным', 'danger')
                elif 'foreign key constraint' in str(e):
                    flash('Выбрано несуществующее лекарство', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')
                return render_template('edit_medicine_inventory.html',
                                       inventory=inventory,
                                       medicines=medicines)

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')
                return render_template('edit_medicine_inventory.html',
                                       inventory=inventory,
                                       medicines=medicines)

        return render_template('edit_medicine_inventory.html',
                               inventory=inventory,
                               medicines=medicines)


def setup_delete_medicine_inventory_routes(app):
    @app.route('/delete_medicine_inventory/<int:inventory_id>', methods=['POST'])
    def delete_medicine_inventory(inventory_id):
        try:
            inventory = MedicineInventory.query.get_or_404(inventory_id)
            db.session.delete(inventory)
            db.session.commit()
            flash("Запись инвентаря успешно удалена!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Невозможно удалить запись, так как она связана с другими данными", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {e}", "danger")
        return redirect(url_for('view_medicine_inventory'))
