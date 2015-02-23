#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 13:42:42
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-23 13:54:38

####### BUILDSLAVES

# The 'slaves' list defines the set of recognized buildslaves. Each element is
# a BuildSlave object, specifying a unique slave name and password.  The same
# slave name and password must be configured on the slave.
from buildbot.buildslave import BuildSlave

# using simplejson instead of json since Twisted wants ascii instead of unicode
import simplejson as json

slaves = []

# Load slaves from external file, see slaves.json.sample
for slave in json.load(open("slaves.json")):
    slaves.append(BuildSlave(slave['name'], slave['password']))

