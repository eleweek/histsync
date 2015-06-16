#!/bin/bash
mkdir -p ~/.histsync
for file in {'bash-preexec.sh','histsync-client'}; do
    echo Downloading, $file
    curl "http://www.histsync.io/download-client/$file" > ~/.histsync/$file;
done

echo
echo
echo '# Add the following lines in your .bashrc / .bash_profiles'
echo '# ============'
echo '# HistSync'
echo 'source ~/.histsync/bash-preexec.sh'
echo 'preexec() {'
echo '    ~/histsync/histsync-client --api-key {{hist_sync_api_key}} --user {{github_username}} "$1" --log-file ~/.histsync/log;'
echo '}'
echo
echo
echo "# And don't forget to resource your .bashrc / .bash_profile or restart bash"
