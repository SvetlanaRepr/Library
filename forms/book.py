# - * - coding: utf-8 - * -
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import DataRequired


class BookEditForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    creator = StringField('Автор', validators=[DataRequired()])
    cover = StringField('Обложка')
    created_date = IntegerField('Дата создания')
    about = TextAreaField('Описание', validators=[DataRequired()])
    file = StringField('Загрузить файл обложки')
    series = StringField('Серия')
    submit = SubmitField('Сохранить')
    cancel = SubmitField('Закрыть')
