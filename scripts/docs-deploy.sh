#! /bin/bash

echo "Deploying docs for $1..."

if [ $1 = "stable" ]; then
    TAG=$(git tag -l | tail -1)
    MESSAGE="Stable $TAG docs deploy from ${GITHUB_SHA::7}"
elif [ $1 = "master" ]; then
    MESSAGE="Master docs deploy from ${GITHUB_SHA::7}"
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

rm -rf $1
mv docs/build $1

echo "Committing changes..."

git commit -am "$MESSAGE"
git push origin gh-pages

echo "Done!"
