#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:08
# @Last Modified by:   caktux
# @Last Modified time: 2015-04-21 03:02:13

import factory
reload(factory)
from factory import *

distributions = ['trusty', 'utopic', 'vivid']

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


def go_ethereum_factory(branch='master', deb=False, headless=True):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/go-ethereum.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='go-ethereum',
            retry=(5, 3)
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-protocol",
            command='sed -ne "s/.*ProtocolVersion    = \(.*\)/\\1/p" eth/protocol.go',
            property="protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-p2p",
            command='sed -ne "s/.*baseProtocolVersion.*= \(.*\)/\\1/p" p2p/peer.go',
            property="p2p"
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-version",
            command='sed -ne "s/.*Version.*=\s*[^0-9]\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" cmd/geth/main.go',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="go-cleanup",
            command="rm -rf $GOPATH",
            description="cleaning up",
            descriptionDone="clean up"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="move-src",
            command=_go_cmds(branch=branch),
            description="moving src",
            descriptionDone="move src"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="install-geth",
            description="installing geth",
            descriptionDone="install geth",
            command="go install -v github.com/ethereum/go-ethereum/cmd/geth",
            env={"GOPATH": Interpolate("${GOPATH}:%(prop:workdir)s/build/Godeps/_workspace")}
        )
    ]: factory.addStep(step)

    if not headless:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="install-mist",
                description="installing mist",
                descriptionDone="install mist",
                command="go install -v github.com/ethereum/go-ethereum/cmd/mist",
                env={"GOPATH": Interpolate("${GOPATH}:%(prop:workdir)s/build/Godeps/_workspace")}
            )
        ]: factory.addStep(step)

    for step in [
        ShellCommand(
            haltOnFailure=True,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command="go test github.com/ethereum/go-ethereum/...",
            env={"GOPATH": Interpolate("${GOPATH}:%(prop:workdir)s/build/Godeps/_workspace")},
            maxTime=900
        )
    ]: factory.addStep(step)

    if deb and headless:
        for architecture in ['i386', 'amd64']:
            for distribution in distributions:
                for step in [
                    Trigger(
                        schedulerNames=["go-ethereum-%s-%s-%s" % (branch, architecture, distribution)],
                        waitForFinish=False,
                        set_properties={
                            "version": Interpolate("%(prop:version)s")
                        }
                    )
                ]: factory.addStep(step)

    if headless:
        for step in [
            FileDownload(
                haltOnFailure=True,
                descriptionDone="download init script",
                mastersrc="startup/geth-supervisord.conf",
                slavedest="geth-supervisord.conf"
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="stop",
                description="stopping",
                descriptionDone="stop",
                command="kill `ps aux | grep 'supervisord -c geth-supervisord.conf' | grep -v grep | awk '{print $2}'` && kill `pidof geth` && sleep 5",
                decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="start",
                description="starting",
                descriptionDone="start",
                command="supervisord -c geth-supervisord.conf && sleep 15",
                logfiles={
                    "geth.log": "geth.log",
                    "geth.err": "geth.err",
                    "supervisord.log": "geth-supervisord.log"
                },
                lazylogfiles=True
            )
        ]: factory.addStep(step)

    return factory
