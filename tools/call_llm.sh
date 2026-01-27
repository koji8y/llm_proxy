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
  echo "Usage: $(basename $0) [-s|-n] [-1|-2|-c|-o] [-H path_to_header] [-m message] [-u base_url] [-k key_variable] [-L] [-M model_name] [-P]"
  echo ''
  echo "  -s: stream"
  echo "  -n: non-stream (default)"
  echo "  -1: Cohere version 1"
  echo "  -2: Cohere version 2"
  echo "  -c: Cohere OpenAI compatible"
  echo "  -o: OpenAI"
  echo "  -H: specify the path to the header (not its template)"
  echo "  -m: specify the message to send"
  echo "  -u: specify the base URL to the LLM to connect"
  echo "  -k: speicify the variable name for the API key"
  echo "  -L: get models instead of chatting"
  echo "  -M: get the specific model's information instead of chatting"
  echo "  -P: preserve temporal file"
  exit 1
}
while getopts "sn12coH:u:k:LM:Ph" opt; do case "${opt}" in
  s) stream=true ;;
  n) stream=false ;;
  1) cohere_version=1 ;;
  2) cohere_version=2 ;;
  c) openai=cohere ;;
  o) openai=openai ;;
  H) header="${OPTARG}" ;;
  m) message="${OPTARG}" ;;
  u) base_url="${OPTARG}" ;;
  k) key_variable="${OPTARG}" ;;
  L) get_models=yes ;;
  M) target_model="${OPTARG}" ;;
  P) preserve_tmp=true ;;
  h|\?) help_exit ;;
esac; done

header_path="/tmp/header.$$"
body_path="/tmp/body.$$"

clean_up() {
  case "${preserve_tmp}" in
    true) ;;
    *) rm -f "${header_path}" "${body_path}" ;;
  esac
}
trap clean_up 0 2 9 15

if [ -n "${cohere_version}" ]; then
  header_template="${here}/${HEADER_COHERE_TEMPLATE:-header_cohere_template}"
  body_template="${here}/body_coherev${cohere_version}_template"
  model="${model:-command-a-03-2025}"
  path="v${cohere_version}/chat"
  base_url="${base_url:-https://api.cohere.com/}"
  key_variable="${key_variable:-CO_API_KEY}"
elif [ -n "${openai}" ]; then
  header_template="${here}/header_openai_template"
  body_template="${here}/body_openai_template"
  model="${model:-gpt-5}"
  case "${openai}" in
    cohere)
      path="compatibility/v1/chat/completions"
      base_url="${base_url:-https://api.cohere.com/}"
      key_variable="${key_variable:-CO_API_KEY}"
      ;;
    *)
      path="v1/chat/completions"
      base_url="${base_url:-https://api.openai.com/}"
      key_variable="${key_variable:-OPENAI_API_KEY}"
      ;;
  esac
else
  echo "Error: Specify either -1 or -2 for Cohere version, -c for Cohere OpenAI-compatible, or -o for OpenAI." >&2
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

if [ -n "${get_models}" ] || [ -n "${target_model}" ]; then
  path="${path%/}"
  path="${path%/completions}"
  path="${path%/chat}/models${target_model+/}${target_model}"
  if [ -n "${COHERE_LIST_MODEL_WO_VERSION}" ] && [ -z "${target_model}" ]; then
    if [ -n "${cohere_version}" ]; then
      path="$(echo "${path}" | sed -e 's:v[12]/::')"
    fi
  fi
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
