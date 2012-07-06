#!/bin/sh
# Make snapshot of nacl-binutils
# Author: Elan Ruusamäe <glen@pld-linux.org>
# $Id$
set -e

# Generated from git
# git clone http://git.chromium.org/native_client/nacl-gcc.git
# (Checkout ID taken from chromium-15.0.874.106/native_client/tools/REVISIONS)
# cd nacl-gcc
# git checkout cff9ac884908ba53ae16149e7c7d19c336aa4895
# cd ..
# For gcc version, echo gcc/BASE-VER
# mv nacl-gcc nacl-gcc-4.4.3-gitcff9ac88
# tar cfj nacl-gcc-4.4.3-gitcff9ac88.tar.bz2 nacl-gcc-4.4.3-gitcff9ac88

package=nacl-gcc
repo_url=http://git.chromium.org/native_client/$package.git
specfile=crossnacl-gcc.spec

chrome_version=20.0.1132.47

chrome_revision=$(curl -s https://omahaproxy.appspot.com/revision?version=$chrome_version)
chrome_branch=$(IFS=.; set -- $chrome_version; echo $3)
test -e DEPS.py || svn cat http://src.chromium.org/chrome/branches/$chrome_branch/src/DEPS@$chrome_revision > DEPS.py
nacl_revision=$(awk -F'"' '/nacl_revision.:/{print $4}' DEPS.py)

# nacl_revision taken from src/DEPS of chrome 20.0.1132.47
nacl_revision=8118

export GIT_DIR=$package/.git

if [ ! -d $package ]; then
	install -d $package
	git init
	git remote add origin $repo_url
	git fetch --depth 1 origin refs/heads/master:refs/remotes/origin/master
else
	git fetch origin refs/heads/master:refs/remotes/origin/master
fi

# get src/native_client/tools/REVISIONS directly from svn
test -e NACL_REVISIONS.sh || svn cat https://src.chromium.org/native_client/trunk/src/native_client/tools/REVISIONS@$nacl_revision > NACL_REVISIONS.sh

if grep -Ev '^(#|(LINUX_HEADERS_FOR_NACL|NACL_(BINUTILS|GCC|GDB|GLIBC|NEWLIB))_COMMIT=[0-9a-f]+$|)' NACL_REVISIONS.sh >&2; then
	echo >&2 "I refuse to execute grabbed file for security concerns"
	exit 1
fi
. ./NACL_REVISIONS.sh

githash=$NACL_GCC_COMMIT
version=$(git show $githash:gcc/BASE-VER)
shorthash=$(git rev-parse --short $githash)
prefix=$package-$version-git$shorthash

if [ -f $prefix.tar.bz2 ]; then
	echo "Tarball $prefix.tar.bz2 already exists at $shorthash"
	exit 0
fi

git archive $githash --prefix $prefix/ > $prefix.tar
bzip2 -9 $prefix.tar

../dropin $prefix.tar.bz2

rm -f NACL_REVISIONS.sh DEPS.py
