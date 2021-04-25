# - * - coding: utf-8 - * -
from flask import Flask, render_template, redirect, request
import base64

from flask.helpers import url_for

from data import db_session
from data.users import User
from data.books import Books
from forms.user import RegisterForm, LoginForm
from forms.book import BookEditForm
from flask_login import LoginManager, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    books = db_sess.query(Books)
    books_list = [
        {
            "id": book.id,
            "title": book.title,
            "cover": f"data:image/jpeg;base64,{base64.b64encode(book.cover).decode()}"
        } for book in books
    ]
    return render_template("index.html", books=books_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book/<b_id>')
def book(b_id):
    db_sess = db_session.create_session()
    book_n = db_sess.query(Books).filter(Books.id == b_id)
    img_str = f"data:image/jpeg;base64,{base64.b64encode(book_n[0].cover).decode()}"
    return render_template("book.html", book=book_n[0], img_str=img_str)


@app.route('/book/<b_id>/edit', methods=['GET', 'POST'])
def book_edit(b_id):
    db_sess = db_session.create_session()
    form = BookEditForm()
    book_n = db_sess.query(Books).filter(Books.id == b_id)[0]
    if request.method == 'GET':
        img_str = f"data:image/jpeg;base64,{base64.b64encode(book_n.cover).decode()}"
        form = BookEditForm(
            title=book_n.title,
            creator=book_n.creator,
            cover=img_str,
            created_date=book_n.created_date,
            about=book_n.about,
            series=book_n.series,
        )
        return render_template("edit.html", form=form, img_str=img_str)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('book', b_id=b_id))
        if form.validate_on_submit():
            book_n.title = form.title.data
            book_n.creator = form.creator.data
            book_n.created_date = form.created_date.data
            book_n.about = form.about.data
            db_sess.commit()
            return redirect(request.url)


@app.route('/delete/<int:b_id>')
def delete_book(b_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == b_id).first()
    db_sess.delete(book)
    db_sess.commit()
    return render_template("delete.html")


@app.route('/load', methods=['GET', 'POST'])
def load_book():
    db_sess = db_session.create_session()
    form = BookEditForm()
    book_n = Books()
    if request.method == 'GET':
        form = BookEditForm(
            title='',
            creator='',
            cover='',
            created_date='',
            about='',
            series='',
        )
        return render_template("edit.html", form=form)
    if request.method == 'POST':
        if form.cancel.data:
            return redirect(url_for('book'))
        if form.validate_on_submit():
            book_n.title = form.title.data
            book_n.creator = form.creator.data
            book_n.created_date = form.created_date.data
            book_n.about = form.about.data
            db_sess.commit()
            return redirect(request.url)


if __name__ == '__main__':
    main()
