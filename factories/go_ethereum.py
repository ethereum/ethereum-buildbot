#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:08
# @Last Modified by:   caktux
# @Last Modified time: 2015-03-04 14:18:47

import factory
reload(factory)
from factory import *

@properties.renderer
def get_short_revision_go(props):
    if props.has_key('got_revision'):
        return props['got_revision']['go-ethereum'][:7]
    return None


def _go_cmds(branch='master'):
    cmds = [
        "mkdir -p $GOPATH/src/github.com/ethereum",
        "cp -a . $GOPATH/src/github.com/ethereum/go-ethereum",
        "rm -rf $GOPATH/pkg"
    ]

    return " && ".join(cmds)


def go_ethereum_factory(branch='master', deb=False):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/go-ethereum.git',
            branch=branch,
            mode='full',
            method = 'copy',
            codebase='go-ethereum',
            retry=(5, 3)
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-protocol",
            command = 'sed -ne "s/.*ProtocolVersion    = \(.*\)/\\1/p" eth/protocol.go',
            property = "protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-p2p",
            command = 'sed -ne "s/.*baseProtocolVersion.*= \(.*\)/\\1/p" p2p/protocol.go',
            property = "p2p"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-version",
            command = 'sed -ne "s/.*Version.*= \\"\(.*\)\\"/\\1/p" cmd/ethereum/main.go',
            property = "version"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="go-cleanup",
            command="rm -rf $GOPATH",
            description="cleaning up",
            descriptionDone="clean up"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "move-src",
            command=_go_cmds(branch=branch),
            description="moving src",
            descriptionDone="move src"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="install-ethereum",
            description="installing ethereum",
            descriptionDone="install ethereum",
            command="go install -v github.com/ethereum/go-ethereum/cmd/ethereum",
            env={"GOPATH": Interpolate("${GOPATH}:%(prop:workdir)s/build/Godeps/_workspace")}
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="install-mist",
            description="installing mist",
            descriptionDone="install mist",
            command="go install -v github.com/ethereum/go-ethereum/cmd/mist",
            env={"GOPATH": Interpolate("${GOPATH}:%(prop:workdir)s/build/Godeps/_workspace")}
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command="go test github.com/ethereum/go-ethereum/...",
            decodeRC={0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),
    ]: factory.addStep(step)

    if deb:
        for architecture in ['i386', 'amd64']:
            for distribution in ['trusty', 'utopic']:
                for step in [
                    Trigger(
                        schedulerNames=["go-ethereum-%s-%s-%s" % (branch, architecture, distribution)],
                        waitForFinish=False,
                        set_properties={
                            "version": Interpolate("%(prop:version)s")
                        }
                    )
                ]: factory.addStep(step)

    for step in [
        FileDownload(
            haltOnFailure = True,
            descriptionDone="download init script",
            mastersrc="eth-go-supervisord.conf",
            slavedest="eth-go-supervisord.conf"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'supervisord -c eth-go-supervisord.conf' | grep -v grep | awk '{print $2}'` && kill `pidof ethereum` && sleep 5",
            decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="start",
            description="starting",
            descriptionDone="start",
            command="supervisord -c eth-go-supervisord.conf && sleep 15",
            logfiles={
                "ethereum.log": "ethereum.log",
                "ethereum.err": "ethereum.err",
                "supervisord.log": "eth-go-supervisord.log"
            },
            lazylogfiles=True
        )
    ]: factory.addStep(step)

    return factory
