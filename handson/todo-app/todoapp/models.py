from todoapp import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import synonym


# モデル
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(200), default=0)
    deadline = db.Column(db.Date)
    user_id = db.Column(db.Integer, nullable=False)
    tab_id = db.Column(db.Integer,)
    complete = db.Column(db.Boolean, nullable=True, default=False)
    memo = db.Column(db.String(255), default='')

    def __repr__(self):
        return '<Task %r>' % self.id


# ステータス
class Status(db.Model):
    __tablename__ = 'Status'

    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(200), nullable=False)


status1 = Status(status_name='達成率0%')
status2 = Status(status_name='達成率50%未満')
status3 = Status(status_name='達成率50%以上')
status4 = Status(status_name='達成率100%')
status5 = Status(status_name='削除')


class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='', nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(100), nullable=False)
    admin = db.Column(db.Boolean, nullable=True, default=False)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()  # 両端の連続する空白文字の削除
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)  # あだ名のようなものを付ける？？

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)  # パスワードに何かしら入っていれば動く

    @classmethod
    def authenticate(cls, query, email, password):
        user = query(cls).filter(cls.email == email).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return u'<User id={self.id} email={self.email!r}>'.format(
            self=self)


class Tab(db.Model):
    __tablename__ = 'Tab'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='', nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


def init():
    db.create_all()
    db.session.bulk_save_objects([status1, status2, status3, status4, status5])
    db.session.commit()
