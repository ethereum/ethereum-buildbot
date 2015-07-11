#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

# Java
def ethereumj_factory(branch='master'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/ethereumj.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='ethereumj',
            retry=(5, 3)
        ),
        ShellCommand(
            logEnviron=False,
            flunkOnFailure=False,
            warnOnFailure=True,
            name="build",
            command=["./gradlew", "build", "--debug"],
            description="building",
            descriptionDone="gradlew"
        ),
        ShellCommand(
            logEnviron=False,
            flunkOnFailure=False,
            warnOnFailure=True,
            name="install",
            command=["./gradlew", "install", "--debug"],
            description="installing",
            descriptionDone="install"
        )
    ]: factory.addStep(step)

    return factory
