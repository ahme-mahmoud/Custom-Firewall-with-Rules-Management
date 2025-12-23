#!/bin/bash

check_traffic() {
    local ip="$1"
    local port="$2"
    local protocol="$3"
    local matched="allow"

    if [ ! -f rules.json ]; then
        echo "$matched"
        return
    fi

    while IFS= read -r rule; do
        action=$(echo "$rule" | jq -r .action)
        rule_ip=$(echo "$rule" | jq -r .ip)
        rule_port=$(echo "$rule" | jq -r .port)
        rule_protocol=$(echo "$rule" | jq -r .protocol)

        [[ "$rule_ip" == "null" ]] && rule_ip=""
        [[ "$rule_port" == "null" ]] && rule_port=""

        if { [ -z "$rule_ip" ] || [ "$rule_ip" == "$ip" ]; } && \
           { [ -z "$rule_port" ] || [ "$rule_port" == "$port" ]; } && \
           { [ "$rule_protocol" == "all" ] || [ "$rule_protocol" == "$protocol" ]; }; then
            matched="$action"
            break
        fi
    done < <(jq -c '.[]' rules.json)

    ./logger.sh "$ip" "$port" "$protocol" "$matched"
    echo "$matched"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    check_traffic "$@"
fi
