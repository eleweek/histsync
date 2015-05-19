from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.github import GitHub
from flask.ext.login import LoginManager, login_user, logout_user, current_user, UserMixin

from sqlalchemy import func
from datetime import datetime
import humanize
import os
from uuid import uuid4


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_APP_SECRET']
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_APP_ID']
Bootstrap(app)
github = GitHub(app)


@github.access_token_getter
def token_getter():
    if current_user.is_authenticated():
        return current_user.github_access_token

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        db.session.add(instance)
    return instance


stars_users = db.Table('stars_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('command_id', db.Integer, db.ForeignKey('command.id'))
                       )


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    another_id = db.Column(db.String())
    time_added = db.Column(db.DateTime, default=func.now())
    text = db.Column(db.String())

    is_public = db.Column(db.Boolean(), default=False)
    time_shared = db.Column(db.DateTime, default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def format_time_added(self):
        if self.time_added:
            return humanize.naturaltime(datetime.utcnow() - self.time_added)
        else:
            return "[None]"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(256))
    api_key = db.Column(db.String())

    github_access_token = db.Column(db.String(200))
    commands = db.relationship("Command", lazy='dynamic', backref='user')
    starred_commands = db.relationship('Command', secondary=stars_users, lazy='dynamic',
                                       backref=db.backref('starred_by', lazy='dynamic'))

    def add_api_key_if_necessary(self):
        if not self.api_key:
            self.generate_api_key()

    def generate_api_key(self):
        self.api_key = str(uuid4())
        db.session.commit()

    def get_commands(self, only_public=False):
        if not only_public:
            commands = self.commands
        else:
            commands = self.commands.filter_by(is_public=True)

        commands = commands.order_by(Command.time_added.desc(), Command.id.desc())
        return commands


@app.route('/')
def index():
    commands = Command.query
    return render_template("index.html", commands=commands)


@app.route('/public_commands')
def public_commands():
    commands = Command.query.filter_by(is_public=True).order_by(Command.time_shared.desc())
    return render_template("public_commands.html", commands=commands)


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(name=username).first_or_404()
    user.add_api_key_if_necessary()
    commands = user.get_commands(only_public=(current_user != user))
    current_user_starred_commands = current_user.starred_commands.all()

    # TODO: a new template
    return render_template("profile.html", commands=commands, username=username, current_user_starred_commands=current_user_starred_commands)


@app.route('/api/v0/user/<username>/add_command', methods=["POST"])
def add_command(username):
    command_text = request.form["command_text"]
    api_key = request.form["api_key"]
    another_id = request.form.get("id")
    user = User.query.filter_by(name=username).first_or_404()

    if another_id is not None and user.commands.filter_by(another_id=another_id).first() is not None:
        abort(400)

    if api_key != user.api_key:
        abort(403)

    c = Command(text=command_text, another_id=another_id)
    user.commands.append(c)
    db.session.add(c)
    db.session.commit()
    return "OK"


@app.route('/api/v0/user/<username>/get_commands')
def get_commands(username):
    api_key = request.args.get("api_key")
    user = User.query.filter_by(name=username).first_or_404()

    def convert_command(c):
        return {"id": c.id,
                "another_id": c.another_id,
                "text": c.text,
                "time_added": c.time_added,
                "is_public": c.is_public}

    return jsonify(comamnds=[convert_command(c) for c in user.get_commands(api_key != user.api_key)])


@app.route('/authorize_callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        # TODO
        raise Exception("TODO: handle absent access token!")

    user_json = github.get("user".format(), params={'access_token': access_token})
    user = get_or_create(User, name=user_json["login"], email=user_json.get("email"), github_access_token=access_token)
    db.session.commit()
    login_user(user)
    return redirect(next_url)


@app.route('/login')
def login():
    return github.authorize('user:email')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/_regenerate_api_key')
def regenerate_api_key():
    if current_user.is_authenticated():
        current_user.generate_api_key()
        return jsonify(api_key=current_user.api_key)


@app.route('/_delete_command/<int:id>', methods=["POST"])
def delete_command(id):
    c = Command.query.get_or_404(id)
    if current_user.is_anonymous() or current_user != c.user:
        abort(403)

    db.session.delete(c)
    db.session.commit()
    return jsonify(result="OK")


@app.route('/_star_command/<int:id>', methods=["POST"])
def _star_command(id):
    c = Command.query.get_or_404(id)
    current_user.starred_commands.append(c)
    db.session.commit()

    return jsonify(result="OK")


@manager.command
def run():
    app.run(debug=True)

if __name__ == '__main__':
    manager.run()
