from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, \
    EqualTo, ValidationError, Length
from main.bases import Student


def check_password(password):  # Проверка пароля
    if password.isdigit() or password.isalpha():
        return 'Пароль состоит из символов одного вида'
    elif set(password).intersection({',', '.', '!', '?', '/', '\\',
                                     ';', '(', ')', '&', '[', ']',
                                     '<', '>', '*', '|', ':', '"'}):
        return 'Недопустимые символы в пароле'
    else:
        return 'OK'


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
                        choices=[('2 год 1 группа', '2 год 1 группа'),
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


class CommentForm(FlaskForm):  # Форма добавления комментария
    name = StringField('Введите Ваш ник', validators=[DataRequired()])
    comment = TextAreaField('Введите текст комментария',
                            validators=[DataRequired()])
    submit = SubmitField('Отправить')
