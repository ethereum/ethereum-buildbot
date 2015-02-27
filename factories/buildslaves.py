#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 15:05:40
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-26 23:17:11

import factory
reload(factory)
from factory import *

@properties.renderer
def _buildslave_stop_cmd(props):
    if props.has_key('last-container'):
        cmds = []
        for container in props['last-container'].splitlines():
            cmds.append("docker stop %s" % container)
        return " && ".join(cmds)
    return None

#
# Buildslave factories
#
def buildslave_factory(lang="cpp", client="cpp-ethereum"):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/ethereum-dockers.git',
            mode='incremental',
            codebase='ethereum-dockers',
            retry=(5, 3)
        ),
        ShellCommand(
            flunkOnFailure = False,
            logEnviron = False,
            name="cleanup-containers",
            description="cleaning up containers",
            descriptionDone="clean up containers",
            command="docker rm $(docker ps -a -q)",
            decodeRC={0:SUCCESS, 1:WARNINGS, 123:WARNINGS}
        ),
        ShellCommand(
            flunkOnFailure = False,
            logEnviron = False,
            name="cleanup-images",
            description="cleaning up images",
            descriptionDone="clean up images",
            command="docker rmi $(docker images -f 'dangling=true' -q)",
            decodeRC={0:SUCCESS, 1:WARNINGS, 123:WARNINGS}
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="docker-%s" % lang,
            description="building %s base" % lang,
            descriptionDone="build %s base" % lang,
            command=["docker", "build", "--no-cache", "-t", "cptobvious/%s-base" % client, "%s-base" % client],
            timeout=1800
        ),
        ShellCommand(
            logEnviron = False,
            name="docker-%s-push" % lang,
            command=["docker", "push", "cptobvious/%s-base" % client],
            warnOnFailure=True,
            decodeRC={0:SUCCESS, 1:WARNINGS}
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="last-container",
            command="docker ps -a | grep buildslave-%s | awk '{print $1}'" % lang,
            property="last-container"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="buildslave-%s" % lang,
            description="building %s buildslave" % lang,
            descriptionDone="build %s buildslave" % lang,
            command=["docker", "build", "--no-cache", "-t", "cptobvious/buildslave-%s" % lang, "%s-buildslave" % client],
            timeout=1800
        )
    ]: factory.addStep(step)

    # Use when dependencies differ between master and develop
    if lang in ['cpp', 'go']:
        for step in [
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-develop" % lang,
                description="building %s develop buildslave" % lang,
                descriptionDone="build %s develop buildslave" % lang,
                command=["docker", "build", "--no-cache", "-t", "cptobvious/buildslave-%s-develop" % lang, "%s-buildslave-develop" % client],
                timeout=1800
            )
        ]: factory.addStep(step)

    if lang in ['cpp', 'go']:
        factory.addStep(
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-deb" % lang,
                description="building %s deb buildslave" % lang,
                descriptionDone="build %s deb buildslave" % lang,
                command=["docker", "build", "--no-cache", "-t", "cptobvious/buildslave-%s-deb" % lang, "%s-buildslave-deb" % client]
            ))

    if lang in ['cpp']:
        factory.addStep(
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-integration" % lang,
                description="building %s integration buildslave" % lang,
                descriptionDone="build %s integration buildslave" % lang,
                command=["docker", "build", "--no-cache", "-t", "cptobvious/buildslave-%s-integration" % lang, "%s-buildslave-integration" % client]
            ))

    for step in [
        ShellCommand(
            warnOnFailure = True,
            logEnviron = False,
            name="buildslave-%s-pr" % lang,
            description="building %s pr buildslave" % lang,
            descriptionDone="build %s pr buildslave" % lang,
            command=["docker", "build", "--no-cache", "-t", "cptobvious/buildslave-%s-pr" % lang, "%s-buildslave-pr" % client]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="buildslave-%s-stop" % lang,
            description="stopping %s buildslave" % lang,
            descriptionDone="stop %s buildslave" % lang,
            command=_buildslave_stop_cmd,
            decodeRC={0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="buildslave-%s-run" % lang,
            description="starting %s buildslave" % lang,
            descriptionDone="start %s buildslave" % lang,
            command=["docker", "run", "-d", "-t", "cptobvious/buildslave-%s" % lang]
        ),
        ShellCommand(
            warnOnFailure = True,
            logEnviron = False,
            name="buildslave-%s-pr-run" % lang,
            description="starting %s pr buildslave" % lang,
            descriptionDone="start %s pr buildslave" % lang,
            command=["docker", "run", "-d", "-t", "cptobvious/buildslave-%s-pr" % lang]
        )
    ]: factory.addStep(step)

    # Use when dependencies differ between master and develop
    if lang in ['cpp', 'go']:
        for step in [
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-develop-run" % lang,
                description="starting %s develop buildslave" % lang,
                descriptionDone="start %s develop buildslave" % lang,
                command=["docker", "run", "-d", "-t", "cptobvious/buildslave-%s-develop" % lang]
            )
        ]: factory.addStep(step)

    if lang in ['cpp', 'go']:
        for step in [
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-deb-run" % lang,
                description="starting %s deb buildslave" % lang,
                descriptionDone="start %s deb buildslave" % lang,
                command=["docker", "run", "-d", "--privileged=true", "-t", "cptobvious/buildslave-%s-deb" % lang]
            )
        ]: factory.addStep(step)

    if lang in ['cpp']:
        for step in [
            ShellCommand(
                warnOnFailure = True,
                logEnviron = False,
                name="buildslave-%s-integration-run" % lang,
                description="starting %s integration buildslave" % lang,
                descriptionDone="start %s integration buildslave" % lang,
                command=["docker", "run", "-d", "-t", "cptobvious/buildslave-%s-integration" % lang]
            )
        ]: factory.addStep(step)

    return factory
