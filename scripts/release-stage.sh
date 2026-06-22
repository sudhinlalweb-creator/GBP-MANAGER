#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: bash scripts/release-stage.sh <stage-slug> <commit message>"
  echo 'Example: bash scripts/release-stage.sh phase-4-admin "admin panel actions"'
  exit 1
fi

STAGE_SLUG="$1"
shift
STAGE_MESSAGE="$*"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
TAG_NAME="stage-${STAGE_SLUG}-${TIMESTAMP}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This folder is not a Git repository yet."
  echo ""
  echo "Bootstrap it first:"
  echo "  git init"
  echo "  git branch -M main"
  echo "  git add -A"
  echo '  git commit -m "chore: initial platform baseline"'
  echo "  git remote add origin <your-github-repo-url>"
  echo "  git push -u origin main"
  echo ""
  echo "Then rerun:"
  echo "  bash scripts/release-stage.sh ${STAGE_SLUG} \"${STAGE_MESSAGE}\""
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Git is initialized, but no 'origin' remote is configured."
  echo ""
  echo "Add your GitHub remote first:"
  echo "  git remote add origin <your-github-repo-url>"
  echo "  git push -u origin main"
  echo ""
  echo "Then rerun:"
  echo "  bash scripts/release-stage.sh ${STAGE_SLUG} \"${STAGE_MESSAGE}\""
  exit 1
fi

git add -A

if git diff --cached --quiet; then
  echo "No staged changes found. Nothing to release."
  exit 0
fi

git commit -m "stage(${STAGE_SLUG}): ${STAGE_MESSAGE}"
git tag -a "${TAG_NAME}" -m "Stage release ${TAG_NAME}"
git push origin HEAD
git push origin "${TAG_NAME}"

echo "Released ${TAG_NAME}"
