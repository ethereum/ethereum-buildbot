#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caktux
# @Date:   2015-02-23 14:56:36
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-25 06:39:38

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import _go_cmds

@properties.renderer
def jsonrpc_for_develop(props):
    if props.has_key('version'):
        return int(props['version'][2:3]) > 3
    return None

def deb_factory(name=None, repourl=None, ppabranch=None, branch='master', distribution='trusty', architecture='i386'):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure = True,
            logEnviron = False,
            repourl=repourl,
            branch=branch,
            mode='full',
            method='copy',
            retry=(5, 3)
        ),

        # Set snapshot property for Launchpad versioning
        SetProperty(
            description="setting snapshot",
            descriptionDone="set snapshot",
            name="set-snapshot",
            property="snapshot",
            value=Interpolate("+%(prop:buildnumber)s%(kw:snapshot)s%(kw:distribution)s", snapshot=(dev_snapshot if branch=='develop' else ""), distribution=distribution)
        )
    ]: factory.addStep(step)

    # Run 'go get' for go-ethereum
    if name == 'go-ethereum':
        for step in [
            ShellCommand(
                haltOnFailure = True,
                logEnviron = False,
                name = "move-src",
                command=_go_cmds(branch=branch),
                description="moving src",
                descriptionDone="move src",
                env={"GOPATH": Interpolate("%(prop:workdir)s/go")}
            ),
            ShellCommand(
                logEnviron = False,
                name="source-tarball",
                description="creating source tarball",
                descriptionDone="create source tarball",
                command=Interpolate("tar --exclude .git --exclude pkg --exclude bin -czf ../%(kw:name)s_%(prop:version)s%(prop:snapshot)s.orig.tar.gz .", name=name),
                workdir=Interpolate("%(prop:workdir)s/go")
            ),
            # clean up the Git checkout for debuild
            ShellCommand(
                logEnviron = False,
                name = "clean-build",
                command="rm -rf build && mkdir build",
                description="cleaning build",
                descriptionDone="clean build",
                workdir=Interpolate("%(prop:workdir)s")
            )
        ]: factory.addStep(step)
    # Just create the source tarball for others
    else:
        factory.addStep(ShellCommand(
            logEnviron = False,
            name="source-tarball",
            description="creating source tarball",
            descriptionDone="create source tarball",
            command=Interpolate("tar --exclude .git -czf ../%(kw:name)s_%(prop:version)s%(prop:snapshot)s.orig.tar.gz .", name=name)
        ))

    for step in [
        # Get debian/ directory
        ShellCommand(
            logEnviron = False,
            name="get-debian",
            description="getting debian folder",
            descriptionDone="get debian folder",
            command=Interpolate("wget https://github.com/ethereum/ethereum-ppa/archive/%(kw:ppabranch)s.tar.gz -O- | tar -zx --exclude package.sh --exclude README.md --strip-components=1", ppabranch=ppabranch)
        ),

        # Bump version
        ShellCommand(
            logEnviron = False,
            name="bump-debian",
            description="bumping %s deb version" % distribution,
            descriptionDone="bump %s deb version" % distribution,
            command=Interpolate("EMAIL='caktux (Buildserver key) <caktux@gmail.com>' dch -v %(prop:version)s%(prop:snapshot)s-0ubuntu1 'git build of %(prop:got_revision)s'", dist=distribution)
        ),

        # Build a source package
        ShellCommand(
            logEnviron = False,
            name="source-package",
            description="debuilding %s" % distribution,
            descriptionDone="debuild %s" % distribution,
            command="debuild -S -sa -us -uc"
        ),
    ]: factory.addStep(step)

    # Source only packages for dependencies, build local deb packages otherwise
    if name in ['ethereum', 'go-ethereum']:
        # Add pbuilderrc with ccache config
        # factory.addStep(FileDownload(
        #     mastersrc="pbuilderrc",
        #     slavedest="~/.pbuilderrc"
        # ))

        # Set othermirror for pbuilder
        if name == 'go-ethereum':
            # if branch == 'master':
            #     otherppa = "http://ppa.launchpad.net/ubuntu-sdk-team/ppa/ubuntu"
            # else:
            otherppa = "http://ppa.launchpad.net/beineri/opt-qt541-trusty/ubuntu"

            factory.addStep(ShellCommand(
                logEnviron = False,
                name="pbuilder-opts",
                description="setting pbuilderrc",
                descriptionDone="set pbuilderrc",
                command="echo 'OTHERMIRROR=\"deb [trusted=yes] %s %s main|deb-src [trusted=yes] %s %s main\"' > ~/.pbuilderrc" % (otherppa, distribution, otherppa, distribution),
            ))
        elif name == 'ethereum':
            if branch == 'develop':
                factory.addStep(ShellCommand(
                    logEnviron = False,
                    name="pbuilder-opts",
                    description="setting pbuilderrc",
                    descriptionDone="set pbuilderrc",
                    command="echo 'OTHERMIRROR=\"deb [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum/ubuntu %s main|deb-src [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum/ubuntu %s main|deb [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum-dev/ubuntu %s main|deb-src [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum-dev/ubuntu %s main\"' > ~/.pbuilderrc" % (distribution, distribution, distribution, distribution),
                ))
            else:
                factory.addStep(ShellCommand(
                    logEnviron = False,
                    name="pbuilder-opts",
                    description="setting pbuilderrc",
                    descriptionDone="set pbuilderrc",
                    command="echo 'OTHERMIRROR=\"deb [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum/ubuntu %s main|deb-src [trusted=yes] http://ppa.launchpad.net/ethereum/ethereum/ubuntu %s main\"' > ~/.pbuilderrc" % (distribution, distribution),
                ))

        for step in [
            # Package that thing already
            UbuCowbuilder(
                logEnviron = False,
                architecture=architecture,
                distribution=distribution,
                basetgz="/var/cache/pbuilder/%s-%s-ethereum.cow" % (distribution, architecture),
                keyring="/usr/share/keyrings/ubuntu-archive-keyring.gpg"
            )
        ]: factory.addStep(step)

    for step in [
        # Run Lintian
        # DebLintian(
        #     fileloc=Interpolate("%(prop:deb-changes)s")
        # ),

        # Gather artefacts
        ShellCommand(
            haltOnFailure=True,
            logEnviron = False,
            name="move-packages",
            description='moving packages',
            descriptionDone='move packages',
            command="mkdir result; mv %s ../*.changes ../*.dsc ../*.gz result/" % ("*.deb *.changes" if name in ['ethereum', 'go-ethereum'] else ""),
        ),

        # Upload result folder
        DirectoryUpload(
            slavesrc="result",
            masterdest=Interpolate("public_html/builds/%(prop:buildername)s/%(prop:buildnumber)s"),
            url=Interpolate("/builds/%(prop:buildername)s/%(prop:buildnumber)s"),
        ),

        # Clean latest link
        MasterShellCommand(
            name='clean-latest',
            description='cleaning latest link',
            descriptionDone='clean latest link',
            command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/latest")]
        ),

        # Link latest
        MasterShellCommand(
            name='link-latest',
            description='linking latest',
            descriptionDone='link latest',
            command=['ln', '-sf', Interpolate("%(prop:buildnumber)s"), Interpolate("public_html/builds/%(prop:buildername)s/latest")]
        ),

        # Create source changes folders
        MasterShellCommand(
            name='mkdir-changes',
            description='mkdir',
            descriptionDone='mkdir',
            command=['mkdir', '-p', Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s", dist=distribution, arch=architecture, name=name)]
        ),

        # Link source changes
        MasterShellCommand(
            name='link-changes',
            description='linking changes',
            descriptionDone='link changes',
            command=['ln', '-sf', Interpolate("../../../../public_html/builds/%(prop:buildername)s/%(prop:buildnumber)s"), Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s", dist=distribution, arch=architecture, name=name)]
        )
    ]: factory.addStep(step)

    # Use ethereum-dev ppa for snapshots, only dput one source pkg
    if architecture == 'amd64':
        for step in [
            # Prepare .changes file for Launchpad
            MasterShellCommand(
                name='prepare-changes',
                description='preparing changes',
                descriptionDone='prepare changes',
                command=['sed', '-i', '-e', Interpolate('s/UNRELEASED/%(kw:dist)s/', dist=distribution), '-e', 's/urgency=medium/urgency=low/', Interpolate('changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s/%(prop:buildnumber)s/%(kw:name)s_%(prop:version)s%(prop:snapshot)s-0ubuntu1_source.changes', dist=distribution, arch=architecture, name=name)]
            ),
            # debsign
            MasterShellCommand(
                name='debsign',
                description='debsigning',
                descriptionDone='debsign',
                command=['debsign', Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s/%(prop:buildnumber)s/%(kw:name)s_%(prop:version)s%(prop:snapshot)s-0ubuntu1_source.changes", dist=distribution, arch=architecture, name=name)]
            ),
            # dput
            MasterShellCommand(
                name='dput',
                description='dputting',
                descriptionDone='dput',
                command=['dput', 'ppa:ethereum/ethereum%s' % ("-dev" if branch=='develop' or (name == 'libjson-rpc-cpp' and jsonrpc_for_develop) else ""), Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s/%(prop:buildnumber)s/%(kw:name)s_%(prop:version)s%(prop:snapshot)s-0ubuntu1_source.changes", dist=distribution, arch=architecture, name=name)]
            )
        ]: factory.addStep(step)

    return factory
