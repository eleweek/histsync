#!/usr/bin/env python

# Auto-launching using this: export PROMPT_COMMAND='/Users/putilin/client.py "`fc -nl -1`"'

import requests
import sys
import os
import re

assert len(sys.argv) == 2

history_output = sys.argv[1]
m = re.match(r"[ ]*(\d+)[ ][ ](.*)", history_output)

command_id = m.group(1)
command_text = m.group(2)


USERNAME = "eleweek"
HOST = "histsync.herokuapp.com"
API_KEY = "61f33ca6-50d3-4eea-a924-e9b7b6f86ed4"

payload = {'api_key': API_KEY, 'command_text': command_text, "id": '{}${}'.format(os.getppid(), command_id)}
print payload
r = requests.post("http://{}/api/v0/user/{}/add_command".format(HOST, USERNAME), data=payload)
r.raise_for_status()
