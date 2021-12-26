#! /bin/bash

echo "Updating git sha to $1"

sed -i 's/__git_sha__ = "\[.*\]"/__git_sha__ = "\['$1'\]"/' \
    yami/__init__.py
