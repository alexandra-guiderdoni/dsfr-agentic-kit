#!/usr/bin/env bash

python_with_pyyaml() {
  if python3 -c 'import yaml' >/dev/null 2>&1; then
    python3 "$@"
    return
  fi

  if command -v uv >/dev/null 2>&1; then
    local cache_owner="${UID:-user}"
    local uv_cache_dir="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/dsfr-agentic-kit-uv-cache-${cache_owner}}"
    if ! mkdir -p -- "$uv_cache_dir"; then
      printf '[FAIL] impossible de créer le cache uv inscriptible : %s\n' "$uv_cache_dir" >&2
      return 2
    fi

    local status
    if UV_CACHE_DIR="$uv_cache_dir" uv run --quiet --with PyYAML python3 "$@"; then
      status=0
    else
      status=$?
    fi
    return "$status"
  fi

  python3 "$@"
}
