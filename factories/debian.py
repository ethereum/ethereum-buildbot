#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

import go_ethereum
reload(go_ethereum)
from go_ethereum import _go_cmds

@properties.renderer
def jsonrpc_for_develop(props):
    if 'version' in props:
        return int(props['version'][2:3]) > 3
    return None

@properties.renderer
def deb_version(props):
    if 'version' in props:
        if ":" in props['version']:
            return props['version'][2:]
        else:
            return props['version']
    return None

def deb_factory(name=None, repourl=None, ppabranch=None, branch='master', distribution='trusty', architecture='i386', testdeb=False):
    factory = BuildFactory()

    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
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
            value=Interpolate("+%(prop:buildnumber)s%(kw:snapshot)s%(kw:distribution)s",
                              snapshot=(dev_snapshot if branch == 'develop' or testdeb else ""),
                              distribution=distribution)
        )
    ]: factory.addStep(step)

    # Run 'go get' for go-ethereum
    if name == 'ethereum':
        for step in [
            ShellCommand(
                haltOnFailure=True,
                logEnviron=False,
                name="move-src",
                command=_go_cmds(branch=branch),
                description="moving src",
                descriptionDone="move src",
                env={"GOPATH": Interpolate("%(prop:workdir)s/go")}
            ),
            ShellCommand(
                logEnviron=False,
                name="source-tarball",
                description="creating source tarball",
                descriptionDone="create source tarball",
                command=Interpolate("tar --exclude .git --exclude pkg --exclude bin -czf "
                                    "../%(kw:name)s_%(prop:version)s%(prop:snapshot)s.orig.tar.gz .", name=name),
                workdir=Interpolate("%(prop:workdir)s/go")
            ),
            # clean up the Git checkout for debuild
            ShellCommand(
                logEnviron=False,
                name="clean-build",
                command="rm -rf build && mkdir build",
                description="cleaning build",
                descriptionDone="clean build",
                workdir=Interpolate("%(prop:workdir)s")
            )
        ]: factory.addStep(step)
    # Get qtwebengine-opensource-src tarball
    elif name == 'qtwebengine-opensource-src':
        for step in [
            ShellCommand(
                logEnviron=False,
                name="source-tarball",
                description="getting source tarball",
                descriptionDone="get source tarball",
                command=Interpolate("wget -c https://download.qt.io/official_releases/qt/5.4/%(kw:version)s/submodules/"
                                    "qtwebengine-opensource-src-%(kw:version)s.tar.xz "
                                    "-O ../%(kw:name)s_%(prop:version)s%(prop:snapshot)s.orig.tar.xz",
                                    name=name,
                                    version=branch)
            ),
            # clean up the Git checkout for debuild
            ShellCommand(
                logEnviron=False,
                name="clean-build",
                command="rm -rf build && mkdir build",
                description="cleaning build",
                descriptionDone="clean build",
                workdir=Interpolate("%(prop:workdir)s")
            )
        ]: factory.addStep(step)
    # Just create the source tarball for others
    else:
        factory.addStep(ShellCommand(
            logEnviron=False,
            name="source-tarball",
            description="creating source tarball",
            descriptionDone="create source tarball",
            command=Interpolate("tar --exclude .git -czf "
                                "../%(kw:name)s_%(kw:version)s%(prop:snapshot)s.orig.tar.gz .",
                                name=name,
                                version=deb_version)
        ))

    for step in [
        # Get debian/ directory
        ShellCommand(
            logEnviron=False,
            name="get-debian",
            description="getting debian folder",
            descriptionDone="get debian folder",
            command=Interpolate("wget https://github.com/ethereum/ethereum-ppa/archive/%(kw:ppabranch)s.tar.gz -O- |"
                                " tar -zx --exclude package.sh --exclude README.md --strip-components=1",
                                ppabranch=ppabranch)
        ),

        # Bump version
        ShellCommand(
            logEnviron=False,
            name="bump-debian",
            description="bumping %s deb version" % distribution,
            descriptionDone="bump %s deb version" % distribution,
            command=Interpolate("EMAIL='caktux (Buildserver key) <caktux@gmail.com>' "
                                "dch -v %(prop:version)s%(prop:snapshot)s-0ubuntu1 "
                                "'git build of %(prop:got_revision)s'",
                                dist=distribution)
        ),

        # Build a source package
        ShellCommand(
            logEnviron=False,
            name="source-package",
            description="debuilding %s" % distribution,
            descriptionDone="debuild %s" % distribution,
            command="debuild -S -sa -us -uc"
        ),
    ]: factory.addStep(step)

    # Source only packages for dependencies, build local deb packages otherwise
    if name in ['ethereum', 'cpp-ethereum']:
        # Add pbuilderrc with ccache config
        # factory.addStep(FileDownload(
        #     mastersrc="pbuilderrc",
        #     slavedest="~/.pbuilderrc"
        # ))
        main_ppa = "http://ppa.launchpad.net/ethereum/ethereum/ubuntu"
        dev_ppa = "http://ppa.launchpad.net/ethereum/ethereum-dev/ubuntu"
        qt_ppa = "http://ppa.launchpad.net/ethereum/ethereum-qt/ubuntu"

        for step in [
            # Set PPA dependencies for pbuilder
            ShellCommand(
                logEnviron=False,
                name="pbuilder-opts",
                description="setting pbuilderrc",
                descriptionDone="set pbuilderrc",
                command="echo 'OTHERMIRROR=\""
                        "deb [trusted=yes] {1} {0} main|deb-src [trusted=yes] {1} {0} main|"
                        "deb [trusted=yes] {2} {0} main|deb-src [trusted=yes] {2} {0} main|"
                        "deb [trusted=yes] {3} {0} main|deb-src [trusted=yes] {3} {0} main\"' > ~/.pbuilderrc"
                            .format(distribution, main_ppa, dev_ppa, qt_ppa)
            ),
            # Package that thing already
            UbuCowbuilder(
                logEnviron=False,
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
        # Prepare .changes file for Launchpad
        ShellCommand(
            name='prepare-changes',
            description='preparing changes',
            descriptionDone='prepare changes',
            command=Interpolate("sed -i -e s/UNRELEASED/%(kw:dist)s/ "
                                "-e s/urgency=medium/urgency=low/ ../*.changes",
                                dist=distribution)
        ),

        # Gather artefacts
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="move-packages",
            description='moving packages',
            descriptionDone='move packages',
            command="mkdir result; mv %s../*.changes ../*.dsc ../*.gz %sresult/" %
                    ("*.deb *.changes " if name in ['ethereum', 'cpp-ethereum'] else "",
                        "../*.xz " if name == 'qtwebengine-opensource-src' else ""),
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
            command=['mkdir', '-p',
                        Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s",
                                    dist=distribution, arch=architecture, name=name)]
        ),

        # Link source changes
        MasterShellCommand(
            name='link-changes',
            description='linking changes',
            descriptionDone='link changes',
            command=['ln', '-sf',
                        Interpolate("../../../../public_html/builds/%(prop:buildername)s/%(prop:buildnumber)s"),
                        Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s",
                                    dist=distribution,
                                    arch=architecture,
                                    name=name)]
        )
    ]: factory.addStep(step)

    # Use ethereum-dev ppa for snapshots, only dput one source pkg
    ppa_suffix = ""
    if branch == 'develop' or (name == 'libjson-rpc-cpp' and jsonrpc_for_develop):
        ppa_suffix = "-dev"
    elif name == 'qtwebengine-opensource-src':
        ppa_suffix = "-qt"

    if architecture == 'amd64':
        for step in [
            # debsign
            MasterShellCommand(
                haltOnFailure=False,
                flunkOnFailure=False,
                name='debsign',
                description='debsigning',
                descriptionDone='debsign',
                command=['debsign', Interpolate("changes/%(kw:dist)s/%(kw:arch)s/"
                                                "%(kw:name)s/%(prop:buildnumber)s/"
                                                "%(kw:name)s_%(kw:version)s%(prop:snapshot)s-"
                                                "0ubuntu1_source.changes",
                                                dist=distribution,
                                                arch=architecture,
                                                name=name,
                                                version=deb_version)]
            ),
            # dput
            MasterShellCommand(
                name='dput',
                description='dputting',
                descriptionDone='dput',
                command=['dput', 'ppa:%s%s' % ("caktux/ppa" if testdeb else "ethereum/ethereum", ppa_suffix),
                            Interpolate("changes/%(kw:dist)s/%(kw:arch)s/%(kw:name)s/"
                                        "%(prop:buildnumber)s/%(kw:name)s_%(kw:version)s%(prop:snapshot)s-"
                                        "0ubuntu1_source.changes",
                                        dist=distribution,
                                        arch=architecture,
                                        name=name,
                                        version=deb_version)]
            )
        ]: factory.addStep(step)

    return factory
