from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from sqlalchemy import func
from datetime import datetime
import humanize
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
Bootstrap(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_added = db.Column(db.DateTime, default=func.now())
    text = db.Column(db.String())

    def format_time_added(self):
        if self.time_added:
            return humanize.naturaltime(datetime.utcnow() - self.time_added)
        else:
            return "[None]"


@app.route('/')
def index():
    commands = Command.query
    return render_template("index.html", commands=commands)


@app.route('/api/v0/add_command', methods=["POST"])
def add_command():
    command_text = request.form["command_text"]
    c = Command(text=command_text)
    db.session.add(c)
    db.session.commit()
    return "OK"


@manager.command
def run():
    app.run(debug=True)

if __name__ == '__main__':
    manager.run()
