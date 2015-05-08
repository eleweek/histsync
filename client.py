#!/usr/bin/env python

# Auto-launching using this: export PROMPT_COMMAND='/Users/putilin/client.py "`fc -nl -1`"'

import requests
import sys

assert len(sys.argv) == 2

USERNAME = "eleweek"
API_KEY = "b85598dd-4f55-48e2-ae32-c87dc8d33013"

payload = {'api_key': API_KEY, 'command_text': sys.argv[1]}
r = requests.post("http://histsync.herokuapp.com/api/v0/user/{}/add_command".format(USERNAME), data=payload)
r.raise_for_status()
