#! /bin/bash

echo "Post-release script initialized..."

LATEST_TAG=$(git tag -l | tail -1)
STRIPPED=$(grep -ioP "v\K.*" <<< $LATEST_TAG)

if [[ $LATEST_TAG == *"post"* ]]; then
    SHORT_VERS=$(sed -rn 's/(.*)\.post.*/\1/p' <<< $STRIPPED)
    POST_VERS=$(($(grep -ioP "post\K.*" <<< $LATEST_TAG)+1))
else
    SHORT_VERS=$(sed -r 's/\.post.*//p' <<< $STRIPPED)
    POST_VERS="0"
fi

NEW_VERS="$SHORT_VERS.post$POST_VERS"

echo "Updating project version..."
sed -i '0,/version = ".*"/{s/version = ".*"/version = "'$NEW_VERS'"/}' pyproject.toml

echo "Updating init version..."
sed -i 's/__version__ = ".*"/__version__ = "'$NEW_VERS'"/' yami/__init__.py

./scripts/update-sha.sh "HEAD"

echo "Committing changes..."

git config --global user.name "Jonxslays"
git config --global user.email "51417989+Jonxslays@users.noreply.github.com"

git fetch
git commit -am "Post release - bump version number to $NEW_VERS [skip ci]"
git push origin master

echo "Done!"
