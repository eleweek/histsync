mkdir -p ~/.histsync
for file in {'bash-preexec.sh','histsync-client'}; do
    curl "http://histsync.io/download-client/$file" > ~/.histsync/$file;
done
