#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:18
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-23 16:57:37

import factory
reload(factory)
from factory import *

# Java
def ethereumj_factory(branch='master'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/ethereumj.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='ethereumj',
            retry=(5, 3)
        ),
        ShellCommand(
            logEnviron=False,
            name="build",
            command=["./gradlew", "build", "--debug"],
            description="building",
            descriptionDone="gradlew"
        ),
        ShellCommand(
            logEnviron=False,
            name="install",
            command=["./gradlew", "install", "--debug"],
            description="installing",
            descriptionDone="install"
        )
    ]: factory.addStep(step)

    return factory
