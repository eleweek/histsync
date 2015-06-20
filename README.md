# HistSync

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

## Special thanks

Goes to [raoulvdberge](https://github.com/raoulvdberge) for early testing, bug reporting & advice
