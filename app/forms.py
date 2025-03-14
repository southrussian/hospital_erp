from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(message='Неверный формат email')])
    password = PasswordField('Пароль', validators=[InputRequired(),
                                                   Length(min=6, message='Пароль должен быть минимум 6 символов')])
