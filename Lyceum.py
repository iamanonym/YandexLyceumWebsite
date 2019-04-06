from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, SelectField, TextAreaField, RadioField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, \
    EqualTo, ValidationError, Length
import json
import sys
from flask_restful import abort


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mYsEcReTkEy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Lyceum.db'
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
PROGRAM = {1: 'https://docviewer.yandex.ru/view/70851904/?*=7sebe5u%2F%'
              '2Bvmaknm4LCE9BXEppJp7InVybCI6InlhLWRpc2stcHVibGljOi8vYTR'
              'OeUQ1L01FVnlnWHFDTTBqUXFwNzBYbEhGOFhxTksxbHNyUU43Q08ydGVw'
              'WjlOclNJWnhwYlZ0dlBCcTIzNHRGUDZnd2JqdnRhYWZUcHRjdWE0U0E9P'
              'SIsInRpdGxlIjoiVGhlX2Jhc2ljc19vZl9wcm9ncmFtbWluZ19pbl9QeX'
              'Rob25fMTQ0X2hvdXJzLnBkZiIsInVpZCI6IjcwODUxOTA0IiwieXUiOiI'
              '1NDUyNDgzNDcxNTUwMzg4NDY5Iiwibm9pZnJhbWUiOmZhbHNlLCJ0cyI6'
              'MTU1Mzc1Njg0Mzk1M30%3D',
           2: 'https://docviewer.yandex.ru/view/70851904/?*=9D6E0XNwTSZG'
              'dY0AoQl4Q6B%2Bq8p7InVybCI6InlhLWRpc2stcHVibGljOi8vYTROeUQ'
              '1L01FVnlnWHFDTTBqUXFweVgvRkt6bVgvSU84VTBKa2JtTlBDd1MwYS9G'
              'WEZRUUlhWFBrNDByNlQ5cUVrSTBlMGl0L1A1M0pqQktkcmpGdWc9PSIsI'
              'nRpdGxlIjoiRnVuZGFtZW50YWxzX29mX2luZHVzdHJpYWxfcHJvZ3JhbW'
              '1pbmdfMTY4X2hvdXJzLnBkZiIsInVpZCI6IjcwODUxOTA0IiwieXUiOiI'
              '1NDUyNDgzNDcxNTUwMzg4NDY5Iiwibm9pZnJhbWUiOmZhbHNlLCJ0cyI6'
              'MTU1Mzc1NjkyMjc1NX0%3D'}


def check_password(password):  # Проверка пароля
    if password.isdigit() or password.isalpha():
        return 'Пароль состоит из символов одного вида'
    elif set(password).intersection({',', '.', '!', '?', '/', '\\',
                                     ';', '(', ')', '&', '[', ']',
                                     '<', '>', '*', '|', ':', '"'}):
        return 'Недопустимые символы в пароле'
    else:
        return 'OK'


def add_solution(code, status, user, task):  # Добавление решения в базу
    solution = Solution(code=code, status=status,
                        student_id=user.id, task_id=task.id)
    user.Solutions.append(solution)
    task.Solutions.append(solution)
    db.session.add(solution)
    db.session.commit()


def fill_news():  # Добавление новостей в базу
    with open('static/text/News.json') as file:
        news = json.loads(file.read())
        for article in news:
            temp = \
                Article.query.filter_by(title=news[article]['title']).first()
            if temp is None:  # Проверка наличия новости в базе
                article_obj = Article(title=news[article]['title'],
                                      content=news[article]['content'],
                                      text=news[article]['text'])
                db.session.add(article_obj)
                db.session.commit()


def fill_tasks():  # Добавление задач в базу
    with open('static/text/Tasks.json') as file:
        tasks = json.loads(file.read())
        for task in tasks:
            temp = Task.query.filter_by(title=tasks[task]['title']).first()
            if temp is None:  # Проверка наличия задачи в базе
                task_obj = Task(title=tasks[task]['title'],
                                condition=tasks[task]['condition'],
                                handheld=bool(int(tasks[task]['handheld'])))
                db.session.add(task_obj)
                db.session.commit()


def check_task(task_id, code):  # Проверка решения
    res, solve, inputs = [], [], []
    with open('static/text/input{}.txt'.format(task_id)) as file:
        for line in file.readlines():
            inputs.append(line.strip())
        file.close()
    with open('static/text/res{}.txt'.format(task_id)) as file2:
        for line in file2.readlines():
            solve.append(line.rstrip())
        file2.close()
    for number in range(3):
        input_file = open('static/text/input_temp.txt', 'w')
        input_file.write(inputs[number])
        input_file.close()
        temp = code if code.endswith('\n') else code + \
            '\n' + "sys.stdout = stdout\nfile1.close()\nfile2.close()\n"
        code2 = \
            "file1 = open('static/text/input_temp.txt')\n" \
            "file2 = open('static/text/output_temp.txt', 'w')\n" \
            "stdout = sys.stdout\nsys.stdin = file1\n" \
            "sys.stdout = file2\n" + temp
        try:
            exec(code2)
        except Exception:
            return False
        with open('static/text/output_temp.txt'.format(task_id)) as file:
            res.append(file.read().rstrip())  # Добавление результата в список
            file.close()
    return res == solve


