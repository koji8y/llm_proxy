#!/bin/bash
help_exit() {
  echo "Usage: $(basename $0) [-s|-n] [-1|-2] [-H path_to_header] "
  echo ''
  echo "  -s: stream"
  echo "  -n: non-stream (default)"
  echo "  -1: version 1 (default)"
  echo "  -2: version 2"
  exit 1
}
version=1
stream=ns
header=tmp/header_cohere
while getopts "sn12H:h" opt; do case "${opt}" in
  s) stream=s ;;
  n) stream=ns ;;
  1) version=1 ;;
  2) version=2 ;;
  H) header="${OPTARG}" ;;
  h|\?) help_exit ;;
esac; done

set -ex
curlh -X POST --data @tmp/bodyv${version}${stream} -H @${header} --url http://127.0.0.1:8000/v${version}/chat
