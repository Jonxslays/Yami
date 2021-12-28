#! /bin/bash

echo "Deploying docs for $1..."

if [ $1 = "stable" ]; then
    TAG=$(git tag -l | tail -1)
    MESSAGE="Stable $TAG docs deploy from ${GITHUB_SHA::7}"
    BUILD_DIR=$(grep -ioP "v\K.*" <<< $TAG)
    sed -ri "s/\/Yami\/(.*)'/\/Yami\/"$BUILD_DIR"'/" index.html
elif [ $1 = "master" ]; then
    MESSAGE="Master docs deploy from ${GITHUB_SHA::7}"
    BUILD_DIR="master"
else
    echo "$1 doesn't match 'stable' or 'master', exiting..."
    exit 1
fi

git config --global user.name "Jonxslays"
git config --global user.email "51417989+Jonxslays@users.noreply.github.com"
git fetch && git checkout gh-pages

if [ ! -d "docs/build" ]; then
    echo "Docs build directory is missing, exiting..."
    exit 1
fi

rm -rf $BUILD_DIR
mv docs/build $BUILD_DIR

echo "Committing changes..."

git add .
git commit -m "$MESSAGE"
git push origin gh-pages

echo "Done!"
