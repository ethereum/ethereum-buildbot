from buildbot.process.factory import BuildFactory
from buildbot.process.properties import Interpolate
from buildbot.steps.source.git import Git
from buildbot.steps.shell import Configure
from buildbot.steps.shell import Compile
from buildbot.steps.shell import SetPropertyFromCommand
from buildbot.steps.shell import ShellCommand
from buildbot.steps import shell
from buildbot.steps.trigger import Trigger
from buildbot.status.results import SUCCESS, WARNINGS, SKIPPED # FAILURE, EXCEPTION, RETRY
from buildbot.steps.transfer import FileDownload


import logging

# TODO initial test to check how buildbot actually works.
def support_dep_build(step):
    logging.info (step.build.getProperty('workdir'))
    return False

# C++
def create_factory(branch='master', deb=False):
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
            retry=(5, 3),
            workdir='cpp-ethereum-%s' % branch
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
            command = 'sed -ne "s/.*c_databaseVersion = \(.*\);/\\1/p" libethcore/CommonEth.cpp',
            property = "database",
            workdir = 'cpp-ethereum-%s' % branch
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            command='sed -ne "s/.*c_protocolVersion = \(.*\);/\\1/p" libethcore/CommonEth.cpp',
            property="protocol",
            workdir = 'cpp-ethereum-%s' % branch
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            command='sed -ne "s/.*Version = \\"\(.*\)\\";/\\1/p" libdevcore/Common.cpp',
            property="version",
            workdir = 'cpp-ethereum-%s' % branch
        ),
        ShellCommand(
            description = 'compiling',
            descriptionDone = 'compile',
            descriptionSuffix = 'dependencies',
            command = ['./build.py', 'dep'],           
            workdir = 'cpp-ethereum-%s' % branch,
            logEnviron = False,
            doStepIf = support_dep_build
        ),
        Configure(
            haltOnFailure = True,
            logEnviron = False,
            command=["cmake", "."],
            workdir='cpp-ethereum-%s' % branch
        ),
        Compile(
            haltOnFailure = True,
            logEnviron = False,
            command="make -j $(cat /proc/cpuinfo | grep processor | wc -l)",
            workdir='cpp-ethereum-%s' % branch
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            description="installing",
            descriptionDone="install",
            command=["make", "install"],
            workdir='cpp-ethereum-%s' % branch
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            description="running ldconfig",
            descriptionDone="ldconfig",
            command=["ldconfig"],
            workdir='cpp-ethereum-%s' % branch
        ),
        ShellCommand(
            logEnviron = False,
            name="test-cpp",
            description="testing",
            descriptionDone="test",
            command=["./testeth"],
            env={'CTEST_OUTPUT_ON_FAILURE': '1', 'ETHEREUM_TEST_PATH': Interpolate('%(prop:workdir)s/tests')},
            workdir="cpp-ethereum-%s/test" % branch,
            decodeRC={0:SUCCESS, 1:WARNINGS, 201:WARNINGS}
        ),
        FileDownload(
            haltOnFailure = True,
            descriptionDone="download init script",
            mastersrc="eth-supervisord.conf",
            slavedest="eth-supervisord.conf"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'supervisord -c eth-supervisord.conf' | awk '{print $2}'` && kill `pidof eth`",
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
        ),
    ]: factory.addStep(step)

    if deb:
        for architecture in ['i386', 'amd64']:
            for distribution in ['trusty', 'utopic']:
                for step in [
                    Trigger(
                        schedulerNames=["cpp-ethereum-%s-%s-%s" % (branch, architecture, distribution)],
                        waitForFinish=False,
                        set_properties={
                            "version": Interpolate("%(prop:version)s")
                        }
                    )
                ]: factory.addStep(step)

    return factory
