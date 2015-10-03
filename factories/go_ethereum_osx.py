#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import _go_cmds


def osx_go_factory(branch='develop', isPullRequest=False):
    factory = BuildFactory()

    env = {
        "GOPATH": Interpolate("%(prop:workdir)s/go:%(prop:workdir)s/build/Godeps/_workspace"),
        'PATH': [Interpolate("%(prop:workdir)s/go/bin"), "${PATH}"]
    }

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
            name="update-version",
            command='gsed -ne "s/^\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" VERSION',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="go-cleanup",
            command=Interpolate("rm -rf %(prop:workdir)s/go"),
            description="cleaning up",
            descriptionDone="clean up",
            env={"GOPATH": Interpolate("%(prop:workdir)s/go")}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="move-src",
            description="moving src",
            descriptionDone="move src",
            command=_go_cmds(branch=branch),
            env={"GOPATH": Interpolate("%(prop:workdir)s/go")}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="install-geth",
            description="installing geth",
            descriptionDone="install geth",
            command="go install -v github.com/ethereum/go-ethereum/cmd/geth",
            env=env
        )
    ]: factory.addStep(step)

    for step in [
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command="go test github.com/ethereum/go-ethereum/...",
            env=env,
            maxTime=900
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for step in [
            Trigger(
                schedulerNames=["go-ethereum-%s-brew" % branch],
                waitForFinish=False,
                set_properties={
                    "version": Interpolate("%(prop:version)s")
                }
            )
        ]: factory.addStep(step)

    return factory
