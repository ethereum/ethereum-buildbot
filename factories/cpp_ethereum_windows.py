#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 15:00:37
# @Last Modified by:   caktux
# @Last Modified time: 2015-04-15 22:59:41

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
            haltOnFailure = True,
            logEnviron = False,
            repourl = 'https://github.com/ethereum/cpp-ethereum.git',
            branch = branch,
            mode = 'full',
            method = 'copy',
            codebase = 'cpp-ethereum',
            retry = (5, 3)
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-database",
            command = [r'C:\\Program Files (x86)\Git\bin\sh.exe', "--login", "-c", r'sed -ne "s/.*c_databaseBaseVersion = \(.*\);/\\1/p" libethcore/Common%s.cpp' % ("Eth" if branch == 'master' else "")],
            property = "database"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-protocol",
            command = [r'C:\\Program Files (x86)\Git\bin\sh.exe', "--login", "-c", r'sed -ne "s/.*c_protocolVersion = \(.*\);/\\1/p" libethcore/Common%s.cpp' % ("Eth" if branch == 'master' else "")],
            property="protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-version",
            command = [r'C:\\Program Files (x86)\Git\bin\sh.exe', "--login", "-c", r'grep "Version" ./libdevcore/Common.cpp | sed "s/.*\"\(.*\)\".*/\1/"'],
            property = "version"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "dependencies",
            description = 'dependencies',
            descriptionDone= 'dependencies',
            command = ['getstuff.bat'],
            workdir="build/extdep"
        ),
        # Configure(
        #     haltOnFailure = True,
        #     logEnviron = False,
        #     command=["cmake", "."],
        #     workdir="build/extdep"
        # ),
        # MsBuild12(
        #     haltOnFailure = True,
        #     logEnviron = False,
        #     projectfile="project.sln",
        #     config="release",
        #     platform="Win32",
        #     workdir="build/extdep"
        # ),
        Configure(
            haltOnFailure = True,
            logEnviron = False,
            command=["cmake", "."]
        ),
        MsBuild12(
            haltOnFailure = True,
            logEnviron = False,
            projectfile="ethereum.sln",
            config="release",
            platform="Win32"
        )
    ]: factory.addStep(step)

    if isPullRequest == False:
        for step in [
            ShellCommand(
                haltOnFailure = True,
                logEnviron = False,
                name = "pack",
                description = 'pack',
                descriptionDone= 'packed',
                command = ['7z', 'a', 'cpp-ethereum.7z', './alethzero/Release/*']
            ),
            SetProperty(
                description="setting filename",
                descriptionDone="set filename",
                name="set-filename",
                property="filename",
                value=Interpolate("AlethZero-Win32-%(kw:time_string)s-%(prop:version)s-%(prop:protocol)s-%(prop:database)s-%(kw:short_revision)s.7z", time_string=get_time_string, short_revision=get_short_revision)
            ),
            FileUpload(
                haltOnFailure = True,
                name = 'upload',
                slavesrc="cpp-ethereum.7z",
                masterdest = Interpolate("public_html/builds/%(prop:buildername)s/%(prop:filename)s"),
                url = Interpolate("/builds/%(prop:buildername)s/%(prop:filename)s")
            ),
            MasterShellCommand(
                name = "clean-latest-link",
                description = 'cleaning latest link',
                descriptionDone= 'clean latest link',
                command = ['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/AlethZero-Win32-latest.7z")]
            ),
            MasterShellCommand(
                haltOnFailure = True,
                name = "link-latest",
                description = 'linking latest',
                descriptionDone= 'link latest',
                command = ['ln', '-sf', Interpolate("%(prop:filename)s"), Interpolate("public_html/builds/%(prop:buildername)s/AlethZero-Win32-latest.7z")]
            )
        ]: factory.addStep(step)

    return factory
