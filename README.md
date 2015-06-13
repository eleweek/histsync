# HistSync

Cloud bash history app using Python and Flask.

The app is currently under heavy development.

## Using the alpha version

To use an alpha version of the app, try this:

1. Go to http://histsync.io/
2. Login with GitHub
3. Click on "My Profile"
4. Click "Show API key" and copy your API key
5. [Install bash-preexec](https://github.com/rcaloras/bash-preexec)
6. Install `histsync-client.py` (put it into your root directory)
7. Add this to your `.bashrc` / `.bash_profile`: 

```
preexec() {
    ~/histsync-client.py --api_key <your_api_key> --user <your_username> "$1" >>~/histsync.log 2>&1;
}
``` 
