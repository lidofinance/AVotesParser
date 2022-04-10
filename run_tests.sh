#!/bin/bash
if [ "$#" -ne 2 ]; then
  echo "Usage: run_tests.sh <etherscan-api-key> <infura-project-id>"
  exit 0
fi

API_KEY="$1"
INFURA_ID="$2"

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
  poetry run tox -c "." -- --apikey="$API_KEY" --infura-id="$INFURA_ID"
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
