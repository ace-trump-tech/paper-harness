#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
versions_dir="$root_dir/versions"
mkdir -p "$versions_dir"

clone_or_update() {
  local name="$1"
  local url="$2"
  if [[ -d "$versions_dir/$name/.git" ]]; then
    git -C "$versions_dir/$name" pull --ff-only
  else
    git clone "$url" "$versions_dir/$name"
  fi
}

clone_or_update paper-harness-undergraduate https://github.com/ace-trump-tech/paper-harness-undergraduate.git
clone_or_update paper-harness-professional https://github.com/ace-trump-tech/paper-harness-professional.git
