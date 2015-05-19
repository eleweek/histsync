# histsync

Cloud Bash History app using python and flask

The app is currently under heavy development

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

The client shouldn't send the previous command on startup

So something like zsh's preexec() hook is necessary (or maybe it is possible to detect is $PROMPT_COMMAND is executed after startup)

### FAQ PAGE

### Easy install script

### Easy standalone app 

Make it easy to deploy your own standalone installation, probably using something like "Deploy to heroku" button
