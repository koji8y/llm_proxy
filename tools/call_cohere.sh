#!/bin/bash
stream=false
message="Who is the prime minister of Japan?"

here="$(cd "$(dirname $0)"; pwd -P)"
if [ -f .env ]; then
    source .env
fi

curlh() {
  echo "curl $@" 1>&2
  curl -N --no-progress-meter -D /dev/stderr "$@"
}
help_exit() {
  echo "Usage: $(basename $0) [-s|-n] [-1|-2|-o] [-H path_to_header] [-m message] [-u base_url] [-k key_variable] [-M]"
  echo ''
  echo "  -s: stream"
  echo "  -n: non-stream (default)"
  echo "  -1: Cohere version 1 (default)"
  echo "  -2: Cohereversion 2"
  echo "  -o: OpenAI"
  echo "  -M: get models instead of chatting"
  exit 1
}
header_path="/tmp/header.$$"
body_path="/tmp/body.$$"
clean_up() {
  rm -f "${header_path}" "${body_path}"
}
trap clean_up 0 2 9 15
while getopts "sn12oH:u:k:Mh" opt; do case "${opt}" in
  s) stream=true ;;
  n) stream=false ;;
  1) cohere_version=1 ;;
  2) cohere_version=2 ;;
  o) openai=yes ;;
  H) header="${OPTARG}" ;;
  m) message="${OPTARG}" ;;
  u) base_url="${OPTARG}" ;;
  k) key_variable="${OPTARG}" ;;
  M) get_models=yes ;;
  h|\?) help_exit ;;
esac; done

if [ -n "${cohere_version}" ]; then
  header_template="${here}/header_cohere_template"
  body_template="${here}/body_coherev${cohere_version}_template"
  path="v${cohere_version}/chat"
  model="${model:- command-a-03-2025}"
  base_url="${base_url:-https://api.cohere.com/}"
  key_variable="${key_variable:-CO_API_KEY}"
elif [ -n "${openai}" ]; then
  header_template="${here}/header_openai_template"
  body_template="${here}/body_openai_template"
  path="v1/chat/completions"
  model="${model:- gpt-5}"
  base_url="${base_url:-https://api.openai.com/}"
  key_variable="${key_variable:-OPENAI_API_KEY}"
else
  echo "Error: Specify either -1 or -2 for Cohere version, or -o for OpenAI." >&2
  help_exit
fi
base_url="${base_url%/}"


if [ -z "${header}" ]; then
  cat "${header_template}" \
    | sed -e 's/${API_KEY}/'"${!key_variable}"'/' \
    > "${header_path}"
else
  echo "${header}" > "${heeader_path}"
fi
echo "[Header:]" 1>&2
cat "${header_path}" 1>&2

if [ -n "${get_models}" ]; then
  path="${path%/}"
  path="${path%/completions}"
  path="${path%/chat}/models"
  # cat "${body_template}" \
  #   | sed -e 's/${model}/'"${model}"'/;s/${message}/'"${message}"'/;s/${stream}/'"${stream}"'/' \
  #   > "${body_path}"
  # echo "[Body:]"
  # cat "${body_path}"
  curlh -X GET -H @${header_path} --url ${base_url}/${path}
  exit 0
fi

cat "${body_template}" \
  | sed -e 's/${model}/'"${model}"'/;s/${message}/'"${message}"'/;s/${stream}/'"${stream}"'/' \
  > "${body_path}"
echo "[Body:]" 1>&2
cat "${body_path}" 1>&2

curlh -X POST --data @${body_path} -H @${header_path} --url ${base_url}/${path}
