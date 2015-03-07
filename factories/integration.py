#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-24 00:38:34
# @Last Modified by:   caktux
# @Last Modified time: 2015-03-07 13:32:23

import StringIO

import factory
reload(factory)
from factory import *

from buildbot import locks
integration_lock = locks.SlaveLock("integration", maxCount = 1)

class XvfbNoseTest(ShellCommand):

    def __init__(self, test_files, min_coverage, reportdir=""):
        test_paths = ''
        for test_file in test_files:
            test_paths += ' ' + test_file + '.py'
        self.packages = test_files
        cover_packages = '--cover-package=' + ','.join(test_files)
        count_packages = len(test_files)
        name_packages = test_files[0] + ' test' if count_packages == 1 else 'tests'
        if reportdir:
            reportdir = "/" + reportdir
        self.reportdir = reportdir

        command = Interpolate('DISPLAY=:1 xvfb-run -s "-screen 0 1280x1200x8" nosetests -v --with-html --html-file=report%s/index.html --cover-tests --with-coverage ' % reportdir + cover_packages + ' --cover-min-percentage=' + str(min_coverage) + ' --cover-erase --cover-html --cover-html-dir=report%s/coverage' % reportdir + test_paths)
        description = 'running ' + name_packages
        descriptionDone = name_packages
        ShellCommand.__init__(
            self,
            name = name_packages,
            command = command,
            description = description,
            descriptionDone = descriptionDone,
            flunkOnWarnings = False,
            flunkOnFailure = False,
            haltOnFailure = False,
            warnOnFailure = True,
            warnOnWarnings = True,
            workdir = "integration/tests",
            locks = [integration_lock.access('exclusive')]
        )

        # this counter will feed Progress along the 'test cases' metric

        # counter = TestCaseCounter()
        # self.addLogObserver('stdio', counter)
        # self.progressMetrics += ('tests',)

    def createSummary(self, log):
        buildername = self.getProperty('buildername')
        buildnumber = self.getProperty('buildnumber')

        url = '/reports/' + buildername + '/' + str(buildnumber) + '/report' + self.reportdir

        lines = list(StringIO.StringIO(log.getText()).readlines())

        #
        # HTML test report
        #
        passed, total = self._getRatio(lines, len(self.packages))
        # os.chmod(report, stat.S_IROTH) # ?
        self.addURL('passed %s/%s' % (passed, total), url)

        #
        # Coverage test report
        #
        percentage = 'N/A'
        for line in lines:
            if line.startswith(self.packages[0]):
                percentage = line.split()[3]
            if 'TOTAL' in line and 'ERROR' not in line:
                percentage = line.split()[-1]
                break
        self.addURL("coverage %s" % percentage, url + '/coverage')

    def _getRatio(self, lines, total):
        '''Returns total and passed tests'''
        passed = 0
        for line in lines:
            if "... ok" in line:
                passed += 1
        return (passed, total)


