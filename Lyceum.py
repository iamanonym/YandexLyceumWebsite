from main.app import app, db
from main.routes import *
from main.bases import fill_tasks, fill_news, \
    fill_test_questions, create_teacher

if __name__ == '__main__':
    db.create_all()  # Создаем все сущности в базе
    fill_news()  # Заполнить базу
    fill_test_questions()
    fill_tasks()
    create_teacher()
    app.run(port=8000, host='127.0.0.1')  # Запустить сервер
