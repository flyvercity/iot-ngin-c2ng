# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

CONTROL_SCRIPT=$1 
SERVICE=$2
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
${SCRIPT_DIR}/${CONTROL_SCRIPT} restart $SERVICE
${SCRIPT_DIR}/${CONTROL_SCRIPT} logs $SERVICE -f
