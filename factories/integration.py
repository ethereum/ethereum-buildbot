#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-24 00:38:34
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-26 04:43:26

import StringIO

import factory
reload(factory)
from factory import *

from buildbot import locks
integration_lock = locks.SlaveLock("integration", maxCount = 1)

class XvfbNoseTest(ShellCommand):

    def __init__(self, test_files, package_names, min_coverage):
        test_paths = ''
        for test_file in test_files:
            test_paths += ' ' + test_file + '.py'
        self.packages = package_names
        cover_packages = '--cover-package=' + ','.join(test_files)
        count_packages = len(package_names)
        name_packages = package_names[0] + ' test' if count_packages == 1 else 'tests'

        command = Interpolate('DISPLAY=:1 xvfb-run -s "-screen 0 1280x1200x8" nosetests -v --with-html --html-file=report/index.html --cover-tests --with-coverage ' + cover_packages + ' --cover-min-percentage=' + str(min_coverage) + ' --cover-erase --cover-html --cover-html-dir=report/coverage' + test_paths)
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

        build_report_path = '/reports/' + buildername + '/' + str(buildnumber) + '/report/'

        lines = list(StringIO.StringIO(log.getText()).readlines())

        #
        # HTML test report
        #
        url = build_report_path
        passed, total = self._getRatio(lines)
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
        url = build_report_path + 'coverage'
        self.addURL("coverage %s" % percentage, url)

    def _getRatio(self, lines):
        '''Returns total and passed tests'''
        passed = None
        total = 0
        for line in lines:
            if line.startswith('Ran'):
                total = line.split()[1]
            if line.startswith('FAILED'):
                regex = re.compile("FAILED \((errors=[0-9]+)?(, )?(failures=[0-9]+)?\)")
                r = regex.search(line)
                groups = r.groups()
                passed = int(total)
                if isinstance(groups, basestring):
                    passed = passed - int(groups[0].split('=')[-1])
                    break
                if len(groups) == 3 and isinstance(groups[2], basestring):
                    passed = passed - int(groups[2].split('=')[-1])
                    break
        if passed is None:
            passed = total
        return (passed, total)


def integration_factory():
    factory = BuildFactory()

    test_files = ['integration']
    package_names = ['integration']
    min_coverage = 90

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
            description="testing",
            descriptionDone="py.test",
            name="test-py.test",
            command=["py.test", "-vvrs"],
            workdir="integration"
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
            name="stop",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'supervisord -c eth-supervisord-integration.conf' | awk '{print $2}'` && kill `pidof eth` && sleep 5",
            decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
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
            name="clean-report",
            description="cleaning report",
            descriptionDone="clean report",
            command="rm -f screenshot* && rm -rf report && rm -f *.pyc",
            workdir="integration/tests"
        ),
        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="start",
            description="starting",
            descriptionDone="start",
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
            name="report-folder",
            description="creating report folder",
            descriptionDone="create report folder",
            command=["mkdir", "-p", "report"],
            workdir="integration/tests"
        ),
        # FileDownload(
        #     haltOnFailure = True,
        #     descriptionDone="download integration test",
        #     mastersrc="tests/integration.py",
        #     slavedest="tests/integration.py",
        #     workdir="integration"
        # ),

        XvfbNoseTest(test_files, package_names, min_coverage),

        ShellCommand(
            haltOnFailure = True,
            logEnviron = False,
            name="stop",
            description="stopping",
            descriptionDone="stop",
            command="kill `ps aux | grep 'supervisord -c eth-supervisord-integration.conf' | awk '{print $2}'` && kill `pidof eth` && sleep 5",
            decodeRC={-1: SUCCESS, 0:SUCCESS, 1:WARNINGS, 2:WARNINGS}
        ),

        # Upload screenshot
        FileUpload(
            haltOnFailure = False,
            flunkOnFailure = False,
            warnOnFailure = True,
            name = 'upload-screenshot',
            slavesrc = "screenshot.png",
            masterdest = Interpolate("public_html/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot.png"),
            url = Interpolate("/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot.png"),
            workdir="integration/tests"
        ),

        # Upload failure screenshot
        FileUpload(
            haltOnFailure = False,
            flunkOnFailure = False,
            warnOnFailure = True,
            name = 'upload-fail-screenshot',
            doStepIf = warnings,
            slavesrc = "screenshot-fail.png",
            masterdest = Interpolate("public_html/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot-fail.png"),
            url = Interpolate("/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot-fail.png"),
            workdir="integration/tests"
        ),

        # Upload final screenshot
        FileUpload(
            haltOnFailure = False,
            flunkOnFailure = False,
            warnOnFailure = True,
            name = 'upload-final-screenshot',
            doStepIf = no_warnings,
            slavesrc = "screenshot-final.png",
            masterdest = Interpolate("public_html/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot-final.png"),
            url = Interpolate("/reports/%(prop:buildername)s/%(prop:buildnumber)s/screenshot-final.png"),
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