def create_teacher():  # Добавление учителя в базу
    user1 = Student.query.filter_by(username='teacher1').first()
    if user1 is None:
        teacher = Student(username='teacher1',
                          password_hash=generate_password_hash('teacher1'),
                          name='Константин', surname='Проценко',
                          email='protsenko@lyceum.yaconnect.com',
                          group='-', teacher=True)
        db.session.add(teacher)
        db.session.commit()


class Tester:  # Класс, следящий за прохождением теста абитуриента
    def __init__(self):
        self.started = False
        self.result = [None for _ in range(5)]
        self.answers = [None for _ in range(5)]

    def start(self):  # Начать тест
        self.started = True
        self.result = [None for _ in range(5)]
        self.answers = [None for _ in range(5)]

    def stop(self):  # Закончить тест
        self.started = False

    def has_started(self):
        return self.started

    def add(self, ind, answer):  # Добавить ответ
        if self.started:
            self.answers[ind] = answer
            self.result[ind] = TASKS[ind][1] == answer

    def get_result(self):
        return self.result.count(True)

    def get_list(self):
        return self.result

    def get_answers(self):
        return self.answers


class Student(db.Model):  # Класс пользователя
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group = db.Column(db.String(80), unique=False, nullable=False)
    teacher = db.Column(db.Boolean, unique=False, nullable=False)

    def __repr__(self):
        return '<Student {} {} {} {}>'.format(
            self.id, self.username, self.name, self.surname)

    def check_password(self, password):  # Проверка пароля
        return check_password_hash(self.password_hash, password)


class Task(db.Model):  # Класс задачи
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    condition = db.Column(db.String(80), unique=False, nullable=False)
    handheld = db.Column(db.Boolean, unique=False, nullable=False)

    def __repr__(self):
        return '<Task {} {}>'.format(self.id, self.title)


class Solution(db.Model):  # Класс решения
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(1000), unique=False, nullable=False)
    status = db.Column(db.String(50), unique=False, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'),
                           nullable=False)
    student = db.relationship('Student',
                              backref=db.backref('Solutions', lazy=True))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                        nullable=False)
    task = db.relationship('Task', backref=db.backref('Solutions', lazy=True))

    def __repr__(self):
        return '<Solution {} {} {}>'.format(self.id, self.task, self.status)


class Article(db.Model):  # Класс новости
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(500))
    text = db.Column(db.String(10000))

    def __repr__(self):
        return '<News {} {}>'.format(self.id, self.title)


