#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import *


def brew_go_factory(branch='develop'):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/go-ethereum.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='go-ethereum',
            retry=(5, 3)
        ),
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/homebrew-ethereum.git',
            branch='master',
            mode='incremental',
            codebase='homebrew-ethereum',
            retry=(5, 3),
            workdir='brew'
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-old-version",
            descriptionDone='set old version',
            command='sed -ne "s/^%s  version \'\(.*\)\'/\\1/p" ethereum.rb' % ("" if branch == 'master' else "  "),
            property='old_version',
            workdir='brew',
        )
    ]: factory.addStep(step)

    if branch == 'master':
        factory.addStep(ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="update-version",
            descriptionDone='update go-ethereum version',
            command=Interpolate('sed -i "" "s/^  version \'\(.*\)\'/  version \'%(prop:version)s\'/" ethereum.rb'),
            workdir='brew',
        ))
    elif branch == 'develop':
        factory.addStep(ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="update-version",
            descriptionDone='update go-ethereum version',
            command=Interpolate('sed -i "" "s/^    version \'\(.*\)\'/    version \'%(prop:version)s\'/" ethereum.rb'),
            workdir='brew',
        ))

    for step in [
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="git-add",
            descriptionDone='git add',
            command='git add ethereum.rb',
            workdir='brew'
        ),
        ShellCommand(
            logEnviron=False,
            name="git-commit",
            descriptionDone='git commit',
            command=Interpolate('git commit -m "bump ethereum to %(prop:version)s on %(kw:branch)s"', branch=branch),
            workdir='brew',
            decodeRC={0: SUCCESS, 1: SUCCESS, 2: WARNINGS}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="git-push",
            descriptionDone='git push',
            command='git pull --no-edit && git push',
            workdir='brew',
            decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="cleanup",
            description='cleanup',
            descriptionDone='clean',
            command=["brew", "remove", "ethereum"],
            workdir='brew',
            decodeRC={0: SUCCESS, 1: SUCCESS, 2: WARNINGS}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="clean-up-bottles",
            description='cleaning up bottles',
            descriptionDone='clean up bottles',
            command="rm *.tar.gz",
            workdir='brew',
            decodeRC={0: SUCCESS, 1: SUCCESS, 2: WARNINGS}
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="brew-update",
            description='brew updating',
            descriptionDone='brew update',
            command=["brew", "update"],
            workdir='brew'
        ),
        Compile(
            haltOnFailure=True,
            logEnviron=False,
            name="brew",
            description='running brew',
            descriptionDone='brew',
            command=brew_install_cmd(cmd=['brew', 'install', 'ethereum.rb', '-v', '--build-bottle'], branch=branch),
            workdir='brew'
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="bottle",
            command=brew_install_cmd(cmd=["brew", "bottle", "ethereum.rb", "-v"], branch=branch),
            description="bottling",
            descriptionDone="bottle",
            workdir='brew'
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-old-revision",
            command='sed -ne "s/^    revision \(.*\)/\\1/p" ethereum.rb',
            property='old_revision',
            workdir='brew'
        ),
        SetProperty(
            name="set-bottle",
            description="setting bottle",
            descriptionDone="set bottle",
            property="bottle",
            value=Interpolate("ethereum-%(prop:version)s.yosemite.bottle%(kw:revision)s.tar.gz", revision=brew_revision_suffix)
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-sha1sum",
            command=Interpolate('sha1sum %(prop:bottle)s | grep -o -w "\w\{40\}"'),
            property='sha1sum',
            workdir='brew'
        ),
        FileUpload(
            haltOnFailure=True,
            name='upload-bottle',
            slavesrc=Interpolate("%(prop:bottle)s"),
            masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:buildnumber)s/bottle/"
                                   "ethereum-%(prop:version)s.yosemite.bottle.%(prop:buildnumber)s.tar.gz"),
            url=Interpolate("/builds/%(prop:buildername)s/%(prop:buildnumber)s/bottle/"
                            "ethereum-%(prop:version)s.yosemite.bottle.%(prop:buildnumber)s.tar.gz"),
            workdir='brew'
        )
    ]: factory.addStep(step)

    if branch == 'master':
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-bottle-url",
                descriptionDone='update bottle url',
                command=Interpolate('sed -i "" "s/^    root_url \'\(.*\)\'/    root_url \'https:\/\/build.ethdev.com\/builds\/'
                                    '%(kw:urlbuildername)s\/%(prop:buildnumber)s\/bottle\'/" ethereum.rb', urlbuildername=urlbuildername),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^    revision \(.*\)/    revision %(prop:buildnumber)s/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha1sum",
                descriptionDone='update sha1sum',
                command=Interpolate('sed -i "" "s/^    sha1 \'\(.*\)\' => :yosemite/    sha1 \'%(prop:sha1sum)s\' => :yosemite/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-add",
                descriptionDone='git add',
                command='git add ethereum.rb',
                workdir='brew'
            ),
            ShellCommand(
                logEnviron=False,
                name="git-commit",
                descriptionDone='git commit',
                command=Interpolate('git commit -m "bump ethereum to %(prop:version)s at ethereum/go-ethereum@%(kw:go_revision)s"',
                                    go_revision=get_short_revision_go),
                workdir='brew',
                decodeRC={0: SUCCESS, 1: SUCCESS, 2: WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-push",
                descriptionDone='git push',
                command='git pull --no-edit && git push',
                workdir='brew',
                decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
            )
        ]: factory.addStep(step)

    elif branch == 'develop':
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-bottle-url",
                descriptionDone='update bottle url',
                command=Interpolate('sed -i "" "s/^      root_url \'\(.*\)\'/      root_url \'https:\/\/build.ethdev.com\/builds\/%(kw:urlbuildername)s\/'
                                    '%(prop:buildnumber)s\/bottle\'/" ethereum.rb', urlbuildername=urlbuildername),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^      revision \(.*\)/      revision %(prop:buildnumber)s/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha1sum",
                descriptionDone='update sha1sum',
                command=Interpolate('sed -i "" "s/^      sha1 \'\(.*\)\' => :yosemite/      sha1 \'%(prop:sha1sum)s\' => :yosemite/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-add",
                descriptionDone='git add',
                command='git add ethereum.rb',
                workdir='brew'
            ),
            ShellCommand(
                logEnviron=False,
                name="git-commit",
                descriptionDone='git commit',
                command=Interpolate('git commit -m "bump ethereum to %(prop:version)s at ethereum/go-ethereum@%(kw:go_revision)s"',
                                    go_revision=get_short_revision_go),
                workdir='brew',
                decodeRC={0: SUCCESS, 1: SUCCESS, 2: WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-push",
                descriptionDone='git push',
                command='git pull --no-edit && git push',
                workdir='brew',
                decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
            )
        ]: factory.addStep(step)

    return factory
