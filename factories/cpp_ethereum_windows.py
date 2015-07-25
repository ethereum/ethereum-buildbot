#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import cpp_ethereum
reload(cpp_ethereum)
from cpp_ethereum import *

#
# Windows factories
#
def win_cpp_factory(branch='master', isPullRequest=False):
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
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-protocol",
            command=[r'C:\\Program Files (x86)\Git\bin\sh.exe', "--login", "-c", r'sed -ne "s/.*c_protocolVersion = \(.*\);/\\1/p" libethcore/Common.cpp'],
            property="protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-version",
            command=[r'C:\\Program Files (x86)\Git\bin\sh.exe', "--login", "-c", r'grep "Version" ./libdevcore/Common.cpp | sed "s/.*\"\(.*\)\".*/\1/"'],
            property = "version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="dependencies",
            description='dependencies',
            descriptionDone='dependencies',
            command=['getstuff.bat'],
            workdir="build/extdep"
        ),
        Configure(
            haltOnFailure=True,
            logEnviron=False,
            command=["cmake", ".", "-G", "Visual Studio 12 Win64"]
        ),
        MsBuild12(
            haltOnFailure=True,
            logEnviron=False,
            projectfile="ethereum.sln",
            config="Release",
            platform="x64"
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for step in [
            MsBuild12(
                haltOnFailure=True,
                logEnviron=False,
                name="installer",
                projectfile="PACKAGE.vcxproj",
                config="Release",
                platform="x64"
            ),
            SetProperty(
                description="setting filename",
                descriptionDone="set filename",
                name="set-filename",
                property="filename",
                value=Interpolate("Ethereum (++)-%(prop:version)s-win64-%(kw:time_string)s-%(kw:short_revision)s.exe",
                                  time_string=get_time_string,
                                  short_revision=get_short_revision)
            ),
            FileUpload(
                name="upload",
                slavesrc=Interpolate("Ethereum (++)-%(prop:version)s-win64.exe"),
                masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:filename)s"),
                url=Interpolate("/builds/%(prop:buildername)s/%(prop:filename)s")
            ),
            MasterShellCommand(
                name="clean-latest-link",
                description='cleaning latest link',
                descriptionDone='clean latest link',
                command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/Ethereum (++)-win64-latest.exe")]
            ),
            MasterShellCommand(
                haltOnFailure=True,
                name="link-latest",
                description='linking latest',
                descriptionDone='link latest',
                command=['ln', '-sf', Interpolate("%(prop:filename)s"), Interpolate("public_html/builds/%(prop:buildername)s/Ethereum (++)-win64-latest.exe")]
            )
        ]: factory.addStep(step)

    return factory
