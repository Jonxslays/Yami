#! /bin/bash

PROJECT_VERS=$(grep -m 1 -oP 'version = "(.*)"' pyproject.toml | sed -rn 's/.*"(.*)"/v\1/p')
INIT_VERS=$(sed -rn 's/__version__ = "(.*)"/v\1/p' yami/__init__.py)

if [ ! $INIT_VERS = $PROJECT_VERS ]; then
    echo "Project version doesn't match init version!"
    exit 1
else
    echo $PROJECT_VERS
fi
