#!/usr/bin/env bash
set -eu -o pipefail

build() {
    docker build --progress=plain -t joshhsoj1902/pokemonredexperiments:latest .
}

run() {
    docker compose up
}

"$@"