def integration_factory():
    factory = BuildFactory()

    test_files = ['catalog', 'integration']
    user_test_files = ['integration-user']
    min_coverage = 80

    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/cpp-ethereum.git',
            branch='develop',
            mode='full',
            method = 'copy',
            codebase='cpp-ethereum',
            retry=(5, 3)
        ),
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/ethereum/ethereum.js.git',
            branch='master',
            mode='incremental',
            codebase='ethereumjs',
            retry=(5, 3),
            workdir="ethereumjs"
        ),
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl='https://github.com/etherex/etherex.git',
            branch='master',
            mode='incremental',
            codebase='integration',
            retry=(5, 3),
            workdir="integration"
        ),
        Configure(
            haltOnFailure = True,
            logEnviron = False,
            command=["cmake", ".", "-DCMAKE_CXX_COMPILER=/usr/lib/ccache/g++"],
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
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="test-requirements",
            description="installing test requirements",
            descriptionDone="install test requirements",
            command=["pip", "install", "-r", "dev_requirements.txt"],
            workdir="integration"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="upgrade-requirements",
            description="upgrading test requirements",
            descriptionDone="upgrade test requirements",
            command=["pip", "install", "--upgrade", "--no-deps", "-r", "dev_requirements.txt"],
            workdir="integration"
        ),
        Test(
            flunkOnFailure = False,
            logEnviron = False,
            description="py.testing",
            descriptionDone="py.test",
            name="py.test",
            command=["py.test", "-vvrs"],
            workdir="integration"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="npm-install",
            description="npm installing",
            descriptionDone="npm install",
            command=["npm", "install"],
            workdir="ethereumjs"
        ),
        Test(
            flunkOnFailure = False,
            logEnviron = False,
            description="npm testing",
            descriptionDone="npm test",
            name="npm-test",
            command=["npm", "test"],
            workdir="ethereumjs"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="clean-chain",
            description="cleaning up",
            descriptionDone="clean chain",
            command=["rm", "-rf", ".ethereum_eth"]
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="clean-up",
            description="cleaning up",
            descriptionDone="clean up",
            command="rm -rf screenshots && rm -rf report && rm -f *.pyc",
            workdir="integration/tests"
        ),
        FileDownload(
            haltOnFailure = True,
            descriptionDone="download init script",
            mastersrc="eth-supervisord-integration.conf",
            slavedest="eth-supervisord-integration.conf"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="start-eth",
            description="starting eth",
            descriptionDone="start eth",
            command="supervisord -c eth-supervisord-integration.conf && sleep 5",
            logfiles={
                "eth.log": "eth.log",
                "eth.err": "eth.err",
                "supervisord.log": "eth-supervisord.log"
            },
            lazylogfiles=True
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="pyepm-deploy",
            description="deploying",
            descriptionDone="deploy",
            command=["pyepm", "contracts/EtherEx.yaml"],
            workdir="integration"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="get-address",
            description="getting address",
            descriptionDone="get address",
            command="curl -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"eth_coinbase\",\"params\":null,\"id\":2}' http://localhost:8080 > address.json"
        ),
        SetPropertyFromCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="parse-address",
            description="parsing address",
            descriptionDone="parse address",
            command="sed -ne 's/.*result\":\"\(.*\)\"}/\\1/p' address.json",
            property="address"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="fill-address",
            description="filling address",
            descriptionDone="fill address",
            command=Interpolate("curl -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"eth_transact\",\"params\":[{\"to\": \"%(prop:address)s\", \"gas\": \"500\", \"value\": \"100000000000000000000\"}],\"id\":72}' http://localhost:8080")
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop-mining",
            description="stopping mining",
            descriptionDone="stop mining",
            command="sleep 20 && curl -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"eth_setMining\",\"params\":[false],\"id\":1}' http://localhost:8080"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="create-folders",
            description="creating folders",
            descriptionDone="create folders",
            command=["mkdir", "-p", "report", "screenshots"],
            workdir="integration/tests"
        ),
        FileDownload(
            haltOnFailure = True,
            descriptionDone="download catalog test",
            mastersrc="tests/catalog.py",
            slavedest="tests/catalog.py",
            workdir="integration"
        ),
        XvfbNoseTest(test_files, min_coverage),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop-eth",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'eth-supervisord-integration.conf' | grep -v grep | awk '{print $2}'` && kill `pidof eth` && sleep 5",
            decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),
        FileDownload(
            haltOnFailure = True,
            descriptionDone="download init script",
            mastersrc="eth-supervisord-integration-user.conf",
            slavedest="eth-supervisord-integration-user.conf"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="start-eth-user",
            description="starting eth",
            descriptionDone="start eth",
            command="supervisord -c eth-supervisord-integration-user.conf && sleep 5",
            logfiles={
                "eth.log": "eth.log",
                "eth.err": "eth.err",
                "supervisord.log": "eth-supervisord.log"
            },
            lazylogfiles=True
        ),
        XvfbNoseTest(user_test_files, min_coverage, reportdir="enduser"),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop-final",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'eth-supervisord-integration-user.conf' | grep -v grep | awk '{print $2}'` && kill `pidof eth` && sleep 5",
            decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),
        ShellCommand(
            haltOnFailure = False,
            flunkOnFailure = False,
            warnOnFailure = True,
            logEnviron = False,
            name="move-screenshots",
            description="moving screenshots",
            descriptionDone="move screenshots",
            command="mv *.png screenshots/",
            workdir="integration/tests"
        ),
        # Upload screenshots
        DirectoryUpload(
            name = 'upload-screenshots',
            compress = 'gz',
            slavesrc = "screenshots",
            masterdest = Interpolate("public_html/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshots"),
            url = Interpolate("/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshots/"),
            workdir="integration/tests"
        ),
        # Upload HTML and coverage report
        DirectoryUpload(
            name = 'upload-reports',
            compress = 'gz',
            slavesrc = "report",
            masterdest = Interpolate("public_html/reports/%(prop:buildername)s/%(prop:buildnumber)s/report"),
            url = Interpolate("/reports/%(prop:buildername)s/%(prop:buildnumber)s/report/"),
            workdir="integration/tests"
        )
    ]: factory.addStep(step)

    return factory
