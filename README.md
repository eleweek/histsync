# HistSync

[![Join the chat at https://gitter.im/eleweek/histsync](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/eleweek/histsync?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Cloud bash history app using Python and Flask.

The app is currently under heavy development.

## Installing

Run: 
```bash <(curl http://www.histsync.io/download-client/install.bash)```

And then add this to your .bashrc / .bash_profile

```
preexec() {
    ~/.histsync/histsync-client --api-key {{hist_sync_api_key}} --user {{github_username}} "$1" --log-file ~/.histsync/log;
}
``` 

## Running development version locally

HistSync uses python2.7

Using foreman is recommended(makes easier config managing)

### Virtual Environment

1. Initialize virtual environment: ```virtualenv histsync-venv```
2. Activate virtual environment ```source histsync-venv/bin/activate```
3. Install dependencies ```pip install -r requirements-dev.txt```

### Database

HistSync uses postgres in production(and it is recommended to use postgres in development), but using sqlite is also fine.

1. Run ```foreman run python```
2. In python shell: 
```
from app import db
db.create_all()
```
3. TODO: migrations

### .env 

Create .env file containing these lines

```
STANDALONE="true"
STANDALONE_USERNAME="yourusername"
DATABASE_URL="sqlite:///sqlite.db"
GITHUB_APP_ID="noid"
GITHUB_APP_SECRET="nosecret"
SECRET_KEY="devkey"
```

### Running the app

```foreman run python app.py run```

## Special thanks for helping with 1.0 release

Goes to [raoulvdberge](https://github.com/raoulvdberge) for early testing, bug reporting & advice
