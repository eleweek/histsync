#!/usr/bin/env python

import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--api_key", required=True, help="HistSync api key")
parser.add_argument("--user", required=True, help="Your GitHub/HistSync username")
parser.add_argument("--host", help="HistSync host", default="http://histsync.herokuapp.com")
parser.add_argument("command", help="Command to send")
args = parser.parse_args()

shell_pid = os.getppid()

user = args.user
api_key = args.api_key
host = args.host
command_text = args.command

if os.fork() != 0:
    sys.exit()

import requests
import logging


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    logger.addHandler(ch)


def upload_command(host, username, api_key, command_text):
    try:
        payload = {'api_key': api_key, 'command_text': command_text}
        r = requests.post("{}/api/v0/user/{}/add_command".format(host, username), data=payload)

        r.raise_for_status()
    except Exception as e:
        logging.exception(e)


setup_logging()
upload_command(host, user, api_key, command_text)
