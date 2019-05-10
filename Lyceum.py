from main.app import app, db
from main.routes import *
from main.bases import fill_tasks, fill_news, \
    fill_test_questions, create_teacher


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

if __name__ == '__main__':
    db.create_all()  # Создаем все сущности в базе
    fill_news()  # Заполнить базу
    fill_test_questions()
    fill_tasks()
    create_teacher()
    app.run(port=8000, host='127.0.0.1')  # Запустить сервер
