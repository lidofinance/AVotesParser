#!/bin/bash
set -e

API_KEY="$ETHERSCAN_TOKEN"
INFURA_ID="$WEB3_INFURA_PROJECT_ID"

if [ -z "$API_KEY" ]; then
  echo "Please set ETHERSCAN_TOKEN env variable"
  exit 1
fi

if [ -z "$INFURA_ID" ]; then
  echo "Please set WEB3_INFURA_PROJECT_ID env variable"
  exit 1
fi

pre_test() {
  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  pushd "$DIR" >/dev/null || exit
}

test_target() {
  local TARGET="${1}"
  local API_KEY="${2}"
  local INFURA_ID="${3}"

  echo "--- RUN TESTS: ${TARGET} ---"
  cd "production/${TARGET}"
  poetry install -v
  poetry shell
  tox -c "." -- --apikey="$API_KEY" --infura-id="$INFURA_ID"
  exit
  rm -rf $HOME/.cache/pypoetry/artifacts/*
  cd -
}

test() {
  TARGETS="avotes-parser-core avotes-parser-cli"
  local API_KEY="${1}"
  local INFURA_ID="${2}"

  for t in $TARGETS; do
    test_target $t "$API_KEY" "$INFURA_ID"
  done
}

pre_test
test "$API_KEY" "$INFURA_ID"
