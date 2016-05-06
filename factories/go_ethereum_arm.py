#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import get_short_revision_go


def arm_go_factory(branch='develop', isPullRequest=False):
    factory = BuildFactory()

    env = {
        "CC": "arm-linux-gnueabi-gcc-5",
        "GOOS": "linux",
        "GOARCH": "arm",
        "GOARM": "5",
        "CGO_ENABLED": "1"
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
            name="set-version",
            command='sed -ne "s/^\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" VERSION',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-clean",
            command=["make", "clean"],
            description="cleaning up",
            descriptionDone="clean up"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-all",
            description="installing",
            descriptionDone="install",
            command=["make", "all"],
            env=env
        ),
        ShellCommand(
            haltOnFailure=True,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command=["make", "test"],
            maxTime=900,
            env=env
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="tar-geth",
                description='packing',
                descriptionDone='pack',
                command=['tar', '-cjf', 'geth.tar.bz2', 'build/bin/geth']
            ),
            SetPropertyFromCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="set-sha256sum",
                command=Interpolate('sha256sum geth.tar.bz2 | grep -o -w "\w\{64\}"'),
                property='sha256sum'
            ),
            SetProperty(
                description="setting filename",
                descriptionDone="set filename",
                name="set-filename",
                property="filename",
                value=Interpolate("geth-ARM-%(kw:time_string)s-%(prop:version)s-%(kw:short_revision)s.tar.bz2",
                                  time_string=get_time_string,
                                  short_revision=get_short_revision_go)
            ),
            FileUpload(
                haltOnFailure=True,
                name='upload-geth',
                slavesrc="geth.tar.bz2",
                masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:filename)s"),
                url=Interpolate("/builds/%(prop:buildername)s/%(prop:filename)s")
            ),
            MasterShellCommand(
                name="clean-latest-link",
                description='cleaning latest link',
                descriptionDone='clean latest link',
                command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/geth-ARM-latest.tar.bz2")]
            ),
            MasterShellCommand(
                haltOnFailure=True,
                name="link-latest",
                description='linking latest',
                descriptionDone='link latest',
                command=['ln', '-sf', Interpolate("%(prop:filename)s"), Interpolate("public_html/builds/%(prop:buildername)s/geth-ARM-latest.tar.bz2")]
            )
        ]: factory.addStep(step)

    return factory
