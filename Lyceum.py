from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, session, \
    url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, SelectField, TextAreaField, RadioField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo
import json
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mYsEcReTkEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

TASKS = [('''В алфавите племени мымба-ымба 31 буква. Каждое слово в языке
             состоит из 3 букв и читается одинаково в обе стороны.
             Каково максимальное количество слов в этом языке?''', '930'),
         ('''Катя наклеила на рулет тонкие поперечные кольца трёх разных 
             цветов. Если разрезать по серым кольцам, получится 15 кусков 
             рулета, если по синим — 57 кусков, а если по зеленым — 21 кусок. 
             Сколько кусков рулета получится, если разрезать по 
             кольцам всех трёх цветов?''', '91'),
         ('''Поверхность пруда постепенно закрывается вырастающими в нем 
             кувшинками. За каждый день покрытая кувшинками площадь 
             увеличивается вдвое. Вся поверхность пруда закрывается за 7 дней.
             За сколько дней четверть пруда зарастает кувшинками?''', '5'),
         ('''Гусеница прогрызает грушу диаметром 8 сантиметров насквозь за 
             20 секунд, вылезая снаружи полностью. Известно, что середину груши 
             она начинает грызть уже через 8 секунд после начала пути. 
             Какова длина гусеницы в сантиметрах?''', '2'),
         ('''Согласны ли Вы с этим следствием? 1. Все кошки - не собаки.
             2. Все собаки лают. Значит, все кошки не лают.''',
          'Не согласен')]
BOOK = {1: 'https://vk.com/doc7608079_448293932?'
           'hash=1adedc3d4302500693&dl=d46c3b3175fe3c7b46',
        2: 'https://vk.com/doc7608079_471689382?'
           'hash=f0a04cbc3f1c723542&dl=035031a390ac63eb85',
        3: 'https://vk.com/doc7608079_487953471?'
           'hash=030508d4371e0c9055&dl=9278a8c41509462672'}


class Tester:
    def __init__(self):
        self.started = False
        self.result = [None for number in range(5)]
        self.answers = [None for number in range(5)]

    def start(self):
        self.started = True
        self.result = [None for number in range(5)]
        self.answers = [None for number in range(5)]

    def stop(self):
        self.started = False

    def has_started(self):
        return self.started

    def add(self, ind, answer):
        if self.started:
            self.answers[ind] = answer
            self.result[ind] = TASKS[ind][1] == answer
            print(self.result[ind])
            print(TASKS[ind][1], answer, TASKS[ind][1] == answer)

    def get_result(self):
        return self.result.count(True)

    def get_list(self):
        return self.result

    def get_answers(self):
        return self.answers


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


class TestForm1(FlaskForm):
    task = StringField(TASKS[0][0], validators=[DataRequired()])
    submit = SubmitField('Далее')


class TestForm2(FlaskForm):
    task = StringField(TASKS[1][0], validators=[DataRequired()])
    submit = SubmitField('Далее')


class TestForm3(FlaskForm):
    task = StringField(TASKS[2][0], validators=[DataRequired()])
    submit = SubmitField('Далее')


class TestForm4(FlaskForm):
    task = StringField(TASKS[3][0], validators=[DataRequired()])
    submit = SubmitField('Далее')


class TestForm5(FlaskForm):
    task = RadioField(TASKS[4][0], validators=[DataRequired()],
                      choices=[('Согласен', 'Согласен'),
                               ('Не согласен', 'Не согласен')])
    submit = SubmitField('Далее')


db.create_all()
tester = Tester()


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


@app.route('/place', methods=['GET'])
@app.route('/place/', methods=['GET'])
def place():
    return render_template('Place.html', title='Местоположение',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/teachers', methods=['GET'])
@app.route('/teachers/', methods=['GET'])
def teachers():
    return render_template('Teachers.html', title='Преподаватели',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/coordinator', methods=['GET'])
@app.route('/coordinator/', methods=['GET'])
def coordinator():
    return render_template('Coordinator.html', title='Координатор',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/abitu', methods=['GET'])
@app.route('/abitu/', methods=['GET'])
def abitu():
    return render_template('Abitu.html', title='Абитуриентам',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/test', methods=['GET'])
@app.route('/test/', methods=['GET'])
def test():
    return render_template('Test.html', title='Пробное тестирование')


@app.route('/test/<int:task_id>', methods=['GET', 'POST'])
@app.route('/test/<int:task_id>/', methods=['GET', 'POST'])
def task_of_test(task_id):
    if 1 <= task_id <= 5:
        if task_id == 1:
            tester.start()
        task_dict = {1: TestForm1(), 2: TestForm2(), 3: TestForm3(),
                     4: TestForm4(), 5: TestForm5()}
        form = task_dict[task_id]
        if form.validate_on_submit():
            tester.add(task_id - 1, form.task.data)
            if task_id != 5:
                return redirect('/test/{}'.format(task_id + 1))
            else:
                return redirect('/test/result')
        return render_template('Test_task.html', title='Пробное тестирование',
                               form=form, task_id=task_id)
    else:
        abort(404, message='Task not found')


@app.route('/test/result', methods=['GET'])
@app.route('/test/result/', methods=['GET'])
def test_result():
    if tester.has_started():
        tester.stop()
        return render_template('Test_result.html',
                               title='Пробное тестирование',
                               number=tester.get_result(),
                               res_list=tester.get_list(),
                               tasks=TASKS, answers=tester.get_answers())
    else:
        abort(404, message='Страница не найдена')


@app.route('/schedule', methods=['GET', 'POST'])
@app.route('/schedule/', methods=['GET', 'POST'])
def schedule():
    return render_template('Schedule.html', title='Абитуриентам',
                           src1=url_for('static', filename='img/d.png'),
                           src2=url_for('static', filename='img/d.png'),
                           src3=url_for('static', filename='img/d.png'))


@app.route('/studentbook/<int:book_id>/', methods=['GET'])
@app.route('/studentbook/<int:book_id>', methods=['GET'])
def studentbook(book_id):
    if not 1 <= book_id <= 3:
        abort(404, message='Книга не найдена')
    else:
        return render_template('Studentbook.html', title='Абитуриентам',
                               src1=url_for('static', filename='img/d.png'),
                               src2=url_for('static', filename='img/d.png'),
                               src3=url_for('static', filename='img/d.png'),
                               src=BOOK[book_id])


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
