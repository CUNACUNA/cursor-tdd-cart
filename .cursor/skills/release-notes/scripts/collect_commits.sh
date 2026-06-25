#!/bin/bash
# 사용법: collect_commits.sh <from-ref> <to-ref>
from="${1:-HEAD~20}"
to="${2:-HEAD}"
git log --pretty=format:'- %s (%h)' "$from..$to"
