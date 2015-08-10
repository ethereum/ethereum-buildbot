#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import get_short_revision_go

def _go_cmds_win(branch='master'):
    cmds = [
        "mkdir %GOPATH%\\src\\github.com\\ethereum",
        "xcopy /S/E *.* %GOPATH%\\src\\github.com\\ethereum\\go-ethereum\\"
    ]

    return " && ".join(cmds)

def windows_go_factory(branch='develop', isPullRequest=False):
    factory = BuildFactory()

    env = {
        "GOPATH": Interpolate("%(prop:workdir)s\\go;%(prop:workdir)s\\build\\Godeps\\_workspace"),
        'PATH': [Interpolate("%(prop:workdir)s\\go\\bin"), "${PATH}"]
    }

    sed = '"C:\\Program Files (x86)\\GnuWin32\\bin\\sed.exe"'
    zip_ = '"C:\\Program Files (x86)\\GnuWin32\\bin\\zip.exe"'

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
            command='%s -ne "s/.*Version.*=\s*[^0-9]\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" cmd\geth\main.go' % sed,
            property = "version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="go-cleanup",
            command=Interpolate("rd /s /q %(prop:workdir)s\\go && mkdir %(prop:workdir)s\\go"),
            description="cleaning up",
            descriptionDone="clean up"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="move-src",
            description="moving src",
            descriptionDone="move src",
            command=_go_cmds_win(branch=branch),
            env={"GOPATH": Interpolate("%(prop:workdir)s\go")}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="build-geth",
            description="building geth",
            descriptionDone="build geth",
            command="go build -v github.com\ethereum\go-ethereum\cmd\geth",
            env=env
        )
    ]: factory.addStep(step)

    for step in [
        ShellCommand(
            flunkOnFailure=False,
            warnOnFailure=True,
            logEnviron=False,
            name="go-test",
            description="go testing",
            descriptionDone="go test",
            command="go test github.com\ethereum\go-ethereum\...",
            env=env,
            maxTime=900
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="zip",
                description='zipping',
                descriptionDone='zipped',
                command="%s geth.zip geth.exe" % zip_
            ),
            SetProperty(
                description="setting filename",
                descriptionDone="set filename",
                name="set-filename",
                property="filename",
                value=Interpolate("Geth-Win64-%(kw:time_string)s-%(prop:version)s-%(kw:short_revision)s.zip",
                                  time_string=get_time_string,
                                  short_revision=get_short_revision_go)
            ),
            FileUpload(
                haltOnFailure=True,
                name='upload',
                slavesrc="geth.zip",
                masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:filename)s"),
                url=Interpolate("/builds/%(prop:buildername)s/%(prop:filename)s")
            ),
            MasterShellCommand(
                name="clean-latest-link",
                description='cleaning latest link',
                descriptionDone='clean latest link',
                command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/Geth-Win64-latest.zip")]
            ),
            MasterShellCommand(
                haltOnFailure=True,
                name="link-latest",
                description='linking latest',
                descriptionDone='link latest',
                command=['ln', '-sf', Interpolate("%(prop:filename)s"), Interpolate("public_html/builds/%(prop:buildername)s/Geth-Win64-latest.zip")]
            )
        ]: factory.addStep(step)

    return factory
