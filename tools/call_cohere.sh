#!/bin/bash
model=command-a-03-2025
version=1
stream=false
message="Who is the prime minister of Japan?"

here="$(cd "$(dirname $0)"; pwd -P)"
if [ -f .env ]; then
    source .env
fi
help_exit() {
  echo "Usage: $(basename $0) [-s|-n] [-1|-2] [-H path_to_header] [-m message]"
  echo ''
  echo "  -s: stream"
  echo "  -n: non-stream (default)"
  echo "  -1: version 1 (default)"
  echo "  -2: version 2"
  exit 1
}
header_path="/tmp/header.$$"
body_path="/tmp/body.$$"
clean_up() {
  rm -f "${header_path}" "${body_path}"
}
trap clean_up 0 2 9 15
while getopts "sn12H:h" opt; do case "${opt}" in
  s) stream=true ;;
  n) stream=false ;;
  1) version=1 ;;
  2) version=2 ;;
  H) header="${OPTARG}" ;;
  m) message="${OPTARG}" ;;
  h|\?) help_exit ;;
esac; done

header_template="${here}/header_cohere_template"
body_template="${here}/body_coherev${version}_template"

if [ -z "${header}" ]; then
  cat "${header_template}" | sed -e 's/${CO_API_KEY}/'"${CO_API_KEY}"'/' > "${header_path}"
else
  echo "${header}" > "${heeader_path}"
fi
echo "Header:"
cat "${header_path}"

cat "${body_template}" \
  | sed -e 's/${model}/'"${model}"'/;s/${message}/'"${message}"'/;s/${stream}/'"${stream}"'/' \
  > "${body_path}"
echo "Body:"
cat "${body_path}"

set -ex
#curlh -X POST --data @tmp/bodyv${version}${stream} -H @${header_path} --url http://127.0.0.1:8000/v${version}/chat
curlh -X POST --data @${body_path} -H @${header_path} --url http://127.0.0.1:8000/v${version}/chat
