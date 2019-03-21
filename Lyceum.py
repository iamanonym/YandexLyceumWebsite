from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, SelectField, TextAreaField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mYsEcReTkEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<Student {} {} {} {}>'.format(
            self.id, self.username, self.name, self.surname)


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(80), unique=False, nullable=False)
    code = db.Column(db.String(1000), unique=False, nullable=False)
    status = db.Column(db.String(50), unique=False, nullable=False)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('yandex_lyceum_student.id'),
                           nullable=False)

    def __repr__(self):
        return '<SolutionAttempt {} {} {}>'.format(
            self.id, self.task, self.status)


class LoginForm(FlaskForm):
    username = StringField('Введите логин', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class SubmitRegisterForm(FlaskForm):
    register = SubmitField('Регистрация')


class RegisterForm(FlaskForm):
    username = StringField('Введите Ваш логин', validators=[DataRequired()])
    password = PasswordField('Введите пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    name = StringField('Введите Ваше имя', validators=[DataRequired()])
    surname = StringField('Введите Вашу фамилию', validators=[DataRequired()])
    email = StringField('Введите Ваш email', validators=[DataRequired(), Email()])
    group = SelectField('Выберите вашу группу',
                        choices=[('1 группа, 2 год', '1 группа, 2 год'),
                                 ('2 группа, 2 год', '2 группа, 2 год'),
                                 ('1 группа, 1 год', '1 группа, 1 год')])
    submit = SubmitField('Зарегистрироваться')


class TaskForm(FlaskForm):
    text = TextAreaField('Решение')
    submit = SubmitField('Отправить')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form2 = SubmitRegisterForm()
    if form.validate_on_submit():
        return redirect("/index")
    if form2.validate_on_submit():
        return redirect('/register')
    return render_template('Login.html', title='Авторизация',
                           form=form, form2=form2)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Student(username=form.username.data,
                       password_hash=
                       generate_password_hash(form.password.data),
                       name=form.name.data, surname=form.surname.data,
                       email=form.email.data, group=form.group.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/index')
    return render_template('Register.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    form = TaskForm()
    return render_template('Task_page.html', title='Задача', form=form)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')
