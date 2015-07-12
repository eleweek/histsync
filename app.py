from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, send_from_directory
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_github import GitHub
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin, login_required

from flask_restful import Resource, Api, reqparse
from flask_restful import fields, marshal_with
from flask_restful import abort as fr_abort

from sqlalchemy import func, PrimaryKeyConstraint
from sqlalchemy.sql import or_
from datetime import datetime
import humanize
import os
from uuid import uuid4

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument('api_key')

add_command_parser = api_key_parser.copy()
add_command_parser.add_argument('command')

app = Flask(__name__)
app.config['STANDALONE'] = os.environ.get('STANDALONE', False)
app.config['STANDALONE_USERNAME'] = os.environ.get('STANDALONE_USERNAME')
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_APP_SECRET']
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_APP_ID']
Bootstrap(app)
github = GitHub(app)
api = Api(app)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.template_filter()
def timesince(dt, default="just now"):
    """
    Jinja filter that takes a datetime and retuns the
    'human' version of time since said datetime.

    e.g. 28 minutes ago
    """

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


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


class SearchForm(Form):
    regex = StringField('regex', validators=[DataRequired()])
    search_button = SubmitField('Search')


stars_users = db.Table('stars_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('command_id', db.Integer, db.ForeignKey('command.id')),
                       PrimaryKeyConstraint('user_id', 'command_id')
                       )


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    another_id = db.Column(db.String())
    time_added = db.Column(db.DateTime, default=func.now())
    text = db.Column(db.String())

    is_public = db.Column(db.Boolean(), default=False)
    time_shared = db.Column(db.DateTime, default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text())

    def __repr__(self):
        return u'Command {} "{}"'.format(self.id, self.text)

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
    starred_commands = db.relationship('Command', secondary=stars_users, lazy='joined',
                                       backref=db.backref('starred_by', lazy='joined'))

    def __repr__(self):
        return u'User {} {}'.format(self.id, self.name)

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

    def get_starred_commands(self):
        commands = Command.query\
                          .filter(Command.starred_by.any(User.id == self.id))\
                          .filter(or_(Command.is_public, Command.user == self))\
                          .order_by(Command.time_added.desc(), Command.id.desc())

        return commands


@app.route('/')
def index():
    commands = Command.query.filter_by(is_public=True).\
        options(db.subqueryload(Command.starred_by)).outerjoin("starred_by").\
        group_by(Command.id).order_by(db.func.count(User.id).desc()).all()
    return render_template("index.html", commands=commands)


@app.route('/public_commands')
def public_commands():
    commands = Command.query.filter_by(is_public=True).order_by(Command.time_shared.desc())
    return render_template("public_commands.html", commands=commands)


@app.before_request
def add_api_key():
    if current_user.is_authenticated():
        current_user.add_api_key_if_necessary()


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(name=username).first_or_404()
    commands = user.get_commands(only_public=True)

    # TODO: a new template
    return render_template("profile.html", commands=commands, username=username)


@app.route('/my_shell_history', defaults={"page": 1}, methods=["GET", "POST"])
@app.route('/my_shell_history/page/<int:page>', methods=["GET", "POST"])
@login_required
def my_shell_history(page):
    search_form = SearchForm()
    if search_form.validate_on_submit():
        return redirect(url_for("my_shell_history_search", regex=search_form.regex.data))

    commands = current_user.get_commands(only_public=False).paginate(per_page=100, page=page)
    return render_template("shell_history.html", commands=commands, search_form=search_form, title="My Shell History")


@app.route('/my_shell_history/search/<regex>', defaults={"page": 1})
@app.route('/my_shell_history/search/<regex>/page/<int:page>')
@login_required
def my_shell_history_search(page, regex):
    commands = current_user.get_commands(only_public=False).filter(Command.text.op("~")(regex)).paginate(per_page=100, page=page)
    return render_template("shell_history.html", commands=commands, title=u"My Shell History: search results for [{}]".format(regex))


@app.route('/my_starred_commands')
def my_starred_commands():
    commands = current_user.get_starred_commands()
    return render_template("starred_commands.html", commands=commands)


command_resource_fields = {
    "id": fields.Integer,
    "text": fields.String,
    "time_added": fields.DateTime,
    "is_public": fields.Boolean
}


class UserCommands(Resource):
    @staticmethod
    def _get_user_checking_credentials(username, api_key):
        user = User.query.filter_by(name=username).first()
        if not user:
            fr_abort(403, message="No such user")

        if api_key != user.api_key:
            fr_abort(403, message="Wrong API key")
        return user

    @marshal_with(command_resource_fields)
    def get(self, username):
        args = api_key_parser.parse_args()
        user = UserCommands._get_user_checking_credentials(username, args['api_key'])
        return user.get_commands().all()

    def post(self, username):
        args = add_command_parser.parse_args()
        user = UserCommands._get_user_checking_credentials(username, args['api_key'])
        command_text = args['command']

        c = Command(text=command_text)
        user.commands.append(c)
        db.session.add(c)
        db.session.commit()
        return 200

api.add_resource(UserCommands, '/api/v0/user/<username>/commands')


@app.route('/authorize_callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return "No access token. If you think this is a bug, please report it: http://github.com/eleweek/histsync", 403

    user_json = github.get("user".format(), params={'access_token': access_token})
    user = get_or_create(User, name=user_json["login"], email=user_json.get("email"), github_access_token=access_token)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(next_url)


@app.route('/login')
def login():
    if not app.config['STANDALONE']:
        return github.authorize('user:email')
    else:
        user = get_or_create(User, name=app.config['STANDALONE_USERNAME'])
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('index'))


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


@app.route('/_unstar_command/<int:id>', methods=["POST"])
def _unstar_command(id):
    c = Command.query.get_or_404(id)
    current_user.starred_commands.remove(c)
    db.session.commit()

    return jsonify(result="OK")


@app.route('/_publish_command/<int:id>', methods=["POST"])
def _publish_command(id):
    c = Command.query.get_or_404(id)
    if current_user.is_anonymous() or current_user != c.user:
        abort(403)
    c.is_public = True
    c.text = request.form['command']
    c.description = request.form['description']
    db.session.commit()

    return jsonify(result="OK")


@app.route('/_edit_command/<int:id>', methods=["POST"])
def _edit_command(id):
    c = Command.query.get_or_404(id)
    if current_user.is_anonymous() or current_user != c.user:
        abort(403)
    c.text = request.form['command']
    c.description = request.form['description']
    db.session.commit()
    return jsonify(result="OK")


@app.route('/_unpublish_command/<int:id>', methods=["POST"])
def _unpublish_command(id):
    c = Command.query.get_or_404(id)
    if current_user.is_anonymous() or current_user != c.user:
        abort(403)
    c.is_public = False
    db.session.commit()

    return jsonify(result="OK")


@app.route('/download-client/<part>')
def download_client(part):
    if part not in ['bash-preexec.sh', 'histsync-client', 'install.bash']:
        abort(404)
    return send_from_directory('.', part)


@app.route('/faq')
def faq():
    return render_template("faq.html")


@manager.command
def run():
    app.run(debug=True)

if __name__ == '__main__':
    manager.run()
