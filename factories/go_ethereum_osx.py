#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *


def osx_go_factory(branch='develop', isPullRequest=False):
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
            name="update-version",
            command='gsed -ne "s/^\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" VERSION',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-clean",
            description="cleaning up",
            descriptionDone="clean up",
            command=["make", "clean"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-all",
            description="installing",
            descriptionDone="install",
            command=["make", "all"]
        ),
        ShellCommand(
            haltOnFailure=True,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command=["make", "test"],
            maxTime=900
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for step in [
            Trigger(
                name='brew-el-capitan',
                schedulerNames=["go-ethereum-%s-el-capitan" % branch],
                waitForFinish=False,
                set_properties={
                    "version": Interpolate("%(prop:version)s")
                }
            )
        ]: factory.addStep(step)

    return factory
