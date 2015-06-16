mkdir -p ~/.histsync
for file in {'bash-preexec.sh','histsync-client'}; do
    curl "http://histsync.io/download-client/$file" > ~/.histsync/$file;
done

echo '# Add the following lines in your .bashrc or .bash_profiles'
echo '# ============'
echo '# HistSync'
echo 'source ~/.bash-preexec.sh'
echo 'preexec() {'
echo '    ~/histsync/histsync-client --api-key {{hist_sync_api_key}} --user {{github_username}} "$1" --log-file ~/.histsync/log;'
echo '}'
