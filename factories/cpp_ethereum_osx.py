#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import cpp_ethereum
reload(cpp_ethereum)
from cpp_ethereum import *

def cmake_osx_cmd(cmd=[], ccache=True, evmjit=False, headless=True):
    # cmd.append("-DBUNDLE=default")
    cmd.append("-DFATDB=1")
    cmd.append("-DETHASHCL=1")
    if headless:
        cmd.append("-DGUI=0")
    if evmjit:
        cmd += [
            "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
            "-DLLVM_DIR=/usr/local/opt/llvm/share/llvm/cmake",
            "-DEVMJIT=1"
        ]
    elif ccache:
        cmd.append("-DCMAKE_CXX_COMPILER=/usr/local/opt/ccache/libexec/g++")
    return cmd

def osx_cpp_check_factory(branch='develop'):
    factory = BuildFactory()

    scan_build_path = "/usr/local/opt/llvm/share/clang/tools/scan-build"
    analyzer = "c++-analyzer"

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
        Configure(
            haltOnFailure=True,
            logEnviron=False,
            command=["cmake", ".", "-DCMAKE_CXX_COMPILER=%s/%s" % (scan_build_path, analyzer)]
        ),
        Compile(
            logEnviron=False,
            name="scan-build",
            command=["%s/scan-build" % scan_build_path, "--use-analyzer=%s/%s" % (scan_build_path, analyzer), "make", "-j", "6"]
        )
    ]: factory.addStep(step)

    return factory

# C++
def osx_cpp_factory(branch='develop', isPullRequest=False, evmjit=False, headless=True):
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
            name="set-version",
            command='sed -ne "s/^set(PROJECT_VERSION \\"\(.*\)\\")$/\\1/p" CMakeLists.txt',
            property="version"
        ),
        Configure(
            haltOnFailure=True,
            logEnviron=False,
            command = cmake_osx_cmd(['cmake', '.'], evmjit=evmjit, headless=headless)
        ),
        Compile(
            haltOnFailure=True,
            logEnviron=False,
            command="make -j $(sysctl -n hw.ncpu)"
        )
    ]: factory.addStep(step)

    if not headless:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="make-install",
                description='running make install',
                descriptionDone='make install',
                command=['make', 'install'],
                workdir='build/alethzero'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="make-install-mix",
                description='running mix make install',
                descriptionDone='make install mix',
                command=['make', 'install'],
                workdir='build/mix'
            )
        ]: factory.addStep(step)

    for step in [
        Test(
            haltOnFailure=True,
            warnOnFailure=True,
            logEnviron=False,
            name="test-cpp",
            description="testing",
            descriptionDone="test",
            command=testeth_cmd(["./testeth"], evmjit=evmjit),
            env={'CTEST_OUTPUT_ON_FAILURE': '1', 'ETHEREUM_TEST_PATH': Interpolate('%(prop:workdir)s/tests')},
            workdir="build/test",
            maxTime=900
        ),
    ]: factory.addStep(step)

    # Trigger check
    if not evmjit and not headless:
        for step in [
            Trigger(
                schedulerNames=["cpp-ethereum-%s-osx-check" % branch],
                waitForFinish=False,
                set_properties={
                    "version": Interpolate("%(prop:version)s")
                }
            )
        ]: factory.addStep(step)

    # Trigger deb builders
    if not evmjit and headless:
        if not isPullRequest:
            for step in [
                Trigger(
                    schedulerNames=["cpp-ethereum-%s-brew" % branch],
                    waitForFinish=False,
                    set_properties={
                        "version": Interpolate("%(prop:version)s")
                    }
                )
            ]: factory.addStep(step)

    # Package AlethZero.app
    if not isPullRequest and not headless:
        for step in [
            Compile(
                haltOnFailure=True,
                logEnviron=False,
                command="make -j $(sysctl -n hw.ncpu) appdmg"
            ),
            SetPropertyFromCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="set-sha1sum",
                command=Interpolate('sha1sum Ethereum.dmg | grep -o -w "\w\{40\}"'),
                property='sha1sum'
            ),
            SetProperty(
                description="setting filename",
                descriptionDone="set filename",
                name="set-filename",
                property="filename",
                value=Interpolate("AlethZero-OSX-%(kw:time_string)s-%(prop:version)s-%(kw:short_revision)s.dmg",
                                  time_string=get_time_string,
                                  short_revision=get_short_revision)
            ),
            FileUpload(
                haltOnFailure=True,
                name='upload-alethzero',
                slavesrc="Ethereum.dmg",
                masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:filename)s"),
                url=Interpolate("builds/%(prop:buildername)s/%(prop:filename)s")
            ),
            MasterShellCommand(
                name="clean-latest-link",
                description='cleaning latest link',
                descriptionDone='clean latest link',
                command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/AlethZero-OSX-latest.dmg")]
            ),
            MasterShellCommand(
                haltOnFailure=True,
                name="link-latest",
                description='linking latest',
                descriptionDone='link latest',
                command=['ln', '-sf', Interpolate("%(prop:filename)s"), Interpolate("public_html/builds/%(prop:buildername)s/AlethZero-OSX-latest.dmg")]
            )
        ]: factory.addStep(step)

    return factory
