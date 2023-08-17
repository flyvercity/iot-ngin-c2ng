# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

SERVICE=$1
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
${SCRIPT_DIR}/service-follow.sh ctrl-sims.sh $SERVICE
