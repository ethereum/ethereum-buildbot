#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:10:52
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-23 17:01:50

import re
import time
import urllib

from buildbot.process import properties
from buildbot.process.properties import Interpolate
from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.master import MasterShellCommand, SetProperty
from buildbot.steps.package.deb.lintian import DebLintian
from buildbot.steps.package.deb.pbuilder import UbuCowbuilder
from buildbot.steps.shell import Configure, Compile, SetPropertyFromCommand, ShellCommand, Test, WarningCountingShellCommand
from buildbot.steps.transfer import FileDownload, FileUpload, DirectoryUpload
from buildbot.steps.trigger import Trigger
from buildbot.steps.vstudio import MsBuild12
from buildbot.status.results import SUCCESS, WARNINGS, SKIPPED # FAILURE, EXCEPTION, RETRY
# from buildbot.steps.cppcheck import Cppcheck # TODO native on nine

@properties.renderer
def get_time_string(props):
    return time.strftime("%Y%m%d%H%M%S", time.localtime())

@properties.renderer
def dev_snapshot(props):
    return "SNAPSHOT%s" % time.strftime("%Y%m%d%H%M%S", time.localtime())

@properties.renderer
def urlbuildername(props):
    if props.has_key('buildername'):
        return urllib.quote(props['buildername'])
    return None

# @properties.renderer
# def get_new_bottle_revision(props):
#     if props.has_key('old_revision'):
#         return "." + str(int(props['old_revision']) + 1)
#     return 1

# def _no_warnings(self):
#     fail = False
#     steps = self.build.getStatus().getSteps()
#     for step in steps:
#         (step_result, text) = step.getResults()
#         if step_result != SUCCESS and step_result != SKIPPED and step_result != None:
#             fail = True
#     if fail:
#         return False
#     else:
#         return True

#
# OSX factories
#
def brew_install_cmd(cmd=[], branch='master'):
    if branch == 'develop':
        cmd.append('--devel')
    return cmd
