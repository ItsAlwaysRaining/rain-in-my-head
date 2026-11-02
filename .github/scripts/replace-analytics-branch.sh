#!/usr/bin/env bash
# Replace an analytics branch with ONE new commit holding the two export files, but only if they changed
# (specs/012-usage-tracking, research R9). Run from a checkout of the repository with `origin` set.
#
#   replace-analytics-branch.sh EXPORT_DIR BRANCH
#
# This force-pushes, on purpose: the owner chose "latest copy only", so older copies must leave the branch's
# history. It will only ever touch a branch called `analytics` or `analytics-dev`; anything else is refused.
set -euo pipefail

export_dir="${1:?export directory}"
branch="${2:?branch name}"
files=(usage_events.csv viewers.csv)

case "$branch" in
  analytics | analytics-dev) ;;
  *) echo "Refusing to write to branch '$branch'." >&2; exit 1 ;;
esac
for f in "${files[@]}"; do
  [ -f "$export_dir/$f" ] || { echo "Missing $export_dir/$f" >&2; exit 1; }
done

if git ls-remote --exit-code --heads origin "$branch" > /dev/null 2>&1; then
  git fetch --quiet --depth=1 origin "refs/heads/$branch"
  same=true
  for f in "${files[@]}"; do
    git show "FETCH_HEAD:$f" 2> /dev/null | cmp -s - "$export_dir/$f" || same=false
  done
  if $same; then
    echo "No change since the last export. Nothing to commit."
    exit 0
  fi
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
# A fresh repository holding only the two files, so nothing else from this checkout can end up on the branch.
git init --quiet "$work"
cp "$export_dir"/usage_events.csv "$export_dir"/viewers.csv "$work"/
git -C "$work" add "${files[@]}"
git -C "$work" -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
  commit --quiet -m "Usage export $(date -u +%Y-%m-%dT%H:%MZ)"
# Bring that one commit into this checkout (which holds the push credentials), then replace the branch with it.
git fetch --quiet "$work" HEAD
git push --force origin "FETCH_HEAD:refs/heads/$branch"
echo "Replaced $branch with one commit."
