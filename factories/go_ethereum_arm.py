#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-04-20 22:03:29
# @Last Modified by:   caktux
# @Last Modified time: 2015-04-24 03:00:29

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import get_short_revision_go, _go_cmds


def arm_go_factory(branch='develop', isPullRequest=False):
    factory = BuildFactory()

    env = {
        "GOPATH": Interpolate("%(prop:workdir)s/go:%(prop:workdir)s/build/Godeps/_workspace"),
        "CC": "arm-linux-gnueabi-gcc",
        "GOOS": "linux",
        "GOARCH": "arm",
        "CGO_ENABLED": "1",
        "GOARM": "5",
        'PATH': [Interpolate("%(prop:workdir)s/go/bin"), "${PATH}"]
    }

    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
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
            name="move-src",
            command=_go_cmds(branch=branch),
            description="moving src",
            descriptionDone="move src",
            env={"GOPATH": Interpolate("%(prop:workdir)s/go")}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="build-geth",
            description="building geth",
            descriptionDone="build geth",
            command="go build -v github.com/ethereum/go-ethereum/cmd/geth",
            env=env
        )
    ]: factory.addStep(step)

    # for step in [
    #     ShellCommand(
    #         haltOnFailure=True,
    #         name="go-test",
    #         description="go testing",
    #         descriptionDone="go test",
    #         command="go test github.com/ethereum/go-ethereum/...",
    #         env=env,
    #         maxTime=900
    #     )
    # ]: factory.addStep(step)

    return factory
