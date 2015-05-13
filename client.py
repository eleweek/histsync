#!/usr/bin/env python

# Auto-launching using this: export PROMPT_COMMAND='/Users/putilin/client.py "`fc -nl -1`"'
import os
import sys

shell_pid = os.getppid()

if os.fork() != 0:
    sys.exit()

import requests
import re
assert len(sys.argv) == 2

history_output = sys.argv[1]
m = re.match(r"[ ]*(\d+)[ ][ ](.*)", history_output)

command_id = m.group(1)
command_text = m.group(2)


USERNAME = "eleweek"
HOST = "histsync.herokuapp.com"
API_KEY = "9b946c76-1688-4d3d-9b13-c4d25ef878ef"
payload = {'api_key': API_KEY, 'command_text': command_text, "id": '{}${}'.format(shell_pid, command_id)}

r = requests.post("http://{}/api/v0/user/{}/add_command".format(HOST, USERNAME), data=payload)
r.raise_for_status()
