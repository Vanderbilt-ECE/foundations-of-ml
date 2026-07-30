#!/usr/bin/env bash
set -euo pipefail

course_root=$(pwd)
audit_temp=$(mktemp -d)
server_pid=''

cleanup() {
  if [[ -n "$server_pid" ]]; then
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  playwright-cli -s=slidev-audit close >/dev/null 2>&1 || true
  rm -r "$audit_temp"
}
trap cleanup EXIT

find . \
  -path '*/node_modules' -prune -o \
  -path '*/Presentations/*/slides.md' -print0 | sort -z |
while IFS= read -r -d '' slides; do
  deck=${slides%/slides.md}
  "$course_root/slidev_template/node_modules/.bin/slidev" "$slides" --port 3131 \
    >"$audit_temp/server.log" 2>&1 &
  server_pid=$!

  ready=false
  for _ in {1..100}; do
    if curl -fsS 'http://127.0.0.1:3131/1' >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 0.1
  done
  if [[ "$ready" != true ]]; then
    sed -n '1,160p' "$audit_temp/server.log"
    exit 1
  fi

  playwright-cli -s=slidev-audit open 'http://127.0.0.1:3131/1?clicks=99' >/dev/null
  playwright-cli -s=slidev-audit resize 1920 1080 >/dev/null
  result=$(playwright-cli -s=slidev-audit --raw run-code --filename=scripts/audit_slidev.js)
  printf '%s\t%s\n' "$deck" "$result"
  if [[ "$result" != *',"passed":true}' ]]; then
    exit 1
  fi

  playwright-cli -s=slidev-audit close >/dev/null 2>&1 || true
  kill "$server_pid" 2>/dev/null || true
  wait "$server_pid" 2>/dev/null || true
  server_pid=''
done
