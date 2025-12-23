#!/bin/bash

. ./rule_manager.sh
. ./firewall.sh
. ./logger.sh

main_menu() {
    while true; do
        echo " Custom Firewall – Interactive Menu "
        echo "1. Show Rules"
        echo "2. Add Rule"
        echo "3. Delete Rule"
        echo "4. Check Traffic"
        echo "5. Show Stats"
        echo "6. Export Rules"
        echo "7. Export Logs"
        echo "8. Exit"
        read -rp "Choose an option: " choice

        case $choice in
            1) show_rules ;;
            2)
                read -rp "Action (allow/block): " action
                read -rp "IP (optional): " ip
                read -rp "Port (optional): " port
                read -rp "Protocol (tcp/udp/all): " proto
                add_rule "$action" "$ip" "$port" "$proto"
                ;;
            3)
                show_rules
                read -rp "Enter index to delete: " index
                delete_rule "$index"
                ;;
            4)
                read -rp "Source IP: " ip
                read -rp "Port: " port
                read -rp "Protocol: " proto
                result=$(./firewall.sh "$ip" "$port" "$proto")
                echo "➡️ Result: $result"
                ;;
            5) show_stats ;;
            6) export_rules ;;
            7) export_logs ;;
            8) echo " Exiting..."; break ;;
            *) echo " Invalid option." ;;
        esac
    done
}

main_menu
