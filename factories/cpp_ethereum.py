#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:50:04
# @Last Modified by:   caktux
# @Last Modified time: 2015-04-05 23:10:42

import factory
reload(factory)
from factory import *

distributions = ['trusty', 'utopic', 'vivid']

@properties.renderer
def get_cpp_revision(props):
    if props.has_key('got_revision'):
        return props['got_revision']['cpp-ethereum']
    return None

@properties.renderer
def get_short_revision(props):
    if props.has_key('got_revision'):
        return props['got_revision']['cpp-ethereum'][:7]
    return None


def testeth_cmd(cmd=[], evmjit=False):
    if evmjit:
        cmd.append("--jit")
    return cmd

def cmake_cmd(cmd=[], ccache=True, evmjit=False, headless=True):
    cmd.append("-DFATDB=1")
    cmd.append("-DBUNDLE=default")
    if headless:
        cmd.append("-DGUI=0")
    if evmjit:
        cmd.append("-DLLVM_DIR=/usr/share/llvm-3.5/cmake")
        cmd.append("-DEVMJIT=1")
    elif ccache:
        cmd.append("-DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++")
    return cmd


def cpp_ethereum_factory(branch='master', deb=False, evmjit=False, headless=True):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/cpp-ethereum.git',
            branch=branch,
            mode='full',
            method = 'copy',
            codebase='cpp-ethereum',
            retry=(5, 3)
        ),
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/tests.git',
            branch=branch,
            mode='incremental',
            codebase='tests',
            retry=(5, 3),
            workdir='tests'
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-database",
            command = 'sed -ne "s/.*c_databaseBaseVersion = \(.*\);/\\1/p" libethcore/Common%s.cpp' % ("Eth" if branch == 'master' else ""),
            property = "database"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-protocol",
            command='sed -ne "s/.*c_protocolVersion = \(.*\);/\\1/p" libethcore/Common%s.cpp' % ("Eth" if branch == 'master' else ""),
            property="protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "set-version",
            command='sed -ne "s/.*Version = \\"\(.*\)\\";/\\1/p" libdevcore/Common.cpp',
            property="version"
        ),
        Configure(
            haltOnFailure = True,
            logEnviron = False,
            command=cmake_cmd(["cmake", "."], evmjit=evmjit, headless=headless),
            env={"PATH": "${QTDIR}/bin:${PATH}"}
        ),
        Compile(
            haltOnFailure = True,
            logEnviron = False,
            command="make -j $(cat /proc/cpuinfo | grep processor | wc -l)"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "make-install",
            description="installing",
            descriptionDone="install",
            command=["make", "install"]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name = "ldconfig",
            description="running ldconfig",
            descriptionDone="ldconfig",
            command=["ldconfig"]
        ),
        Test(
            haltOnFailure = True,
            warnOnFailure = True,
            logEnviron = False,
            name="test-cpp-strict",
            description="strict testing",
            descriptionDone="strict test",
            command=testeth_cmd(["./testeth", "-t", "devcrypto,jsonrpc,Solidity*,whisper"], evmjit=evmjit),
            env={'CTEST_OUTPUT_ON_FAILURE': '1', 'ETHEREUM_TEST_PATH': Interpolate('%(prop:workdir)s/tests')},
            workdir="build/test"
        )
    ]: factory.addStep(step)

    # Trigger check and integration builders
    if not evmjit and not headless:
        for step in [
            Trigger(
                schedulerNames=["cpp-ethereum-%s-check" % branch],
                waitForFinish=False,
                set_properties={
                    "database": Interpolate("%(prop:database)s"),
                    "protocol": Interpolate("%(prop:protocol)s"),
                    "version": Interpolate("%(prop:version)s")
                })
        ]: factory.addStep(step)

        if branch is not 'master':
            for step in [
                Trigger(
                    schedulerNames=["cpp-ethereum-integration"],
                    waitForFinish=False,
                    set_properties={
                        "database": Interpolate("%(prop:database)s"),
                        "protocol": Interpolate("%(prop:protocol)s"),
                        "version": Interpolate("%(prop:version)s")
                    })
            ]: factory.addStep(step)

    # Trigger deb builders
    if not evmjit and headless:
        if deb:
            for architecture in ['i386', 'amd64']:
                for distribution in distributions:
                    for step in [
                        Trigger(
                            schedulerNames=["cpp-ethereum-%s-%s-%s" % (branch, architecture, distribution)],
                            waitForFinish=False,
                            set_properties={
                                "version": Interpolate("%(prop:version)s")
                            })
                    ]: factory.addStep(step)

    # Run all tests, warnings let the build pass, failures marks the build with warnings
    for step in [
        ShellCommand(
            flunkOnFailure = False,
            warnOnFailure = True,
            logEnviron = False,
            name="test-cpp",
            description="testing",
            descriptionDone="test",
            command=testeth_cmd(["./testeth"], evmjit=evmjit),
            env={'CTEST_OUTPUT_ON_FAILURE': '1', 'ETHEREUM_TEST_PATH': Interpolate('%(prop:workdir)s/tests')},
            workdir="build/test",
            decodeRC={0:SUCCESS, -1:WARNINGS, 1:WARNINGS, 201:WARNINGS},
            maxTime=900
        )
    ]: factory.addStep(step)

    # Trigger PoC server buildslave and a test node
    if deb and not evmjit and headless:
        for step in [
            Trigger(
                schedulerNames=["cpp-ethereum-%s-server" % branch],
                waitForFinish=False,
                set_properties={
                    "database": Interpolate("%(prop:database)s"),
                    "protocol": Interpolate("%(prop:protocol)s"),
                    "version": Interpolate("%(prop:version)s")
                }
            ),
            FileDownload(
                haltOnFailure = True,
                descriptionDone="download init script",
                mastersrc="startup/eth-supervisord.conf",
                slavedest="eth-supervisord.conf"
            ),
            ShellCommand(
                haltOnFailure = True,
                logEnviron = False,
                name="stop",
                description="stopping",
                descriptionDone="stop",
                command="kill `ps aux | grep 'supervisord -c eth-supervisord.conf' | grep -v grep | awk '{print $2}'` && kill `pidof eth` && sleep 5",
                decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
            ),
            ShellCommand(
                haltOnFailure = True,
                logEnviron = False,
                name="start",
                description="starting",
                descriptionDone="start",
                command="supervisord -c eth-supervisord.conf && sleep 15",
                logfiles={
                    "eth.log": "eth.log",
                    "eth.err": "eth.err",
                    "supervisord.log": "eth-supervisord.log"
                },
                lazylogfiles=True
            )
        ]: factory.addStep(step)

    return factory


def cpp_check_factory(branch='develop'):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/cpp-ethereum.git',
            branch=branch,
            mode='full',
            method = 'copy',
            codebase='cpp-ethereum',
            retry=(5, 3)
        ),
        WarningCountingShellCommand(
            logEnviron = False,
            name="cppcheck",
            description="running cppcheck",
            descriptionDone="cppcheck",
            command=["cppcheck", "--force", "--enable=all", "--template", "gcc", "."]
        )
    ]: factory.addStep(step)

    return factory
