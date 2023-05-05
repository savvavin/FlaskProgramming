from flask import Flask, render_template, request, redirect, url_for
import sqlite3

from forms import LoginForm, RegisterForm, TasksForm, ContestsForm
from models import Tasks, User, Contests, Solutions
from flask import Flask, render_template, redirect, request, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import db_session
import subprocess
import pytest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

counter = 0

@app.route('/')
def index():
    global counter
    db_sess = db_session.create_session()
    task = db_sess.query(Tasks)
    task = task[::-1]
    try:
        counter = task[0].id + 1
    except IndexError:
        counter = 1

    return render_template('index.html')


def main():
    db_session.global_init("proj.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
                                   message="Такая почта уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        user.score = 0
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


@app.route('/contests')
def contests():
    db_sess = db_session.create_session()
    contests = db_sess.query(Contests)
    return render_template("contests.html", contests=contests)


@app.route('/add_contest', methods=['GET', 'POST'])
@login_required
def add_contest():
    form = ContestsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        contests = Contests()
        contests.title = form.title.data
        contests.description = form.description.data
        current_user.contests.append(contests)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/contests')
    return render_template('add_contest.html', title='Добавление контеста',
                           form=form)


@app.route('/contests/<int:id>', methods=['GET', 'POST'])
@login_required
def contest(id):
    db_sess = db_session.create_session()
    contest = db_sess.query(Contests).filter(Contests.id == id).first()
    tasks = db_sess.query(Tasks).filter(Tasks.contest_id == id)
    return render_template('contest.html', contest=contest, tasks=tasks)


@app.route('/edit_contest/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contest(id):
    form = ContestsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        contests = db_sess.query(Tasks).filter(Contests.id == id,
                                               Contests.user == current_user
                                               ).first()
        if contests:
            form.title.data = contests.title
            form.description.data = contests.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        contests = db_sess.query(Contests).filter(Contests.id == id,
                                                  Contests.user == current_user
                                                  ).first()
        if contests:
            contests.title = form.title.data
            contests.description = form.description.data
            db_sess.commit()
            return redirect('/contests')
        else:
            abort(404)
    return render_template('add_contest.html',
                           title='Редактирование контеста',
                           form=form
                           )


@app.route('/contests_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def contests_delete(id):
    db_sess = db_session.create_session()
    contests = db_sess.query(Contests).filter(Contests.id == id,
                                              Contests.user == current_user
                                              ).first()
    tasks = db_sess.query(Tasks).filter(Tasks.contest_id == id)
    if tasks:
        for x in tasks:
            db_sess.delete(x)
            db_sess.commit()
    if contests:
        db_sess.delete(contests)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/contests')


@app.route('/contests/<int:id>/add_task', methods=['GET', 'POST'])
@login_required
def add_task(id):
    form = TasksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = Tasks()
        tasks.title = form.title.data
        tasks.description = form.description.data
        tasks.input_format = form.input_format.data
        tasks.output_format = form.output_format.data
        tasks.input_example = form.input_example.data
        tasks.output_example = form.output_example.data
        tasks.contest_id = id
        global counter
        f = request.files['file']
        test = open(f'tests/test_{counter}.py', 'wb')
        test.write(f.read())
        test.close()
        counter += 1
        current_user.tasks.append(tasks)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/contests/{id}')
    return render_template('add_task.html', title='Добавление задачи',
                           form=form)


@app.route('/contests/<int:id1>/tasks/<int:id>', methods=['GET', 'POST'])
@login_required
def task(id1, id):
    db_sess = db_session.create_session()
    task = db_sess.query(Tasks).filter(Tasks.id == id).first()
    if request.method == "GET":
        return render_template('task.html', task=task)
    elif request.method == "POST":
        f = request.files['file']
        ans = open('ans.py', 'wb')
        ans.write(f.read())
        ans.close()

        solutions = Solutions()
        solutions.task_id = id

        result = subprocess.run(['pytest', f'tests/test_{id}.py'], capture_output=True)
        print(result.stdout.decode())
        print(result.stderr.decode())
        x = result.stdout.decode()[-87::]
        if 'failed' in x:
            solutions.verdict = 'ER'
        else:
            solutions.verdict = 'OK'
            good_solutions = db_sess.query(Solutions).filter(Solutions.task_id == id,
                                                             Solutions.user_id == current_user.id,
                                                             Solutions.verdict == 'OK')
            if good_solutions.first() == None:
                current_user.score = str(int(current_user.score) + 1)

        current_user.solutions.append(solutions)
        db_sess.merge(current_user)
        db_sess.commit()

        return f'form sent <a href="/contests/{id1}/tasks/{id}">Назад</a>'


@app.route('/contests/<int:id1>/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id1, id):
    form = TasksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            form.title.data = tasks.title
            form.description.data = tasks.description
            form.input_format.data = tasks.input_format
            form.output_format.data = tasks.output_format
            form.input_example.data = tasks.input_example
            form.output_example.data = tasks.output_example
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                            Tasks.user == current_user
                                            ).first()
        if tasks:
            tasks.title = form.title.data
            tasks.description = form.description.data
            tasks.input_format = form.input_format.data
            tasks.output_format = form.output_format.data
            tasks.input_example = form.input_example.data
            tasks.output_example = form.output_example.data
            db_sess.commit()
            return redirect(f'/contests/{id1}')
        else:
            abort(404)
    return render_template('add_task.html',
                           title='Редактирование задачи',
                           form=form
                           )


@app.route('/contests/<int:id1>/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id1, id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                        Tasks.user == current_user
                                        ).first()
    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/contests/{id1}')


@app.route('/leaderboard')
def leaderboard():
    db_sess = db_session.create_session()
    users = db_sess.query(User).order_by(User.score.desc())
    return render_template("leaderboard.html", users=users)


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    return render_template("profile.html", user=user)


@app.route('/solutions', methods=['GET', 'POST'])
@login_required
def solutions():
    db_sess = db_session.create_session()
    solutions = db_sess.query(Solutions).filter(Solutions.user_id == current_user.id)
    solutions = solutions[::-1]
    spis = []
    for i in solutions:
        if db_sess.query(Tasks).filter(Tasks.id == i.task_id).first() not in spis:
            spis.append(db_sess.query(Tasks).filter(Tasks.id == i.task_id).first())
    return render_template("solutions.html", solutions=solutions, spis=spis)


@app.route('/solutions/<int:id>', methods=['GET', 'POST'])
@login_required
def solution(id):
    db_sess = db_session.create_session()
    solution = db_sess.query(Solutions).filter(Solutions.id == id).first()
    return render_template("solution.html", solution=solution)


if __name__ == '__main__':
    main()
