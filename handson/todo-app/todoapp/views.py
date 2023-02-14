from flask import request, redirect, url_for, render_template, flash, abort, jsonify, session, g
from todoapp import app, db
from todoapp.models import Todo, User, Tab
from functools import wraps
import datetime
from flask_oidc import OpenIDConnect
import secrets, string

oidc = OpenIDConnect(app)

def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):  # 可変長引数、引数の数を考えなくていい(つまり便利ってこと!!)
        if not g.user.admin:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)

    return decorated_view


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(session['user_id'])  # query.getとくれば主キーからデータを持ってくる


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user, authenticated = User.authenticate(db.session.query,  # userにdb.session.queryが入る
                                                request.form['email'],
                                                request.form['password'])  # authenticatedにはemailとpasswordが入る。
        app.logger.info(authenticated)
        if authenticated:
            session['user_id'] = user.id  # このuser.idって何？？
            session['user_name'] = user.name
            flash('You were logged in')
            g.user = User.query.get(user.id)  # ｇってついていればどこでも使える。
            if g.user.admin:
                return redirect(url_for('user_list'))
            else:
                return redirect(url_for('index'))

        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/todo', methods=['POST', 'GET'])
# @oidc.require_login
def index():
    if request.method == 'POST':  # ページへの接続方式を探知する機能

        content = Todo(content=request.form['content'],
                       deadline=request.form['deadline'],
                       user_id=session['user_id'],
                       tab_id=request.form['tab'])  # なんかしんないけど出来た

        try:
            db.session.add(content)  # session:接続が切断されない、辞書型で保存される
            db.session.commit()
            return redirect('/todo')
        except:
            # return redirect('/todo')
            return "フォームの送信中に問題が発生しました"

    else:
        tasks = Todo.query.filter(Todo.user_id == session['user_id']).order_by(
            Todo.date_created).all()  # tasksはリスト型で返ってくるはず
        statistics = Todo.query.filter(Todo.user_id == session['user_id'],
                                       Todo.deadline == datetime.date.today(), Todo.complete == False).order_by(
            Todo.date_created).all()
        mytasks = Todo.query.filter(Todo.user_id == session['user_id'],
                                    Tab.id == Todo.tab_id).order_by(
            Todo.date_created).all()
        mytasks = len(mytasks)
        statistics = len(statistics)
        # user = tasks[0].user_id
        user = session['user_id']
        tabs = Tab.query.filter(Tab.user_id == session['user_id']).order_by(
            Tab.id).all()
        tabtab = len(tabs)
        print(session['user_id'])
        return render_template('index.html', tasks=tasks, statistics=statistics, user=user,
                               tabs=tabs, mytasks=mytasks, tabtab=tabtab)  # 第二引数にはHTML先で使う変数


# 削除画面
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/todo')
    except:
        return 'There was an problem deleting that task'


# 編集画面
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def update(id):
    task_to_edit = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task_to_edit.content = request.form['content']
        task_to_edit.deadline = request.form['deadline']

        try:
            db.session.commit()
            return redirect('/todo')
        except:
            return "タスクの編集に問題が発生しました"
    else:
        return render_template('edit.html', task=task_to_edit)


@app.route('/todo/memo/<int:id>', methods=['POST', 'GEt'])
def memo(id):
    memo_to_edit = Todo.query.get_or_404(id)

    if request.method == 'POST':
        memo_to_edit.memo = request.form['memo']

        try:
            db.session.commit()
            return redirect('/todo')
        except:
            return 'メモの編集に問題が発生しました。'
    else:
        return render_template('index.html', )


@app.route('/users/')
@login_required
def user_list():
    users = User.query.all()
    return render_template('user/list.html', users=users)


@app.route('/users/<int:user_id>/')  # //の中にはidが入る
def user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user/detail.html', user=user)


@app.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_detail', user_id=user_id))
    return render_template('user/edit.html', user=user)


@app.route('/users/create/', methods=['GET', 'POST'])
# @login_required
def user_create():
    if request.method == 'POST':
        user = User(name=request.form['name'],
                    email=request.form['email'],
                    password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))  # 関数user_listのlist.htmlを返す。
    return render_template('user/edit.html')


@app.route('/users/<int:user_id>/delete/', methods=['DELETE'])
def user_delete(user_id):
    user = User.query.get(user_id)
    if user is None:
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'OK'})


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return render_template('login.html')


# タブ作り
@app.route('/todo/create_tab', methods=['POST', 'GET'])
def create_tab():
    if request.method == 'POST':
        tab = Tab(name=request.form['tab'],
                  user_id=session['user_id'])

        try:
            db.session.add(tab)  # session:接続が切断されない、辞書型で保存される
            db.session.commit()
            return redirect('/todo')
        except:
            return "フォームの送信中に問題が発生しました"

    else:
        tabs = Tab.query.filter(Tab.user_id == session['user_id']).order_by(
            Tab.id).all()
        return render_template('create_tab.html', tabs=tabs)


# 完了btn
@app.route('/todo/complete/<int:id>')
def complete(id):
    task_to_complete = Todo.query.get_or_404(id)
    if not task_to_complete.complete:
        task_to_complete.complete = True
        db.session.commit()
        return redirect('/todo')

    elif task_to_complete.complete:
        task_to_complete.complete = False
        db.session.commit()
        return redirect('/todo')

    else:
        print(1)


# カレンダー機能
@app.route('/todo/calendar')
def calendar():
    tasks = Todo.query.filter(Todo.user_id == session['user_id']).order_by(
        Todo.date_created).all()
    event_json = {
        'monthly': []
    }

    for i in tasks:
        event = {
            'id': i.id,
            'name': i.content,
            'startdate': i.date_created.strftime('%Y-%m-%d'),
            'enddate': i.date_created.strftime('%Y-%m-%d'),
            'starttime': datetime.datetime.now().time().strftime('%H-%M'),
            'endtime': datetime.datetime.now().time().strftime('%H-%M'),
            "color": "#FFB128",
            'url': ''
        }
        event_json['monthly'].append(event)

    return render_template('monthly.html', event_json=event_json)


# タブの削除
@app.route('/create_tab/delete/<int:id>')
def tab_delete(id):
    tab_to_delete = Tab.query.get(id)

    try:
        db.session.delete(tab_to_delete)
        db.session.commit()
        return redirect('/todo/create_tab')
    except:
        return 'There was an problem deleting that task'

@app.route('/oidc-login',methods=['GET','POST'])
@oidc.require_login
def oidc_login():
    email = oidc.user_getfield('email')

    user = User.query.filter(User.email ==  email).first()
    if user is None:
        password = pass_gen(10)
        user = User(name=email,
                    email=email,
                    password=password,
                    admin=False)
        session.add(user)
        session.commit()
        return redirect(url_for('index'))
    flask_session['user_id'] = user.id
    if user.admin == True:
        return redirect(url_for('user_list'))
    else:
        return redirect(url_for('index'))
    return render_template('login.html')

def pass_gen(size=12):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars)for x in range(size))
