#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:30
# @Last Modified by:   caktux
# @Last Modified time: 2015-03-03 16:57:25

import factory
reload(factory)
from factory import *

@properties.renderer
def _serpent_tests(props):
    cmds = []
    contracts = [
        "crowdfund",
        "datafeed",
        "namecoin",
        "subcurrency",
        "schellingcoin/schellingdollar"
    ]
    for contract in contracts:
        cmds.append("printf '\\n\\npretty_compile contract:\\n' && serpent pretty_compile contract.se && printf '\\ncompile contract:\\n' && serpent compile contract.se".replace("contract", contract))
    tests = [
        "ecc/test.py"
    ]
    for test in tests:
        cmds.append("printf '\\n\\npy.test zetest:\\n' && py.test zetest".replace("zetest", test))
    return " && ".join(cmds)

def serpent_factory(branch='master'):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/serpent.git',
            branch='master',
            mode='full',
            method = 'copy',
            codebase='serpent',
            retry=(5, 3)
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
            name="serpent-version",
            command=["serpent", "-v"],
            property="version"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="test-requirements",
            description="installing test requirements",
            descriptionDone="install test requirements",
            command="pip install pytest && pip install --upgrade --no-deps pyethereum"
        ),
        Test(
            flunkOnFailure = False,
            logEnviron = False,
            command=_serpent_tests,
            description="testing",
            descriptionDone="test",
            workdir="build/examples"
        )
    ]: factory.addStep(step)
    return factory

