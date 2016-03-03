#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

#
# Self-update factory
#
def self_update_factory():
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            name='update',
            repourl='https://github.com/ethereum/ethereum-buildbot.git',
            mode='incremental',
            codebase='ethereum-buildbot',
            retry=(5, 3)
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name='copy-samples',
            description='copying samples',
            descriptionDone='copy samples',
            command='cp slaves.json.sample slaves.json && cp users.json.sample users.json && '
                    'cp ircbot.json.sample ircbot.json && cp tokens.json.sample tokens.json && '
                    'cp changehook.passwd.sample changehook.passwd'
        ),
        ShellCommand(
            logEnviron=False,
            name='check',
            description='running checkconfig',
            descriptionDone='checkconfig',
            command=['buildbot', 'checkconfig', '.'],
            flunkOnWarnings=True,
            flunkOnFailure=True,
            haltOnFailure=True,
            warnOnFailure=False,
            interruptSignal=15
        ),
        MasterShellCommand(
            haltOnFailure=True,
            name='live-update',
            description='updating',
            descriptionDone='update',
            command=['git', 'pull']
        ),
        MasterShellCommand(
            haltOnFailure=True,
            name='reload',
            description='reloading',
            descriptionDone='reload',
            command=['buildbot', 'reconfig', '.']
        )
    ]: factory.addStep(step)

    return factory
