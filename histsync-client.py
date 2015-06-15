#!/usr/bin/env python

import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--api-key", required=True, help="HistSync api key")
parser.add_argument("--user", required=True, help="Your GitHub/HistSync username")
parser.add_argument("--host", help="HistSync host", default="http://histsync.io/")
parser.add_argument("--log-file", help="Log file. If not specified or empty, logging is disabled", default="")
parser.add_argument("command", help="Command to send")
args = parser.parse_args()

shell_pid = os.getppid()

user = args.user
api_key = args.api_key
host = args.host
command_text = args.command

if os.fork() != 0:
    sys.exit()

import logging
import urllib
import urllib2


def upload_command(host, username, api_key, command_text):
    try:
        payload = {'api_key': api_key, 'command': command_text}
        req = urllib2.Request("{}/api/v0/user/{}/commands".format(host, username), urllib.urlencode(payload))
        urllib2.urlopen(req)
    except Exception as e:
        logging.exception(e)


if args.log_file:
    logging.basicConfig(filename=args.log_file, level=logging.DEBUG, format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
else:
    logging.disable(logging.CRITICAL)

logging.error("Test error please ignore!!!")
upload_command(host, user, api_key, command_text)
