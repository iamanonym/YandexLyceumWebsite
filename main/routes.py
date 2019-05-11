from flask import render_template, session, redirect
from werkzeug.security import generate_password_hash
from flask_restful import abort
import json
from main.forms import LoginForm, TaskForm, \
    RegisterForm, TestForm, RadioTestForm, CommentForm
from main.bases import Student, Task, Solution, \
    Article, TestQuestion, Comment, add_solution
from main.app import app, db
from main.utils import tester, check_task

with open('main/static/json/Rasp_url.json') as file:
    PROGRAM = json.loads(file.read())
with open('main/static/json/Book_url.json') as file2:
    BOOK = json.loads(file2.read())


@app.errorhandler(401)  # Отработка ошибки 401
def wrong_login(error):
    return render_template('Error.html',
                           title='Неверный логин или пароль',
                           error_code=401), 401


@app.errorhandler(403)  # Отработка ошибки 403
def page_not_found(error):
    return render_template('Error.html',
                           title='Вам не доступна данная страница',
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
            abort(401, message='Неверный логин или пароль')
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
    temp = list(Solution.query.filter_by(status='-'))
    solutions = []
    for solution in temp:
        student = Student.query.filter_by(id=solution.student_id).first()
        if student.group == user.group:
            solutions.append(solution)
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


@app.route('/news/<int:news_id>', methods=['GET', 'POST'])  # Страница новости
@app.route('/news/<int:news_id>/', methods=['GET', 'POST'])
def get_article(news_id):
    article = Article.query.filter_by(id=news_id).first()
    form = CommentForm()
    if article is not None:
        with open(article.text) as file:
            text = file.read()
        if form.validate_on_submit():
            comment = Comment(author=form.name.data,
                              content=form.comment.data,
                              article_id=article.id)
            article.Comments.append(comment)
            db.session.add(comment)
            db.session.commit()
        return render_template('Article.html', title=article.title,
                               article=article, text=text, form=form,
                               comments=article.Comments)
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
        TASKS = list(TestQuestion.query.all())
        task = TASKS[task_id - 1]
        form = None
        if task.form == 'stand':
            form = TestForm()
        elif task.form == 'radio':
            form = RadioTestForm()
        with open(task.question) as file:
            form.task.label = file.read()
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
                               tasks=list(TestQuestion.query.all()),
                               questions=tester.get_questions(),
                               answers=tester.get_answers())
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
                               src=BOOK[str(book_id)])


@app.route('/program')  # Страница программы обучения
@app.route('/program/')
def program():
    return render_template('Program.html', title='Программа обучения',
                           href=PROGRAM)
