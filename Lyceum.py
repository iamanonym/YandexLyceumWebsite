from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, session, \
    url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, SelectField, TextAreaField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo
import json
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

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(80), unique=False, nullable=False)
    code = db.Column(db.String(1000), unique=False, nullable=False)
    status = db.Column(db.String(50), unique=False, nullable=False)
    student_id = db.Column(db.Integer,
                           db.ForeignKey('student.id'),
                           nullable=False)

    def __repr__(self):
        return '<SolutionAttempt {} {} {}>'.format(
            self.id, self.task, self.status)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(500))
    text = db.Column(db.String(10000))

    def __repr__(self):
        return '<News {} {}>'.format(self.id, self.title)


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


db.create_all()


@app.errorhandler(404)
def page_not_found(error):
    return render_template('Error404.html', title='Страница не найдена'), 404


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form2 = SubmitRegisterForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            pass
        else:
            return redirect("/index")
    if form2.validate_on_submit():
        return redirect('/register')
    return render_template('Login.html', title='Авторизация',
                           form=form, form2=form2)


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
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
        session['username'] = form.username.data
        session['user_id'] = user.id
        return redirect('/index')
    return render_template('Register.html', title='Регистрация', form=form)


@app.route('/logout', methods=['GET'])
@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    form = TaskForm()
    return render_template('Task_page.html', title='Задача', form=form)


@app.route('/', methods=['GET'])
@app.route('/news', methods=['GET'])
@app.route('/news/', methods=['GET'])
def main():
    news = Article.query.all()[:10]
    return render_template('News.html', title='Яндекс Лицей. Магнитогорск',
                           news=news,
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/news/<int:news_id>', methods=['GET'])
@app.route('/news/<int:news_id>/', methods=['GET'])
def get_article(news_id):
    article = Article.query.filter_by(id=news_id).first()
    if article is not None:
        with open(article.text) as file:
            text = file.read()
        return render_template('Article.html', title=article.title,
                               article=article, text=text,
                               src1=url_for('static', filename='img/d.png'),
                               src2=url_for('static', filename='img/d.png'),
                               src3=url_for('static', filename='img/d.png'))
    else:
        abort(404, message='Article not found')


@app.route('/place')
@app.route('/place/')
def place():
    return render_template('Place.html', title='Местоположение',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/teachers')
@app.route('/teachers/')
def teachers():
    return render_template('Teachers.html', title='Преподаватели',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/coordinator')
@app.route('/coordinator/')
def coordinator():
    return render_template('Coordinator.html', title='Координатор',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


if __name__ == '__main__':
    with open('News.json') as file:
        news = json.loads(file.read())
        for article in news:
            temp = Article.query.filter_by(title=news[article]['title']).first()
            if temp is None:
                article_obj = Article(title=news[article]['title'],
                                      content=news[article]['content'],
                                      text=news[article]['text'])
                db.session.add(article_obj)
                db.session.commit()
    app.run(port=8000, host='127.0.0.1')
