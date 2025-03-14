from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from models import *

# Допустимые типы палат
ROOM_TYPES = ['общая', 'индивидуальная', 'полулюкс', 'послеоперационная', 'изолятор']


def setup_view_rooms_routes(app):
    @app.route('/view_rooms')
    def view_rooms():
        try:
            # Получаем палаты с информацией об отделениях
            rooms = Room.query.options(db.joinedload(Room.department)).all()
            return render_template('view_rooms.html',
                                   rooms=rooms,
                                   ROOM_TYPES=ROOM_TYPES)
        except Exception as e:
            flash(f"Ошибка при загрузке данных: {str(e)}", "danger")
            return redirect(url_for('index'))


def setup_add_room_routes(app):
    @app.route('/add_room', methods=['GET', 'POST'])
    def add_room():
        departments = Department.query.all()

        if request.method == 'POST':
            try:
                # Валидация обязательных полей
                required_fields = ['room_number', 'department_id', 'capacity']
                for field in required_fields:
                    if not request.form.get(field):
                        flash(f"Поле '{field}' обязательно для заполнения", "danger")
                        return redirect(url_for('add_room'))

                room_number = request.form['room_number'].strip()
                department_id = int(request.form['department_id'])
                capacity = int(request.form['capacity'])
                room_type = request.form.get('room_type', 'общая')

                # Проверка уникальности номера палаты
                if Room.query.filter_by(room_number=room_number).first():
                    flash("Палата с таким номером уже существует", "danger")
                    return redirect(url_for('add_room'))

                # Валидация вместимости
                if capacity <= 0:
                    flash("Вместимость должна быть положительным числом", "danger")
                    return redirect(url_for('add_room'))

                # Создание палаты
                room = Room(
                    room_number=room_number,
                    department_id=department_id,
                    capacity=capacity,
                    room_type=room_type
                )

                db.session.add(room)
                db.session.commit()
                flash("Палата успешно добавлена!", "success")
                return redirect(url_for('view_rooms'))

            except ValueError:
                db.session.rollback()
                flash("Некорректные данные в форме", "danger")
            except IntegrityError:
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при добавлении: {str(e)}", "danger")

        return render_template('add_room.html',
                               departments=departments,
                               ROOM_TYPES=ROOM_TYPES)


def setup_edit_room_routes(app):
    @app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
    def edit_room(room_id):
        room = Room.query.get_or_404(room_id)
        departments = Department.query.all()

        if request.method == 'POST':
            try:
                # Валидация данных
                new_room_number = request.form['room_number'].strip()
                if new_room_number != room.room_number:
                    if Room.query.filter_by(room_number=new_room_number).first():
                        flash("Палата с таким номером уже существует", "danger")
                        return redirect(url_for('edit_room', room_id=room_id))

                room.room_number = new_room_number
                room.department_id = int(request.form['department_id'])
                room.capacity = int(request.form['capacity'])
                room.room_type = request.form.get('room_type', 'общая')

                if room.capacity <= 0:
                    flash("Вместимость должна быть положительным числом", "danger")
                    return redirect(url_for('edit_room', room_id=room_id))

                db.session.commit()
                flash("Данные палаты обновлены!", "success")
                return redirect(url_for('view_rooms'))

            except ValueError:
                db.session.rollback()
                flash("Некорректные данные в форме", "danger")
            except IntegrityError:
                db.session.rollback()
                flash("Ошибка целостности данных", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при обновлении: {str(e)}", "danger")

        return render_template('edit_room.html',
                               room=room,
                               departments=departments,
                               ROOM_TYPES=ROOM_TYPES)


def setup_delete_room_routes(app):
    @app.route('/delete_room/<int:room_id>', methods=['POST'])
    def delete_room(room_id):
        room = Room.query.get_or_404(room_id)
        try:
            # Проверка связанных коек
            if room.beds:
                flash("Невозможно удалить палату с привязанными койками", "danger")
                return redirect(url_for('view_rooms'))

            db.session.delete(room)
            db.session.commit()
            flash("Палата успешно удалена!", "success")
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Ошибка целостности данных: {str(e)}", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении: {str(e)}", "danger")

        return redirect(url_for('view_rooms'))
