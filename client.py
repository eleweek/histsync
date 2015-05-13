#!/usr/bin/env python

# Auto-launching using this: export PROMPT_COMMAND='/Users/putilin/histsync/client.py "`history 1`" >> ~/histsync.log 2>&1'
import os
import sys

shell_pid = os.getppid()

if os.fork() != 0:
    sys.exit()

import requests
import re
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    assert len(sys.argv) == 2

    history_output = sys.argv[1]
    m = re.match(r"[ ]*(\d+)[ ][ ](.*)", history_output)

    command_id = m.group(1)
    command_text = m.group(2)

    USERNAME = "eleweek"
    HOST = "histsync.herokuapp.com"
    API_KEY = "5360f714-c0da-4d64-9aa6-1ec95630ddc3"
    payload = {'api_key': API_KEY, 'command_text': command_text, "id": '{}${}'.format(shell_pid, command_id)}

    r = requests.post("http://{}/api/v0/user/{}/add_command".format(HOST, USERNAME), data=payload)
    r.raise_for_status()
except Exception as e:
    logging.exception(e)
