import sys
from main.bases import TestQuestion


def check_task(task_id, code):  # Проверка решения
    res, solve, inputs = [], [], []
    with open('main/static/text/'
              'task_check/input{}.txt'.format(task_id)) as file:
        for line in file.readlines():
            inputs.append(line.strip())
        file.close()
    with open('main/static/text/'
              'task_check/res{}.txt'.format(task_id)) as file2:
        for line in file2.readlines():
            solve.append(line.rstrip())
        file2.close()
    for number in range(3):
        input_file = open('main/static/text'
                          '/task_check/input_temp.txt', 'w')
        input_file.write(inputs[number])
        input_file.close()
        temp = code if code.endswith('\n') else code + \
            '\n' + "sys.stdout = stdout\nfile1.close()\nfile2.close()\n"
        code2 = \
            "file1 = open('main/static/text/" \
            "task_check/input_temp.txt')\n" \
            "file2 = open('main/static/text/" \
            "task_check/output_temp.txt', 'w')\n" \
            "stdout = sys.stdout\nsys.stdin = file1\n" \
            "sys.stdout = file2\n" + temp
        try:
            exec(code2)
        except Exception:
            return False
        with open('main/static/text/'
                  'task_check/output_temp.txt'.format(task_id)) as file:
            res.append(file.read().rstrip())  # Добавление результата в список
            file.close()
    return res == solve


class Tester:  # Класс, следящий за прохождением теста абитуриента
    def __init__(self):
        self.started = False
        self.result = [None for _ in range(5)]
        self.answers = [None for _ in range(5)]
        self.tasks = None

    def start(self):  # Начать тест
        self.started = True
        self.result = [None for _ in range(5)]
        self.answers = [None for _ in range(5)]
        self.tasks = list(TestQuestion.query.all())

    def stop(self):  # Закончить тест
        self.started = False

    def has_started(self):
        return self.started

    def add(self, ind, answer):  # Добавить ответ
        if self.started:
            self.answers[ind] = answer
            self.result[ind] = self.tasks[ind].answer == answer

    def get_result(self):
        return self.result.count(True)

    def get_questions(self):
        self.questions = []
        for task in self.tasks:
            self.questions.append(open(task.question).read())
        return self.questions

    def get_list(self):
        return self.result

    def get_answers(self):
        return self.answers


tester = Tester()
