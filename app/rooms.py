from flask import render_template, redirect, url_for, flash, request
from models import *


def view_rooms(app):
    @app.route('/view_rooms')
    def view_rooms():
        rooms = Room.query.all()
        return render_template('view_rooms.html', rooms=rooms)


def add_room(app):
    @app.route('/add_room', methods=['GET', 'POST'])
    def add_room():
        departments = Department.query.all()

        if request.method == 'POST':
            room_number = request.form['room_number']
            department_id = request.form['department_id']
            capacity = request.form['capacity']

            room = Room(room_number=room_number, department_id=department_id, capacity=capacity)

            try:
                db.session.add(room)
                db.session.commit()
                flash("Room added successfully!", "success")
                return redirect(url_for('add_room'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")

        return render_template('add_room.html', departments=departments)


def edit_room(app):
    @app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
    def edit_room(room_id):
        room = Room.query.get_or_404(room_id)
        departments = Department.query.all()

        if request.method == 'POST':
            room.room_number = request.form['room_number']
            room.department_id = request.form['department_id']
            room.capacity = request.form['capacity']

            try:
                db.session.commit()
                flash("Room updated successfully!", "success")
                return redirect(url_for('view_rooms'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "danger")

        return render_template('edit_room.html', departments=departments, room=room)


def delete_room(app):
    @app.route('/delete_room/<int:room_id>', methods=['POST'])
    def delete_room(room_id):
        room = Room.query.get_or_404(room_id)

        # Проверка, есть ли койки в палате
        if len(room.beds) > 0:
            flash('Невозможно удалить палату с койками!', 'danger')
            return redirect(url_for('view_rooms'))

        try:
            db.session.delete(room)
            db.session.commit()
            flash('Палата успешно удалена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {e}', 'danger')

        return redirect(url_for('view_rooms'))
