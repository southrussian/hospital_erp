from flask import render_template, redirect, url_for, flash, request
from models import *
from sqlalchemy.exc import IntegrityError


def setup_view_medicine_routes(app):
    @app.route('/view_medicine')
    def view_medicine():
        medicines = Medicine.query.all()
        return render_template('view_medicines.html', medicines=medicines)


def setup_add_medicine_routes(app):
    @app.route('/add_medicine', methods=['GET', 'POST'])
    def add_medicine():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            dosage_form = request.form.get('dosage_form', '').strip()
            atc_code = request.form.get('atc_code', '').strip()[:10]  # Обрезаем до 10 символов

            errors = []
            if not name:
                errors.append("Название лекарства обязательно для заполнения")
            if len(atc_code) > 10:
                errors.append("ATC-код не должен превышать 10 символов")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('add_medicine.html',
                                       name=name,
                                       description=description,
                                       dosage_form=dosage_form,
                                       atc_code=atc_code)

            try:
                medicine = Medicine(
                    name=name,
                    description=description or None,  # Если пустая строка - сохраняем как NULL
                    dosage_form=dosage_form or None,
                    atc_code=atc_code or None
                )
                db.session.add(medicine)
                db.session.commit()
                flash('Лекарство успешно добавлено!', 'success')
                return redirect(url_for('view_medicine'))

            except IntegrityError as e:
                db.session.rollback()
                if 'unique constraint' in str(e).lower():
                    flash('Лекарство с таким названием уже существует', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')

        return render_template('add_medicine.html')


def setup_edit_medicine_routes(app):
    @app.route('/edit_medicine/<int:medicine_id>', methods=['GET', 'POST'])
    def edit_medicine(medicine_id):
        medicine = Medicine.query.get_or_404(medicine_id)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            dosage_form = request.form.get('dosage_form', '').strip()
            atc_code = request.form.get('atc_code', '').strip()[:10]

            errors = []
            if not name:
                errors.append("Название лекарства обязательно для заполнения")
            if len(atc_code) > 10:
                errors.append("ATC-код не должен превышать 10 символов")

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('edit_medicine.html',
                                       medicine=medicine,
                                       name=name,
                                       description=description,
                                       dosage_form=dosage_form,
                                       atc_code=atc_code)

            try:
                medicine.name = name
                medicine.description = description or None
                medicine.dosage_form = dosage_form or None
                medicine.atc_code = atc_code or None

                db.session.commit()
                flash('Лекарство успешно обновлено!', 'success')
                return redirect(url_for('view_medicine'))

            except IntegrityError as e:
                db.session.rollback()
                if 'unique constraint' in str(e).lower():
                    flash('Лекарство с таким названием уже существует', 'danger')
                else:
                    flash(f'Ошибка целостности данных: {e}', 'danger')
                return render_template('edit_medicine.html', medicine=medicine)

            except Exception as e:
                db.session.rollback()
                flash(f'Непредвиденная ошибка: {e}', 'danger')
                return render_template('edit_medicine.html', medicine=medicine)

        return render_template('edit_medicine.html', medicine=medicine)


def setup_delete_medicine_routes(app):
    @app.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
    def delete_medicine(medicine_id):
        try:
            medicine = Medicine.query.get_or_404(medicine_id)
            db.session.delete(medicine)
            db.session.commit()
            flash("Лекарство успешно удалено!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Невозможно удалить лекарство, так как оно связано с другими записями", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка: {e}", "danger")
        return redirect(url_for('view_medicine'))
