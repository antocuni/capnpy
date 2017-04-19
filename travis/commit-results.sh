#!/bin/bash

echo "Commit result..."
#set -v

# get SHA and EMAIL of the current revision
SHA=`git rev-parse --verify HEAD`
EMAIL=`git --no-pager show -s --format='<%ae>' HEAD`

# setup ssh auth
chmod 600 ./travis/travis.rsa
eval `ssh-agent -s`
ssh-add ./travis/travis.rsa

# commit to benchrepo
cd .benchmarks
REPO=`git config remote.origin.url`
TARGET_BRANCH=benchmarks
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}

git config push.default simple
git config user.email "$EMAIL"
git config user.name "Travis CI"

# git fetch origin $TARGET_BRANCH:$TARGET_BRANCH
# git checkout $TARGET_BRANCH || (git checkout --orphan $TARGET_BRANCH; git rm --cached -r .)
git pull # pull again and hope in a fast-forward, in case another travis job
         # committed in the meantime
git add .
git commit -m "add benchmark results:
  - commit $SHA
  - travis job $TRAVIS_JOB_NUMBER
  - https://travis-ci.org/antocuni/capnpy/jobs/$TRAVIS_JOB_ID
"
git push $SSH_REPO $TARGET_BRANCH
