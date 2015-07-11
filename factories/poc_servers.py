#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

def cpp_ethereum_server_factory(branch='master'):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/cpp-ethereum.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='cpp-ethereum',
            retry=(5, 3)
        ),
        Configure(
            haltOnFailure=True,
            logEnviron=False,
            command=["cmake", ".", "-DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++", "-DHEADLESS=1"]
        ),
        Compile(
            haltOnFailure=True,
            logEnviron=False,
            command="make -j $(cat /proc/cpuinfo | grep processor | wc -l)"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-install",
            description="installing",
            descriptionDone="install",
            command=["sudo", "make", "install"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="ldconfig",
            description="running ldconfig",
            descriptionDone="ldconfig",
            command=["sudo", "ldconfig"]
        ),
        FileDownload(
            haltOnFailure=True,
            descriptionDone="download init script",
            mastersrc="startup/eth-supervisord-%s.conf" % branch,
            slavedest="eth-supervisord-%s.conf" % branch
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="stop",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'eth-supervisord-%s.conf' | grep -v grep | awk '{print $2}'` && kill `pidof eth` && sleep 5" % branch,
            decodeRC={-1: SUCCESS, 0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="start",
            description="starting",
            descriptionDone="start",
            command="supervisord -c eth-supervisord-%s.conf && sleep 60" % branch,
            logfiles={
                "eth.log": "eth.log",
                "eth.err": "eth.err",
                "supervisord.log": "eth-supervisord.log"
            },
            lazylogfiles=True
        )
    ]: factory.addStep(step)

    return factory
