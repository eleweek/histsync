# histsync

Cloud Bash History app using python and flask

The app is currently under heavy development

## Using alpha version

To use an alpha version of the app, try this:

1. Go to http://histsync.herokuapp.com/ 
2. Login with github
3. Click "My Profile" in the navbar 
4. Click "Show API key"
5. [Install bash-preexec](https://github.com/rcaloras/bash-preexec)
6. Install histsync-client.py (put it into your ~)
7. Add this to your .bashrc / .bash_profile: 

```
preexec() {
    echo "just typed $1";
    ~/histsync-client.py --api_key <your_api_key> --user <your_username> "$1" >>~/histsync.log 2>&1;
}
``` 

## TODO

### API

Current API supports only adding commands. It is necessary to add support for removing/starring/etc (basically, for everything that's possible from web UI).

### Activity feed in profile

Commands that were added automatically/manually, commands that areyou starred, comments on commands

### /public_commands 

Remove stubs, make buttons actually do something

(?) Different ways of sorting

### Making commands public

Nice workflow for adding commands to public list

### Better client

Better logging

### FAQ PAGE

### Easy install script

Maybe .histsync folder

### Easy standalone app 

Make it easy to deploy your own standalone installation, probably using something like "Deploy to heroku" button
