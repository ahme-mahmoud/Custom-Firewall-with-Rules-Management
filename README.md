# Custom Firewall Project

**Description:**  
A Linux Bash-based firewall management system that allows users to **add, delete, and manage firewall rules**, monitor network traffic, log events, and view traffic statistics. The system uses an interactive CLI and SQLite for logging.  

---
## **Project Structure**
```
custom_firewall_project/
├── add_rule.sh # Add firewall rules
├── delete_rule.sh # Delete firewall rules
├── firewall_menu.sh # CLI user interface
├── log_traffic.sh # Monitor and log traffic
├── show_stats.sh # Display traffic statistics
├── firewall.db # SQLite database
├── logs/
│ └── firewall.log # Traffic log file
```
---

## **Features**
- Add, remove, and modify firewall rules.
- Block or allow traffic by **IP, port, or protocol**.
- Log all traffic events for auditing.
- View statistics and summaries of network activity.
- Interactive command-line interface for easy management.


