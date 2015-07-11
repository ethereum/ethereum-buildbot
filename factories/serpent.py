#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

def serpent_factory(branch='develop'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/serpent.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='serpent',
            retry=(5, 3)
        ),
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/pyethereum.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='pyethereum',
            retry=(5, 3),
            workdir='pyethereum'
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pip-install",
            description="installing",
            descriptionDone="install",
            command=["pip", "install", "-e", "."]
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="serpent-version",
            command=["serpent", "-v"],
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="install-pyethereum",
            description="installing pyethereum",
            descriptionDone="install pyethereum",
            command=["pip", "install", "-e", "."],
            workdir="pyethereum"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pyethereum-requirements",
            description="installing pyethereum requirements",
            descriptionDone="install pyethereum requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "requirements.txt"],
            workdir="pyethereum"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="pyethereum-dev-requirements",
            description="installing pyethereum dev_requirements",
            descriptionDone="install pyethereum dev_requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "dev_requirements.txt"],
            workdir="pyethereum"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="test-submodule",
            descriptionDone="update test submodule",
            command="git submodule init && git submodule update --recursive",
            workdir="pyethereum"
        ),
        ShellCommand(
            flunkOnFailure=False,
            logEnviron=False,
            description="testing",
            descriptionDone="py.test",
            name="py.test",
            command=["py.test"],
            workdir="pyethereum"
        )
    ]: factory.addStep(step)
    return factory
