#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

distributions = ['trusty', 'vivid']

@properties.renderer
def get_cpp_revision(props):
    if 'got_revision' in props:
        return props['got_revision']['cpp-ethereum']
    return None

@properties.renderer
def get_short_revision(props):
    if 'got_revision' in props:
        return props['got_revision']['cpp-ethereum'][:7]
    return None


def testeth_cmd(cmd=[], evmjit=False):
    if evmjit:
        cmd += ['--vm', 'jit']
    return cmd

def cmake_cmd(cmd=[], ccache=True, evmjit=False, headless=True):
    # cmd.append("-DBUNDLE=default")
    cmd.append("-DFATDB=1")
    if headless:
        cmd.append("-DGUI=0")
    if evmjit:
        cmd.append("-DEVMJIT=1")
    elif ccache:
        cmd.append("-DEVMJIT=0")
        cmd.append("-DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++")
    return cmd


def cpp_ethereum_factory(branch='master', deb=False, evmjit=False, headless=True):
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
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/tests.git',
            branch=branch,
            mode='incremental',
            codebase='tests',
            retry=(5, 3),
            workdir='tests'
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-protocol",
            command='sed -ne "s/.*c_protocolVersion = \(.*\);/\\1/p" libethcore/Common.cpp',
            property="protocol"
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-version",
            command='sed -ne "s/^set(PROJECT_VERSION \\"\(.*\)\\")$/\\1/p" CMakeLists.txt',
            property="version"
        ),
        Configure(
            haltOnFailure=True,
            logEnviron=False,
            command=cmake_cmd(["cmake", "."], evmjit=evmjit, headless=headless),
            env={"PATH": "${QTDIR}/bin:${PATH}"}
        ),
        Compile(
            haltOnFailure=True,
            logEnviron=False,
            command="make -j $(cat /proc/cpuinfo | grep processor | wc -l)"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="make-install",
            description="installing",
            descriptionDone="install",
            command=["make", "install"]
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="ldconfig",
            description="running ldconfig",
            descriptionDone="ldconfig",
            command=["ldconfig"]
        ),
        Test(
            haltOnFailure=True,
            warnOnFailure=True,
            logEnviron=False,
            name="test-cpp",
            description="testing",
            descriptionDone="test",
            command=testeth_cmd(["./testeth"], evmjit=evmjit),
            env={
                'CTEST_OUTPUT_ON_FAILURE': '1',
                'ETHEREUM_TEST_PATH': Interpolate('%(prop:workdir)s/tests'),
                'EVMJIT': '-cache=0'
            },
            workdir="build/test",
            maxTime=900
        )
    ]: factory.addStep(step)

    # Trigger check and integration builders
    if not evmjit and not headless:
        for step in [
            Trigger(
                schedulerNames=["cpp-ethereum-%s-check" % branch],
                waitForFinish=False,
                set_properties={
                    "protocol": Interpolate("%(prop:protocol)s"),
                    "version": Interpolate("%(prop:version)s")
                })
        ]: factory.addStep(step)

        # if branch is not 'master':
        #     for step in [
        #         Trigger(
        #             schedulerNames=["cpp-ethereum-integration"],
        #             waitForFinish=False,
        #             set_properties={
        #                 "database": Interpolate("%(prop:database)s"),
        #                 "protocol": Interpolate("%(prop:protocol)s"),
        #                 "version": Interpolate("%(prop:version)s")
        #             })
        #     ]: factory.addStep(step)

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

    # Trigger PoC server buildslave
    if deb and not evmjit and headless:
        for step in [
            Trigger(
                schedulerNames=["cpp-ethereum-%s-server" % branch],
                waitForFinish=False,
                set_properties={
                    "protocol": Interpolate("%(prop:protocol)s"),
                    "version": Interpolate("%(prop:version)s")
                }
            )
        ]: factory.addStep(step)

    return factory


def cpp_check_factory(branch='develop'):
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
        WarningCountingShellCommand(
            logEnviron=False,
            name="cppcheck",
            description="running cppcheck",
            descriptionDone="cppcheck",
            command=["cppcheck", "--force", "--enable=all", "--template", "gcc", "."]
        )
    ]: factory.addStep(step)

    return factory
