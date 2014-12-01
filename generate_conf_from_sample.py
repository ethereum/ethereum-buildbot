#!/usr/bin/python

# generates the config files from templates. Useful when you do config testing of buildbot

from shutil import copyfile


copyfile('slaves.json.sample','slaves.json')
copyfile('users.json.sample','users.json')
copyfile('ircbot.json.sample','ircbot.json')
copyfile('tokens.json.sample','tokens.json')
