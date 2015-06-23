#!/bin/bash
mkdir -p ~/.histsync
for file in {'bash-preexec.sh','histsync-client'}; do
    echo Downloading, $file
    curl "http://www.histsync.io/download-client/$file" > ~/.histsync/$file;
done

chmod +x ~/.histsync/histsync-client

read -p 'Github username: ' username
read -p 'API key (from histsync.io profile): ' key

echo
echo
echo '# Add the following lines in your .bashrc / .bash_profiles'
echo '# ============'
echo '# HistSync'
echo 'source ~/.histsync/bash-preexec.sh'
echo 'preexec() {'
echo "    ~/histsync/histsync-client --api-key $key --user $username \"\$1\" --log-file ~/.histsync/log;"
echo '}'

write (){
	echo '# HistSync' >> ~/$configfile
	echo 'source ~/.histsync/bash-preexec.sh' >> ~/$configfile
	echo 'preexec() {' >> ~/$configfile
	echo "    ~/.histsync/histsync-client --api-key $key --user $username \"\$1\" --log-file ~/.histsync/log;" >> ~/$configfile
	echo '}' >> ~/$configfile
	echo
	echo "$(tput setaf 2)"'Done!'; tput sgr0
}

ask (){
read -p 'Would you like to automatically add these lines to the end of your .bashrc / .bash_profile? (y/n) ' add

if [[ "$add" == 'y' ]]; then

	read -p 'Would you like to use your .bashrc (1) or your .bash_profile (2)? (1/2) ' config

	case $config in
		1)
			configfile='.bashrc'
			write
		;;
		2)
			configfile='.bash_profile'
			write
		;;
		*)
			echo "$(tput setaf 1)"'That did not work! You may add it by hand!'; tput sgr0
			exit 1
	esac
fi
}

ask

echo
echo
echo "# Don't forget to resource your .bashrc / .bash_profile or restart bash!"
