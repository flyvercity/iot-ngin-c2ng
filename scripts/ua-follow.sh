 SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

${SCRIPT_DIR}/ctrl-sims.sh restart c2ng-ua
${SCRIPT_DIR}/ctrl-sims.sh logs c2ng-ua -f
