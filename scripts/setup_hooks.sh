#!/usr/bin/env bash
# Configure git to use tracked repo hooks.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/hooks"

if [[ ! -d "$HOOKS_DIR" ]]; then
    echo "ERROR: hooks directory not found: $HOOKS_DIR" >&2
    exit 1
fi

chmod +x "$HOOKS_DIR"/*
git config core.hooksPath hooks

echo "Configured git hooks for AC14."
echo "Commit messages now require [Plan #N], [Trivial], or [Unplanned]."
