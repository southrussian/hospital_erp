from flask import Flask, render_template, redirect, url_for, flash, session
import logging
from logging.handlers import RotatingFileHandler
from models import *
from flask_migrate import Migrate
from routes import setup_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5896@localhost:5432/hospital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'oxxxymiron'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
file_handler = RotatingFileHandler('hospital_app.log', maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

app.logger.info("Приложение Flask запущено.")

db.init_app(app)
migrate = Migrate(app, db)

setup_routes(app)


@app.route('/')
def dashboard():
    try:
        if 'user_id' not in session:
            flash('Пожалуйста, войдите для доступа к этой странице.', 'warning')
            return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(e)
    app.logger.info(f"Доступ к панели управления пользователем ID: {session['user_id']}.")
    return render_template('dashboard.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5050)
