#!/usr/bin/env bash
# Publish the version in pyproject.toml to PyPI.
#
#   ./scripts/release.sh             build, check and upload (asks before uploading)
#   ./scripts/release.sh --dry-run   build and check only, upload nothing
#   ./scripts/release.sh --test      upload to test.pypi.org instead of pypi.org
#   ./scripts/release.sh --yes       do not ask before uploading
#
# Twine asks for your credentials: username __token__, password = your pypi-... API
# token. You can also set TWINE_USERNAME and TWINE_PASSWORD. The token is never stored
# by this script.
#
# Uses `python` from your PATH; set PYTHON=/path/to/python to use another one.
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python}"
dry_run=0
assume_yes=0
repository=()
target="PyPI"

for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --yes) assume_yes=1 ;;
    --test) repository=(--repository testpypi); target="TestPyPI" ;;
    -h | --help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg (try --help)" >&2; exit 1 ;;
  esac
done

fail() {
  echo "Error: $1" >&2
  exit 1
}

version="$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml | head -n 1)"
[ -n "$version" ] || fail "could not read the version from pyproject.toml"
tag="v$version"
echo "Releasing jay_lint $version to $target"

echo "-> Checking git state"
[ "$(git branch --show-current)" = "main" ] || fail "switch to main first (git checkout main)"
# Tracked changes only: untracked files do not end up in the build.
git diff --quiet && git diff --cached --quiet || fail "you have uncommitted changes"
git fetch --quiet origin --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
  || fail "main is not in sync with origin/main (git pull)"
git rev-parse -q --verify "refs/tags/$tag" > /dev/null \
  || fail "tag $tag does not exist (git tag -a $tag -m ... && git push origin $tag)"
# main may be ahead of the tag (e.g. a later commit that only touches scripts), but
# what gets packaged must be exactly what was tagged.
git merge-base --is-ancestor "$tag" HEAD \
  || fail "tag $tag is not part of main's history"
git diff --quiet "$tag" HEAD -- src pyproject.toml README.md \
  || fail "src/, pyproject.toml or README.md changed since $tag; move the tag or bump the version"

if [ "$target" = "PyPI" ]; then
  echo "-> Checking $version is not already on PyPI"
  status="$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/jay_lint/$version/json" || true)"
  [ "$status" != "200" ] || fail "jay_lint $version is already on PyPI; bump the version"
fi

echo "-> Installing build tools"
"$PYTHON" -m pip install --quiet --upgrade build twine

echo "-> Building"
rm -rf dist build
"$PYTHON" -m build
"$PYTHON" -m twine check dist/*

if [ "$dry_run" -eq 1 ]; then
  echo "Dry run: built and checked, nothing uploaded. Files in dist/:"
  ls dist
  exit 0
fi

if [ "$assume_yes" -ne 1 ]; then
  printf 'Upload jay_lint %s to %s? This cannot be undone. [y/N] ' "$version" "$target"
  read -r answer
  case "$answer" in y | Y | yes | YES) ;; *) echo "Cancelled."; exit 1 ;; esac
fi

echo "-> Uploading (username: __token__, password: your pypi-... token)"
"$PYTHON" -m twine upload "${repository[@]}" dist/*
echo "Done. Check it with: pip install --no-cache-dir jay_lint==$version"
