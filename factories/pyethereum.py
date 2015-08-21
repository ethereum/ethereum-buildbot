#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

# Python
def pyethereum_factory(branch='master'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/pyethereum.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='pyethereum',
            retry=(5, 3)
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-version",
            command='sed -ne "s/.*version=.*[^0-9]\([0-9]*\.[0-9]*\.[0-9]*\).*/\\1/p" setup.py',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pip-requirements",
            description="installing requirements",
            descriptionDone="install requirements",
            command=["pip", "install", "-r", "requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="upgrade-requirements",
            description="upgrading requirements",
            descriptionDone="upgrade requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pip-dev_requirements",
            description="installing dev requirements",
            descriptionDone="install dev requirements",
            command=["pip", "install", "-r", "dev_requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="upgrade-requirements",
            description="upgrading dev requirements",
            descriptionDone="upgrade dev requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "dev_requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pip-install",
            description="installing",
            descriptionDone="install",
            command=["pip", "install", "-e", "."]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="test-submodule",
            descriptionDone="update test submodule",
            command="git submodule init && git submodule update --recursive"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            description="testing",
            descriptionDone="py.test",
            name="py.test",
            command=["py.test"]
        )
    ]: factory.addStep(step)

    return factory