class LoginForm(FlaskForm):  # Форма авторизации
    username = StringField('Введите логин',
                           validators=[DataRequired('Заполните это поле')])
    password = \
        PasswordField('Введите пароль',
                      validators=[DataRequired('Заполните это поле')])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):  # Форма регистрации
    username = \
        StringField('Введите Ваш логин',
                    validators=[DataRequired(message='Заполните это поле'),
                                Length(min=6, max=10,
                                       message='Неправильная длина')])
    password = \
        PasswordField('Введите пароль',
                      validators=[DataRequired(message='Заполните это поле'),
                                  Length(min=6, max=10,
                                         message='Неправильная длина')])
    password2 = \
        PasswordField('Повторите пароль',
                      validators=[DataRequired(message='Заполните это поле'),
                                  EqualTo('password', 'Пароли не совпадают')])
    name = \
        StringField('Введите Ваше имя',
                    validators=[DataRequired(message='Заполните это поле')])
    surname = \
        StringField('Введите Вашу фамилию',
                    validators=[DataRequired(message='Заполните это поле')])
    email = \
        StringField('Введите Ваш email',
                    validators=[DataRequired(message='Заполните это поле'),
                                Email(message='Неправильный адрес почты')])
    group = SelectField('Выберите Вашу группу',
                        choices=[('1 год 1 группа', '1 год 1 группа'),
                                 ('2 год 1 группа', '2 год 1 группа'),
                                 ('2 год 2 группа', '2 год 2 группа')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):  # Проверка, занят ли логин
        student = Student.query.filter_by(username=username.data).first()
        if student is not None:
            raise ValidationError('Данный логин уже занят')

    def validate_password(self, password):  # Проверка, занят ли пароль
        check = check_password(password.data)
        if check is not 'OK':
            raise ValidationError(check)

    def validate_email(self, email):  # Проверка, занята ли почта
        student = Student.query.filter_by(email=email.data).first()
        if student is not None:
            raise ValidationError('Данный e-mail уже занят')


class TaskForm(FlaskForm):
    text = \
        TextAreaField('Решение',
                      validators=[DataRequired(message='Необходимо ввести '
                                                       'код решения')])
    submit = SubmitField('Отправить')

    def validate_text(self, text):
        for word in ['while', 'for', 'def', 'import', 'open', 'os']:
            if word in text.data:
                raise ValidationError('Недопустимое слово '
                                      'в решении: {}'.format(word))


class TestForm(FlaskForm):  # Форма вопроса теста со свободным ответом
    task = StringField(validators=[DataRequired()])
    submit = SubmitField('Далее')


class RadioTestForm(FlaskForm):  # Форма вопроса теста с выбором ответа
    task = RadioField(validators=[DataRequired()],
                      choices=[('Согласен', 'Согласен'),
                               ('Не согласен', 'Не согласен')])
    submit = SubmitField('Далее')


db.create_all()  # Создаем все сущности в базе
tester = Tester()


@app.errorhandler(403)  # Отработка ошибки 403
def page_not_found(error):
    return render_template('Error.html',
                           title='Страница не доступна',
                           error_code=403), 403


@app.errorhandler(404)  # Отработка ошибки 404
def page_not_found(error):
    return render_template('Error.html', title='Страница не найдена',
                           error_code=404), 404


@app.errorhandler(500)  # Отработка ошибки 500
def error_in_program(error):
    return render_template('Error.html', title='Ошибка во время выполнения',
                           error_code=500), 500


@app.route('/login', methods=['GET', 'POST'])  # Страница авторизации
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            abort(403, message='Неверный логин или пароль')
        else:
            session.pop('username', 0)
            session.pop('user_id', 0)
            session['username'] = user.username
            session['user_id'] = user.id
            if user.teacher:
                return redirect('/teacher_page')
            else:
                return redirect("/index")
    return render_template('Login.html', title='Авторизация',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])  # Страница регистрации
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = \
            Student(username=form.username.data,
                    password_hash=generate_password_hash(form.password.data),
                    name=form.name.data, surname=form.surname.data,
                    group=form.group.data, email=form.email.data,
                    teacher=False)
        db.session.add(user)
        db.session.commit()
        session.pop('username', 0)
        session.pop('user_id', 0)
        session['username'] = form.username.data
        session['user_id'] = user.id
        return redirect('/index')
    return render_template('Register.html', title='Регистрация', form=form)


@app.route('/logout', methods=['GET'])  # Выход из аккаунта
@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/index', methods=['GET', 'POST'])  # Страница c навигацией задач
@app.route('/index/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/login')
    user = Student.query.filter_by(username=session['username']).first()
    if not user:
        return redirect('/login')
    if user.teacher:
        return redirect('/teacher_page')
    tasks = Task.query.all()
    sols = []
    for task in tasks:
        temp = Solution.query.filter_by(student_id=user.id,
                                        task_id=task.id)
        temp2 = Solution.query.filter_by(student_id=user.id,
                                         task_id=task.id).first()
        if temp2 is not None:
            sols.append(temp[-1])
        else:
            sols.append(temp2)
    return render_template('Task_page.html', title='Задача',
                           items=tasks, sols=sols)


# Страница задачи
@app.route('/index/<int:task_id>', methods=['GET', 'POST'])
@app.route('/index/<int:task_id>/', methods=['GET', 'POST'])
def task_page(task_id):
    if 1 <= task_id <= 3:
        task = Task.query.filter_by(id=task_id).first()
        user = Student.query.filter_by(username=session['username']).first()
        form = TaskForm()
        if 'username' not in session or user is None:
            return redirect('/login')
        if user.teacher:
            abort(403, message='Страница не доступна')
        temp = Solution.query.filter_by(student_id=user.id,
                                        task_id=task.id).first()
        temp2 = Solution.query.filter_by(student_id=user.id, task_id=task.id)
        booly, booly2 = None, None
        if temp is not None:
            temp = temp2[-1]
            booly, booly2 = False, temp.status == 'WA'
        else:
            booly, booly2 = True, False
        if form.validate_on_submit():
            if not task.handheld and \
                    (booly or booly2):  # Механическая проверка
                if check_task(task.id, form.text.data):  # Зачесть задачу
                    add_solution(form.text.data, 'OK', user, task)
                else:  # Отправить задачу на доработку
                    add_solution(form.text.data, 'WA', user, task)
            elif booly or booly2:  # Отправить задачу на ручную проверку
                add_solution(form.text.data, '-', user, task)
        return render_template('Task.html', title=task.title, task=task,
                               form=form, sol=temp)
    else:
        abort(404, message='Страница не найдена')


