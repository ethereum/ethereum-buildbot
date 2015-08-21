#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import cpp_ethereum
reload(cpp_ethereum)
from cpp_ethereum import *

def brew_cpp_factory(branch='develop', headless=True):
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
            command='sed -ne "s/^%s  version \'\(.*\)\'/\\1/p" cpp-ethereum.rb' % ("" if branch == 'master' else "  "),
            property='old_version',
            workdir='brew',
        )
    ]: factory.addStep(step)

    if headless:
        if branch == 'master':
            for step in [
                ShellCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="update-version",
                    descriptionDone='update version',
                    command=Interpolate('sed -i "" "s/^  version \'\(.*\)\'/  version \'%(prop:version)s\'/" cpp-ethereum.rb'),
                    workdir='brew',
                )
            ]: factory.addStep(step)

        if branch == 'develop':
            for step in [
                ShellCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="update-version",
                    descriptionDone='update version',
                    command=Interpolate('sed -i "" "s/^    version \'\(.*\)\'/    version \'%(prop:version)s\'/" cpp-ethereum.rb'),
                    workdir='brew',
                )
            ]: factory.addStep(step)

        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-add",
                descriptionDone='git add',
                command='git add cpp-ethereum.rb',
                workdir='brew',
            ),
            ShellCommand(
                logEnviron=False,
                name="git-commit",
                descriptionDone='git commit',
                command=Interpolate('git commit -m "bump cpp-ethereum to %(prop:version)s on %(kw:branch)s"', branch=branch),
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

    for step in [
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="clean-up",
            description='cleaning up',
            descriptionDone='clean up',
            command=["brew", "remove", "cpp-ethereum"],
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
            description='brewing',
            descriptionDone='brew',
            command=brew_install_cmd(cmd=['brew', 'install', 'cpp-ethereum.rb', '--with-evmjit', '-v', '--build-bottle'], branch=branch, headless=headless),
            workdir='brew'
        )
    ]: factory.addStep(step)

    if headless:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="bottle",
                command=brew_install_cmd(cmd=['brew', 'bottle', 'cpp-ethereum.rb', '--with-evmjit', '-v'], branch=branch, headless=headless),
                description="bottling",
                descriptionDone="bottle",
                workdir='brew'
            ),
            SetPropertyFromCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="set-old-revision",
                command='sed -ne "s/^%s    revision \(.*\)/\\1/p" cpp-ethereum.rb' % ("" if branch == 'master' else "  "),
                property='old_revision',
                workdir='brew'
            ),
            SetProperty(
                name="set-bottle",
                description="setting bottle",
                descriptionDone="set bottle",
                property="bottle",
                value=Interpolate("cpp-ethereum-%(prop:version)s.yosemite.bottle%(kw:revision)s.tar.gz", revision=brew_revision_suffix)
            ),
            SetPropertyFromCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="sha1sum",
                command=Interpolate('sha1sum %(prop:bottle)s | grep -o -w "\w\{40\}"'),
                property='sha1sum',
                workdir='brew'
            ),
            FileUpload(
                haltOnFailure=True,
                name='upload-bottle',
                slavesrc=Interpolate("%(prop:bottle)s"),
                masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:buildnumber)s/bottle/"
                                       "cpp-ethereum-%(prop:version)s.yosemite.bottle.%(prop:buildnumber)s.tar.gz"),
                url=Interpolate("/builds/%(prop:buildername)s/%(prop:buildnumber)s/bottle/"
                                "cpp-ethereum-%(prop:version)s.yosemite.bottle.%(prop:buildnumber)s.tar.gz"),
                workdir='brew'
            )
        ]: factory.addStep(step)

    if branch == 'master' and headless:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-bottle-url",
                descriptionDone='update bottle url',
                command=Interpolate('sed -i "" "s/^    root_url \'\(.*\)\'/    root_url \'https:\/\/build.ethdev.com\/builds\/'
                                    '%(kw:urlbuildername)s\/%(prop:buildnumber)s\/bottle\'/" cpp-ethereum.rb', urlbuildername=urlbuildername),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^    revision \(.*\)/    revision %(prop:buildnumber)s/" cpp-ethereum.rb'),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha1sum",
                descriptionDone='update sha1sum',
                command=Interpolate('sed -i "" "s/^    sha1 \'\(.*\)\' => :yosemite/    sha1 \'%(prop:sha1sum)s\' => :yosemite/" cpp-ethereum.rb'),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-add",
                descriptionDone='git add',
                command='git add cpp-ethereum.rb',
                workdir='brew',
            ),
            ShellCommand(
                logEnviron=False,
                name="git-commit",
                descriptionDone='git commit',
                command=Interpolate('git commit -m "bump version to %(prop:version)s at ethereum/cpp-ethereum@%(kw:cpp_revision)s"',
                                    cpp_revision=get_short_revision),
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

    if branch == 'develop' and headless:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-bottle-url",
                descriptionDone='update bottle url',
                command=Interpolate('sed -i "" "s/^      root_url \'\(.*\)\'/      root_url \'https:\/\/build.ethdev.com\/builds\/'
                                    '%(kw:urlbuildername)s\/%(prop:buildnumber)s\/bottle\'/" cpp-ethereum.rb', urlbuildername=urlbuildername),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^      revision \(.*\)/      revision %(prop:buildnumber)s/" cpp-ethereum.rb'),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha1sum",
                descriptionDone='update sha1sum',
                command=Interpolate('sed -i "" "s/^      sha1 \'\(.*\)\' => :yosemite/      sha1 \'%(prop:sha1sum)s\' => :yosemite/" cpp-ethereum.rb'),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-successful-version",
                descriptionDone='update successful version',
                command=Interpolate('sed -i "" "s/^      version \'\(.*\)\'/      version \'%(prop:version)s\'/" cpp-ethereum.rb'),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-successful-revision",
                descriptionDone='update successful revision',
                command=Interpolate('sed -i "" "s/:revision => \'\(.*\)\'/:revision => \'%(kw:cpp_revision)s\'/" cpp-ethereum.rb',
                                    cpp_revision=get_cpp_revision),
                workdir='brew',
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-add",
                descriptionDone='git add',
                command='git add cpp-ethereum.rb',
                workdir='brew',
            ),
            ShellCommand(
                logEnviron=False,
                name="git-commit",
                descriptionDone='git commit',
                command=Interpolate('git commit -m "bump successful to %(prop:version)s at ethereum/cpp-ethereum@%(kw:cpp_revision)s"',
                                    cpp_revision=get_short_revision),
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
