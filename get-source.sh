#!/bin/sh
# Make snapshot of nacl-binutils
# Author: Elan Ruusamäe <glen@pld-linux.org>
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
nacl_trunk=http://src.chromium.org/native_client/trunk
omahaproxy_url=https://omahaproxy.appspot.com
specfile=crossnacl-gcc.spec

# if you get errors that sha1 hash not found, try increasing depth
# fatal: Path 'gcc/BASE-VER' does not exist in 'c69a5b7252d2f073d0f526800e4fca3b63cd1fab'
depth=5

chrome_channel=stable
chrome_version=$(curl -s "$omahaproxy_url/?os=linux&channel=$chrome_channel" | awk -F, 'NR > 1{print $3}')
chrome_revision=$(curl -s $omahaproxy_url/revision?version=$chrome_version)
chrome_branch=$(IFS=.; set -- $chrome_version; echo $3)

test -e DEPS.py || svn cat http://src.chromium.org/chrome/branches/$chrome_branch/src/DEPS@$chrome_revision > DEPS.py
nacl_revision=$(awk -F'"' '/nacl_revision.:/{print $4}' DEPS.py)

export GIT_DIR=$package/.git

if [ ! -d $package ]; then
	install -d $package
	git init
	git remote add origin $repo_url
	git fetch --depth $depth origin refs/heads/master:refs/remotes/origin/master
else
	git fetch origin refs/heads/master:refs/remotes/origin/master
fi

# get src/native_client/tools/REVISIONS directly from svn
test -e NACL_REVISIONS.sh || svn cat $nacl_trunk/src/native_client/tools/REVISIONS@$nacl_revision > NACL_REVISIONS.sh

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
	rm -f NACL_REVISIONS.sh DEPS.py
	exit 0
fi

git archive $githash --prefix $prefix/ > $prefix.tar
bzip2 -9 $prefix.tar

../dropin $prefix.tar.bz2

rm -f NACL_REVISIONS.sh DEPS.py