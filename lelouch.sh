#!/usr/bin/env bash

USER_ID=$(id -u)
GROUP_ID=$(id -g)
WORKSPACE="$(realpath .)"
AGENT="$(realpath examples/hello_agent.py)"

while getopts "a:w:u:k:m:h" arg ; do

case "$arg" in
    h)
        echo "lelouch -p <prompt>"
        exit 0;
        ;;
    a)
        AGENT=$(realpath "$OPTARG")
        ;;
    w)
        WORKSPACE=$(realpath "$OPTARG")
        ;;
    u)
        BASE_URL="$OPTARG"
        ;;
    k)
        API_KEY="$OPTARG"
        ;;
    *)
        echo "error: unknown option"
        exit 1
        ;;
esac

done

shift $(($OPTIND - 1))
PROMPT="$1"

docker run -it --rm \
    --user "${USER_ID}:${GROUP_ID}" \
    -e "BASE_URL=${BASE_URL}" \
    -e "API_KEY=${API_KEY}" \
    -e "MODEL=${MODEL}" \
    -v "${AGENT}:/agent/agent.py:ro" \
    -v "${WORKSPACE}:/workspace" \
    lelouch "${PROMPT}"