@app.route('/teacher_page')  # Страница учителя
@app.route('/teacher_page/')
def teacher_page():
    if 'username' not in session:
        return redirect('/login')
    user = Student.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect('/login')
    if not user.teacher:
        abort(403, message='Страница не доступна')
    solutions = list(Solution.query.filter_by(status='-'))
    return render_template('Solutions.html', solutions=solutions,
                           title='Непроверенные решения')


@app.route('/accept/<int:solution_id>')  # Зачесть задачу (вручную)
@app.route('/accept/<int:solution_id>/')
def accept(solution_id):
    if 'username' not in session:
        return redirect('/login')
    user = Student.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect('/login')
    if not user.teacher:
        abort(403, message='Страница не доступна')
    solution = Solution.query.filter_by(id=solution_id).first()
    if solution:
        solution.status = 'OK'
        db.session.commit()
    return redirect('/teacher_page')


@app.route('/refuse/<int:solution_id>')  # Отправить задачу на добработку
@app.route('/refuse/<int:solution_id>/')
def refuse(solution_id):
    if 'username' not in session:
        return redirect('/login')
    user = Student.query.filter_by(username=session['username']).first()
    if user is None:
        return redirect('/login')
    if not user.teacher:
        abort(403, message='Страница не доступна')
    solution = Solution.query.filter_by(id=solution_id).first()
    if solution:
        solution.status = 'WA'
        db.session.commit()
    return redirect('/teacher_page')


@app.route('/', methods=['GET'])
@app.route('/news', methods=['GET'])
@app.route('/news/', methods=['GET'])
def main():  # Основная страница
    news = Article.query.all()[:10]
    return render_template('News.html', title='Яндекс Лицей. Магнитогорск',
                           news=news)


@app.route('/news/<int:news_id>', methods=['GET'])  # Страница новости
@app.route('/news/<int:news_id>/', methods=['GET'])
def get_article(news_id):
    article = Article.query.filter_by(id=news_id).first()
    if article is not None:
        with open(article.text) as file:
            text = file.read()
        return render_template('Article.html', title=article.title,
                               article=article, text=text)
    else:
        abort(404, message='Article not found')


@app.route('/place', methods=['GET'])  # Страница местоположения
@app.route('/place/', methods=['GET'])
def place():
    return render_template('Place.html', title='Местоположение')


@app.route('/teachers', methods=['GET'])  # Страница об учителях
@app.route('/teachers/', methods=['GET'])
def teachers():
    return render_template('Teachers.html', title='Преподаватели')


@app.route('/coordinator', methods=['GET'])  # Страница о координаторе
@app.route('/coordinator/', methods=['GET'])
def coordinator():
    return render_template('Coordinator.html', title='Координатор')


@app.route('/abitu', methods=['GET'])  # Страница для абитуриентов
@app.route('/abitu/', methods=['GET'])
def abitu():
    return render_template('Abitu.html', title='Абитуриентам')


@app.route('/test', methods=['GET'])  # Страница с тестом
@app.route('/test/', methods=['GET'])
def test():
    return render_template('Test.html', title='Пробное тестирование')


@app.route('/test/<int:task_id>', methods=['GET', 'POST'])  # Страница вопроса
@app.route('/test/<int:task_id>/', methods=['GET', 'POST'])  # теста
def task_of_test(task_id):
    if 1 <= task_id <= 5:
        if task_id == 1:
            tester.start()
        elif not tester.has_started():
            return redirect('/test')
        if task_id != 5:
            form = TestForm()
        else:
            form = RadioTestForm()
        form.task.label = TASKS[task_id - 1][0]
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


@app.route('/test/result', methods=['GET'])  # Страница результата теста
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


@app.route('/schedule', methods=['GET', 'POST'])  # Страница расписания
@app.route('/schedule/', methods=['GET', 'POST'])
def schedule():
    return render_template('Schedule.html', title='Расписание')


@app.route('/studentbook')  # Страница навигации учебников
@app.route('/studentbook/')
def studentbook():
    return render_template('Studentbook.html', title='Учебные материалы',
                           src=None)


@app.route('/studentbook/<int:book_id>/', methods=['GET'])  # Страница
@app.route('/studentbook/<int:book_id>', methods=['GET'])  # учебника
def studentbook_by_id(book_id):
    if not 1 <= book_id <= 3:
        abort(404, message='Книга не найдена')
    else:
        return render_template('Studentbook.html', title='Учебные материалы',
                               src=BOOK[book_id])


@app.route('/program')  # Страница программы обучения
@app.route('/program/')
def program():
    return render_template('Program.html', title='Программа обучения',
                           href=PROGRAM)


if __name__ == '__main__':
    fill_news()  # Заполнить базу
    fill_tasks()
    create_teacher()
    app.run(port=8000, host='127.0.0.1')  # Запустить сервер
