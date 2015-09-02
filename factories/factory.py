#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re  # NOQA
import time
import urllib

from buildbot.process import properties
from buildbot.process.properties import Interpolate  # NOQA
from buildbot.process.factory import BuildFactory  # NOQA
from buildbot.steps.source.git import Git  # NOQA
from buildbot.steps.master import MasterShellCommand, SetProperty  # NOQA
from buildbot.steps.package.deb.lintian import DebLintian  # NOQA
from buildbot.steps.package.deb.pbuilder import UbuCowbuilder  # NOQA
from buildbot.steps.shell import Configure, Compile, SetPropertyFromCommand, ShellCommand, Test, WarningCountingShellCommand  # NOQA
from buildbot.steps.transfer import FileDownload, FileUpload, DirectoryUpload  # NOQA
from buildbot.steps.trigger import Trigger  # NOQA
from buildbot.steps.vstudio import MsBuild12  # NOQA
from buildbot.status.results import SUCCESS, WARNINGS, SKIPPED, FAILURE  # EXCEPTION, RETRY  # NOQA
# from buildbot.steps.cppcheck import Cppcheck # TODO native on nine

@properties.renderer
def get_time_string(props):
    return time.strftime("%Y%m%d%H%M%S", time.localtime())

@properties.renderer
def dev_snapshot(props):
    return "SNAPSHOT%s" % time.strftime("%Y%m%d%H%M%S", time.localtime())

@properties.renderer
def urlbuildername(props):
    if 'buildername' in props:
        return urllib.quote(props['buildername'])
    return None

@properties.renderer
def brew_revision_suffix(props):
    if 'old_revision' in props and 'old_version' in props:
        if props['old_version'] == props['version']:
            return ".%s" % (int(props['old_revision']))
        else:
            return ""
    return None

# @properties.renderer
# def get_new_bottle_revision(props):
#     if props.has_key('old_revision'):
#         return "." + str(int(props['old_revision']) + 1)
#     return 1

def warnings(self):
    fail = False
    steps = self.build.getStatus().getSteps()
    for step in steps:
        (step_result, text) = step.getResults()
        if step_result != SUCCESS and step_result != SKIPPED and step_result is not None:
            fail = True
    return fail

def no_warnings(self):
    fail = False
    steps = self.build.getStatus().getSteps()
    for step in steps:
        (step_result, text) = step.getResults()
        if step_result != SUCCESS and step_result != SKIPPED and step_result is not None:
            fail = True
    if fail:
        return False
    else:
        return True

#
# OSX factories
#
def brew_install_cmd(cmd=[], branch='master', headless=True):
    if not headless:
        cmd.append('--with-gui')
    if branch == 'develop':
        cmd.append('--devel')
    return cmd
