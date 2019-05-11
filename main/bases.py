from main.app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json


class Student(db.Model):  # Класс пользователя
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group = db.Column(db.String(80), unique=False, nullable=False)
    teacher = db.Column(db.Boolean, unique=False, nullable=False)

    def check_password(self, password):  # Проверка пароля
        return check_password_hash(self.password_hash, password)


class Task(db.Model):  # Класс задачи
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    condition = db.Column(db.String(80), unique=False, nullable=False)
    handheld = db.Column(db.Boolean, unique=False, nullable=False)


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


class Article(db.Model):  # Класс новости
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String(500), unique=False, nullable=False)
    text = db.Column(db.String(10000), unique=False, nullable=False)


class TestQuestion(db.Model):  # Класс вопроса в тесте
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), unique=True, nullable=False)
    answer = db.Column(db.String(100), unique=False, nullable=False)
    form = db.Column(db.String(30), unique=False, nullable=False)


def add_solution(code, status, user, task):  # Добавление решения в базу
    solution = Solution(code=code, status=status,
                        student_id=user.id, task_id=task.id)
    user.Solutions.append(solution)
    task.Solutions.append(solution)
    db.session.add(solution)
    db.session.commit()


def fill_news():  # Добавление новостей в базу
    with open('main/static/json/News.json') as file:
        news = json.loads(file.read())
        for article in news:
            temp = \
                Article.query.filter_by(title=article['title']).first()
            if temp is None:  # Проверка наличия новости в базе
                article_obj = Article(title=article['title'],
                                      content=article['content'],
                                      text=article['text'])
                db.session.add(article_obj)
                db.session.commit()


def fill_test_questions():  # Добавление вопросов теста в базу
    with open('main/static/json/Test.json') as file:
        test = json.loads(file.read())
        for test_task in test:
            temp = \
                TestQuestion.query.\
                filter_by(question=test_task['question']).first()
            if temp is None:  # Проверка наличия новости в базе
                question_obj = TestQuestion(question=test_task['question'],
                                            answer=test_task['answer'],
                                            form=test_task['form'])
                db.session.add(question_obj)
                db.session.commit()


def fill_tasks():  # Добавление задач в базу
    with open('main/static/json/Tasks.json') as file:
        tasks = json.loads(file.read())
        for task in tasks:
            temp = Task.query.filter_by(title=task['title']).first()
            if temp is None:  # Проверка наличия задачи в базе
                task_obj = Task(title=task['title'],
                                condition=task['condition'],
                                handheld=bool(int(task['handheld'])))
                db.session.add(task_obj)
                db.session.commit()


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
