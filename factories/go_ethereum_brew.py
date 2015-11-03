#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import *

@properties.renderer
def revision_or_buildnumber(props):
    if 'revision' in props:
        return props['revision']
    return props['buildnumber']

def release_name(release):
    return 'Yosemite' if release == 'yosemite' else 'El Capitan'

def brew_go_factory(branch='develop', release='el_capitan'):
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
        )
    ]: factory.addStep(step)

    # Bump version and revision only once
    if release == 'el_capitan':
        if branch == 'master':
            for step in [
                ShellCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="update-version",
                    descriptionDone='update go-ethereum version',
                    command=Interpolate('sed -i "" "s/^'
                                        '  version \'\(.*\)\'/'
                                        '  version \'%(prop:version)s\'/" ethereum.rb'),
                    workdir='brew',
                )
            ]: factory.addStep(step)

        elif branch == 'develop':
            for step in [
                ShellCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="update-version",
                    descriptionDone='update go-ethereum version',
                    command=Interpolate('sed -i "" "s/^'
                                        '    version \'\(.*\)\'/'
                                        '    version \'%(prop:version)s\'/" ethereum.rb'),
                    workdir='brew',
                )
            ]: factory.addStep(step)

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
                decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-push",
                descriptionDone='git push',
                command='git pull --no-edit && git push',
                workdir='brew'
            )
        ]: factory.addStep(step)
    else:
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-pull",
                descriptionDone='git pull',
                command='git pull --no-edit',
                workdir='brew'
            )
        ]: factory.addStep(step)

    for step in [
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
            command="brew bottle ethereum.rb -v%s > bottle.log" % (" --devel" if branch is "develop" else ""),
            logfiles={"bottle.log": "bottle.log"},
            lazylogfiles=True,
            description="bottling",
            descriptionDone="bottle",
            workdir='brew'
        ),
        SetPropertyFromCommand(
            name="set-bottle",
            command='sed -ne "s/.*Bottling \(.*\).../\\1/p" bottle.log',
            description="setting bottle",
            descriptionDone="set bottle",
            property="bottle",
            workdir="brew"
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-sha256sum",
            command='sed -ne "s/.*sha256 \\"\(.*\)\\".*/\\1/p" bottle.log',
            property='sha256sum',
            workdir='brew'
        ),
        FileUpload(
            haltOnFailure=True,
            name='upload-bottle',
            slavesrc=Interpolate("%(prop:bottle)s"),
            masterdest=Interpolate(("public_html/builds/bottles%(kw:dev)s/"
                                   "ethereum-%(prop:version)s.%(kw:release)s.bottle.%(kw:revision)s.tar.gz"),
                                   dev="-dev" if branch == 'develop' else "",
                                   release=release,
                                   revision=revision_or_buildnumber),
            url=Interpolate("/builds/bottles%(kw:dev)s/"
                            "ethereum-%(prop:version)s.%(kw:release)s.bottle.%(kw:revision)s.tar.gz",
                            dev="-dev" if branch == 'develop' else "",
                            release=release,
                            revision=revision_or_buildnumber),
            workdir='brew'
        )
    ]: factory.addStep(step)

    if branch == 'master':
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-pull",
                descriptionDone='git pull',
                command='git pull --no-edit',
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^'
                                    '    revision \(.*\)/'
                                    '    revision %(prop:buildnumber)s/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha256sum",
                descriptionDone='update sha256sum',
                command=Interpolate('sed -i "" "s/^'
                                    '    sha256 \'\(.*\)\' => :%(kw:release)s/'
                                    '    sha256 \'%(prop:sha256sum)s\' => :%(kw:release)s/" ethereum.rb', release=release),
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
                command=Interpolate('git commit -m "ethereum %(prop:version)s on %(kw:branch)s at ethereum/go-ethereum@%(kw:go_revision)s for %(kw:release)s"',
                                    branch=branch,
                                    go_revision=get_short_revision_go,
                                    release=release_name(release)),
                workdir='brew',
                decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-push",
                descriptionDone='git push',
                command='git pull --no-edit && git push',
                workdir='brew'
            )
        ]: factory.addStep(step)

    elif branch == 'develop':
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-pull",
                descriptionDone='git pull',
                command='git pull --no-edit',
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-brew-revision",
                descriptionDone='update brew revision',
                command=Interpolate('sed -i "" "s/^'
                                    '      revision \(.*\)/'
                                    '      revision %(prop:buildnumber)s/" ethereum.rb'),
                workdir='brew'
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="update-sha256sum",
                descriptionDone='update sha256sum',
                command=Interpolate('sed -i "" "s/^'
                                    '      sha256 \'\(.*\)\' => :%(kw:release)s/'
                                    '      sha256 \'%(prop:sha256sum)s\' => :%(kw:release)s/" ethereum.rb', release=release),
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
                command=Interpolate('git commit -m "ethereum %(prop:version)s on %(kw:branch)s at ethereum/go-ethereum@%(kw:go_revision)s for %(kw:release)s"',
                                    branch=branch,
                                    go_revision=get_short_revision_go,
                                    release=release_name(release)),
                workdir='brew',
                decodeRC={0: SUCCESS, 1: WARNINGS, 2: WARNINGS}
            ),
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="git-push",
                descriptionDone='git push',
                command='git pull --no-edit && git push',
                workdir='brew'
            )
        ]: factory.addStep(step)

    # Trigger Yosemite build
    if release == 'el_capitan':
        for step in [
            Trigger(
                name='brew-yosemite',
                schedulerNames=["go-ethereum-%s-yosemite" % branch],
                waitForFinish=False,
                set_properties={
                    "version": Interpolate("%(prop:version)s"),
                    "revision": Interpolate("%(prop:buildnumber)s")
                }
            )
        ]: factory.addStep(step)

    return factory
