#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:15
# @Last Modified by:   caktux
# @Last Modified time: 2015-03-03 16:57:35

import factory
reload(factory)
from factory import *

# Python
def pyethereum_factory(branch='master'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/pyethereum.git',
            branch=branch,
            mode='full',
            method = 'copy',
            codebase='pyethereum',
            retry=(5, 3)
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="pip-requirements",
            description="installing requirements",
            descriptionDone="install requirements",
            command=["pip", "install", "-r", "requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="upgrade-requirements",
            description="upgrading test requirements",
            descriptionDone="upgrade test requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="pip-install",
            description="installing",
            descriptionDone="install",
            command=["pip", "install", "-e", "."]
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="pyeth-version",
            command=["pyeth", "-v"],
            property="version"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="test-requirements",
            description="installing test requirements",
            descriptionDone="install test requirements",
            command=["pip", "install", "-r", "dev_requirements.txt"]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="test-submodule",
            descriptionDone="update test submodule",
            command="git submodule init && git submodule update --recursive"
        ),
        Test(
            flunkOnFailure = False,
            logEnviron = False,
            description="testing",
            descriptionDone="py.test",
            name="test-py.test",
            command="py.test"
        )
    ]: factory.addStep(step)

    return factory
