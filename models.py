from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from db_session import SqlAlchemyBase
import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import orm

from werkzeug.security import generate_password_hash, check_password_hash


class Solutions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'solutions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    verdict = Column(String, nullable=True)

    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = orm.relationship('Tasks')

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f'<Solutions> {self.id}'

class Tasks(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    input_format = Column(String, nullable=True)
    output_format = Column(String, nullable=True)
    input_example = Column(String, nullable=True)
    output_example = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User')

    contest_id = Column(Integer, ForeignKey("contests.id"))
    contest = orm.relationship('Contests')

    solutions = orm.relationship('Solutions', back_populates='task')

    def __repr__(self):
        return f'<Tasks> {self.id} {self.title} {self.user_id} {self.contest_id}'

class Contests(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'contests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User')

    tasks = orm.relationship("Tasks", back_populates='contest')

    def __repr__(self):
        return f'<Contests> {self.id} {self.title} {self.user_id}'

class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    score = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)

    tasks = orm.relationship("Tasks", back_populates='user')

    contests = orm.relationship("Contests", back_populates='user')

    solutions = orm.relationship('Solutions', back_populates='user', lazy='subquery')

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)