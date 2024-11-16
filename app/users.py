from models import *
from flask import render_template, redirect, url_for, flash, request, session


def register(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                flash('Пользователь с таким именем или email уже существует.', 'danger')
                return redirect(url_for('register'))

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')


def login(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.user_id
                flash('Вход выполнен успешно!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Неверное имя пользователя или пароль.', 'danger')

        return render_template('login.html')


def logout(app):
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('Вы вышли из системы.', 'info')
        return redirect(url_for('login'))


def view_users(app):
    @app.route('/view_users')
    def view_users():
        users = User.query.all()
        return render_template('view_users.html', users=users)
