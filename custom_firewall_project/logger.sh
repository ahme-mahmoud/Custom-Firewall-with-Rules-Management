#!/bin/bash

ip="$1"
port="$2"
protocol="$3"
action="$4"
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "$timestamp,$ip,$port,$protocol,$action" >> firewall.log

read_logs() {
    cat firewall.log 2>/dev/null || echo "No logs."
}

show_stats() {
    allowed=$(grep allow firewall.log | wc -l)
    blocked=$(grep block firewall.log | wc -l)
    echo "✔️ Allowed: $allowed"
    echo "⛔ Blocked: $blocked"
}

export_logs() {
    echo "timestamp,ip,port,protocol,action" > logs_export.csv
    cat firewall.log >> logs_export.csv
    echo "✅ Logs exported."
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    case "$1" in
        export_logs) export_logs ;;
        show_stats) show_stats ;;
        read_logs) read_logs ;;
    esac
fi







