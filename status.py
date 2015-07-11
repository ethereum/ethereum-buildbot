#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###### STATUS TARGETS

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

from buildbot.status import html
from buildbot.status import words
from buildbot.status.web import authz, auth
from buildbot.status.github import GitHubStatus
from buildbot.process.properties import Interpolate
from buildstatusimage import BuildStatusImageResource

# using simplejson instead of json since Twisted wants ascii instead of unicode
import simplejson as json

status = []

# Load users from external file, see users.json.sample
users = []
for user in json.load(open("users.json")):
    users.append((user['username'], user['password']))

authz_cfg = authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth(users),
    gracefulShutdown=False,
    forceBuild='auth',  # use this to test your slave once it is set up
    forceAllBuilds='auth',
    pingBuilder='auth',
    stopBuild='auth',
    stopAllBuilds='auth',
    cancelPendingBuild='auth',
)


class WebStatus(html.WebStatus):
    def setupUsualPages(self, numbuilds, num_events, num_events_max):
        html.WebStatus.setupUsualPages(self, numbuilds, num_events, num_events_max)
        self.putChild("buildstatusimage", BuildStatusImageResource())

status.append(WebStatus(
    http_port=8010,  # "ssl:port=8443:privateKey=/etc/ssl/server.key:certKey=/etc/ssl/server.crt:extraCertChain=/etc/ssl/server.ca-bundle",
    authz=authz_cfg,
    change_hook_auth=["file:changehook.passwd"],
    change_hook_dialects={'github': {}},
    order_console_by_time=True))


# IRC bot
ircbot = json.load(open("ircbot.json"))
status.append(words.IRC(host=ircbot['server'],
                        nick=ircbot['nickname'],
                        password=ircbot['password'],
                        channels=ircbot['channels'],
                        notify_events={
                            'successToException': 1,
                            'successToFailure': 1,
                            'failureToSuccess': 1,
                            'exceptionToSuccess': 1}
                        ))


# GitHub Status
tokens = json.load(open("tokens.json"))
for repo in tokens:
    gs = GitHubStatus(
        token=tokens[repo]["token"],
        repoOwner=tokens[repo]["owner"],
        repoName=repo,
        sha=Interpolate("%(src:" + repo + ":revision)s"),
        startDescription='DEV build started.',
        endDescription='DEV build done.')
    status.append(gs)
