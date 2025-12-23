#!/bin/bash

validate_input() {
    [[ "$1" != "allow" && "$1" != "block" ]] && echo "Invalid action" && return 1
    [[ -n "$2" && ! "$2" =~ ^[0-9.]+$ ]] && echo "Invalid IP" && return 1
    [[ -n "$3" && ! "$3" =~ ^[0-9]+$ ]] && echo "Invalid port" && return 1
    [[ "$4" != "tcp" && "$4" != "udp" && "$4" != "all" ]] && echo "Invalid protocol" && return 1
    return 0
}

add_rule() {
    local action="$1"
    local ip="$2"
    local port="$3"
    local protocol="$4"

validate_input "$action" "$ip" "$port" "$protocol" || return

[[ ! -f rules.json ]] && echo "[]" > rules.json

# Prevent duplicate rule
if jq -e --arg a "$action" --arg ip "$ip" --arg port "$port" --arg proto "$protocol" \
    '.[] | select(.action==$a and .ip==$ip and .port==$port and .protocol==$proto)' rules.json > /dev/null; then
    echo " Rule already exists."
    return
fi

jq --arg action "$action" --arg ip "$ip" --arg port "$port" --arg protocol "$protocol" \
    '. += [{"action": $action, "ip": $ip, "port": $port, "protocol": $protocol}]' rules.json > tmp && mv tmp rules.json
echo " Rule added."


}

show_rules() {
    jq . rules.json 2>/dev/null || echo "No rules found."
}

delete_rule() {
    local index="$1"
    [[ ! -f rules.json ]] && echo "⚠️ No rules to delete." && return
    total=$(jq length rules.json)
    if [[ "$index" =~ ^[0-9]+$ && $index -ge 0 && $index -lt $total ]]; then
    	jq "del(.[$index])" rules.json > tmp && mv tmp rules.json
    	echo " Rule deleted."
    else
    	echo " Invalid index."
    fi

}

export_rules() {
    jq . rules.json > rules_export.json
    jq -r '["action","ip","port","protocol"], (.[] | [.action, .ip, .port, .protocol]) | @csv' rules.json > rules_export.csv
    echo "✅ Rules exported."
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    case "$1" in
        add_rule) shift; add_rule "$@" ;;
        delete_rule) shift; delete_rule "$1" ;;
        export_rules) export_rules ;;
        show_rules) show_rules ;;
    esac
fi
