#!/usr/bin/env python
# -*- coding: utf-8 -*-

import factory
reload(factory)
from factory import *

osVersions = [
    'darwin-x64',
    # 'linux-arm',
    'linux-ia32',
    'linux-x64',
    'win32-ia32',
    'win32-x64'
]

@properties.renderer
def get_short_revision_mist(props):
    if 'got_revision' in props:
        return props['got_revision']['mist'][:7]
    return None

@properties.renderer
def folder_version(props):
    if 'version' in props:
        return props['version'].replace('.', '-')
    return None

def mist_factory(branch='master', isPullRequest=False):
    factory = BuildFactory()
    for step in [
        Git(
            haltOnFailure=True,
            logEnviron=False,
            repourl='https://github.com/ethereum/mist.git',
            branch=branch,
            mode='full',
            method='copy',
            codebase='mist',
            retry=(5, 3)
        ),
        SetPropertyFromCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="set-version",
            command='sed -ne "s/.*\\"version\\": \\"\([0-9]*\.[0-9]*\.[0-9]*\)\\".*/\\1/p" package.json',
            property="version"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="npm-install",
            command=["npm", "install"],
            description="npm installing",
            descriptionDone="npm install"
        ),
        ShellCommand(
            haltOnFailure=True,
            logEnviron=False,
            name="gulp-mist",
            command=["gulp", "mist"],
            description="gulping mist",
            descriptionDone="gulp mist"
        )
    ]: factory.addStep(step)

    if not isPullRequest:
        for arch in osVersions:
            for step in [
                ShellCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="zip-mist-%s" % arch,
                    description='packing %s' % arch,
                    descriptionDone='pack %s' % arch,
                    command=['zip', '-r',
                             Interpolate("Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip",
                                         arch=arch,
                                         short_revision=get_short_revision_mist),
                             Interpolate('Mist-%(kw:arch)s-%(kw:folder_version)s',
                                         arch=arch,
                                         folder_version=folder_version)],
                    workdir='build/dist_mist'
                ),
                SetPropertyFromCommand(
                    haltOnFailure=True,
                    logEnviron=False,
                    name="sha256sum-%s" % arch,
                    command=Interpolate('sha256sum Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip | grep -o -w "\w\{64\}"',
                                        arch=arch,
                                        short_revision=get_short_revision_mist),
                    property='sha256sum-%s' % arch,
                    workdir='build/dist_mist'
                ),
                FileUpload(
                    haltOnFailure=True,
                    name='upload-mist-%s' % arch,
                    slavesrc=Interpolate("dist_mist/Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip",
                                         arch=arch,
                                         short_revision=get_short_revision_mist),
                    masterdest=Interpolate("public_html/builds/%(prop:buildername)s/Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip",
                                           arch=arch,
                                           short_revision=get_short_revision_mist),
                    url=Interpolate("/builds/%(prop:buildername)s/Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip",
                                    arch=arch,
                                    short_revision=get_short_revision_mist)
                ),
                MasterShellCommand(
                    name="clean-latest-link-%s" % arch,
                    description='cleaning latest link %s' % arch,
                    descriptionDone='clean latest link %s' % arch,
                    command=['rm', '-f', Interpolate("public_html/builds/%(prop:buildername)s/Mist-%(kw:arch)s-latest.zip",
                                                     arch=arch)]
                ),
                MasterShellCommand(
                    haltOnFailure=True,
                    name="link-latest-%s" % arch,
                    description='linking latest %s' % arch,
                    descriptionDone='link latest %s' % arch,
                    command=['ln', '-sf',
                             Interpolate("Mist-%(prop:version)s-%(kw:arch)s-%(kw:short_revision)s.zip",
                                         arch=arch,
                                         short_revision=get_short_revision_mist),
                             Interpolate("public_html/builds/%(prop:buildername)s/Mist-%(kw:arch)s-latest.zip",
                                         arch=arch)]
                )
            ]: factory.addStep(step)

    return factory
