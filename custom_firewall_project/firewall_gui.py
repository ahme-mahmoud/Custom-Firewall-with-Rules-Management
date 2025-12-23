import gi
import subprocess
import json
import os
import re
import shutil
from datetime import datetime

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Use absolute paths to ensure scripts are found
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULE_MANAGER = os.path.join(BASE_DIR, 'rule_manager.sh')
FIREWALL = os.path.join(BASE_DIR, 'firewall.sh')
LOGGER = os.path.join(BASE_DIR, 'logger.sh')
LOG_FILE = os.path.join(BASE_DIR, 'firewall_gui.log')

class FirewallGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="🔥 Firewall Manager")
        self.set_border_width(10)
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.apply_css()

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.add(main_box)

        # Header
        header = Gtk.HeaderBar(title="Firewall Manager")
        header.set_subtitle("Manage your firewall rules with ease")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        # Input Fields
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.ip_entry = Gtk.Entry()
        self.ip_entry.set_placeholder_text("IP (e.g., 192.168.1.1)")
        self.ip_entry.set_tooltip_text("Enter a valid IP address or leave blank")
        
        self.port_entry = Gtk.Entry()
        self.port_entry.set_placeholder_text("Port (e.g., 80)")
        self.port_entry.set_tooltip_text("Enter a valid port number or leave blank")
        
        self.proto_combo = Gtk.ComboBoxText()
        for proto in ["TCP", "UDP", "All"]:
            self.proto_combo.append_text(proto)
        self.proto_combo.set_active(0)
        self.proto_combo.set_tooltip_text("Select the protocol")

        self.action_combo = Gtk.ComboBoxText()
        for action in ["Allow", "Block"]:
            self.action_combo.append_text(action)
        self.action_combo.set_active(0)
        self.action_combo.set_tooltip_text("Select the action for the rule")

        add_button = Gtk.Button(label="➕ Add Rule")
        add_button.get_style_context().add_class("suggested-action")
        add_button.connect("clicked", self.on_add_rule)

        input_box.pack_start(self.ip_entry, True, True, 0)
        input_box.pack_start(self.port_entry, True, True, 0)
        input_box.pack_start(self.proto_combo, False, False, 0)
        input_box.pack_start(self.action_combo, False, False, 0)
        input_box.pack_start(add_button, False, False, 0)

        # Action Buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        delete_button = Gtk.Button(label="❌ Delete Rule")
        delete_button.get_style_context().add_class("destructive-action")
        delete_button.connect("clicked", self.on_delete_rule)
        
        export_button = Gtk.Button(label="📤 Export Rules")
        export_button.connect("clicked", self.on_export_rules)
        
        export_logs_button = Gtk.Button(label="🗂 Export Logs")
        export_logs_button.connect("clicked", self.on_export_logs)
        
        traffic_button = Gtk.Button(label="🔍 Check Traffic")
        traffic_button.connect("clicked", self.check_traffic)
        
        stats_button = Gtk.Button(label="📊 Show Stats")
        stats_button.connect("clicked", self.show_stats)

        action_box.pack_start(export_button, True, True, 0)
        action_box.pack_start(export_logs_button, True, True, 0)
        action_box.pack_start(delete_button, True, True, 0)
        action_box.pack_start(traffic_button, True, True, 0)
        action_box.pack_start(stats_button, True, True, 0)

        # Rule Table
        self.rule_store = Gtk.ListStore(str, str, str, str)
        self.rule_tree = Gtk.TreeView(model=self.rule_store)
        self.rule_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        for i, title in enumerate(["Action", "IP", "Port", "Protocol"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=i)
            col.set_sort_column_id(i)
            col.set_resizable(True)
            self.rule_tree.append_column(col)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.rule_tree)

        # Add all to main box
        main_box.pack_start(input_box, False, False, 0)
        main_box.pack_start(action_box, False, False, 0)
        main_box.pack_start(scroll, True, True, 0)

        # Real-time validation
        self.ip_entry.connect("changed", self.validate_ip)
        self.port_entry.connect("changed", self.validate_port)

        self.refresh_rules()

    def apply_css(self):
        css = """
        window {
            background-color: #1c2526;
            transition: all 0.2s ease;
        }
        button {
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 500;
            background-color: #2a363b;
            color: #e0e0e0;
        }
        button.suggested-action {
            background-color: #4CAF50;
            color: white;
        }
        button.destructive-action {
            background-color: #f44336;
            color: white;
        }
        button:hover {
            background-color: #3c4649;
        }
        entry {
            border-radius: 4px;
            padding: 6px;
            background-color: #2a363b;
            color: #e0e0e0;
            border: 1px solid #444;
        }
        entry.error {
            border: 1px solid #f44336;
        }
        label {
            padding: 8px;
            color: #e0e0e0;
        }
        treeview {
            background-color: #2a363b;
            color: #e0e0e0;
            border-radius: 4px;
        }
        treeview:selected {
            background-color: #2196F3;
            color: white;
        }
        headerbar {
            background-color: #1c2526;
            color: #e0e0e0;
        }
        headerbar label {
            color: #e0e0e0;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def validate_ip(self, entry):
        text = entry.get_text()
        if text and not re.match(r'^(\d{1,3}\.){0,3}\d{0,3}$', text):
            entry.get_style_context().add_class("error")
        else:
            entry.get_style_context().remove_class("error")

    def validate_port(self, entry):
        text = entry.get_text()
        if text and not text.isdigit():
            entry.get_style_context().add_class("error")
        else:
            entry.get_style_context().remove_class("error")

    def log_to_file(self, message):
        with open(LOG_FILE, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")

    def check_dependencies(self, scripts):
        if not shutil.which('jq'):
            self.log_to_file("Dependency error: jq not found")
            self.show_message("Error: 'jq' command not found. Please install jq to parse JSON.")
            return False
        for script in scripts:
            if not os.path.isfile(script):
                self.log_to_file(f"Dependency error: {script} not found")
                self.show_message(f"Error: {script} not found in {BASE_DIR}.")
                return False
            if not os.access(script, os.X_OK):
                self.log_to_file(f"Dependency error: {script} not executable")
                self.show_message(f"Error: {script} is not executable. Run 'chmod +x {script}' to fix.")
                return False
        return True

    def on_add_rule(self, button):
        if not self.check_dependencies([RULE_MANAGER]):
            return
        action = self.action_combo.get_active_text().lower()
        ip = self.ip_entry.get_text().strip()
        port = self.port_entry.get_text().strip()
        proto = self.proto_combo.get_active_text().lower()

        if ip and not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
            self.show_message("Invalid IP address format.")
            return
        if port and not port.isdigit():
            self.show_message("Port must be a number.")
            return

        try:
            result = subprocess.check_output([RULE_MANAGER, 'add_rule', action, ip, port, proto], stderr=subprocess.STDOUT)
            self.log_to_file(f"Add rule: {result.decode().strip()}")
            self.refresh_rules()
            self.ip_entry.set_text("")
            self.port_entry.set_text("")
            self.show_message("Rule added successfully!")
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode().strip() if e.output else "No error details provided."
            self.log_to_file(f"Add rule error: {error_msg}")
            self.show_message(f"Failed to add rule: {error_msg}")

    def on_delete_rule(self, button):
        if not self.check_dependencies([RULE_MANAGER]):
            return
        selection = self.rule_tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is None:
            self.show_message("Please select a rule to delete.")
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are you sure you want to delete this rule?"
        )
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            index = model.get_path(treeiter)[0]
            try:
                result = subprocess.check_output([RULE_MANAGER, 'delete_rule', str(index)], stderr=subprocess.STDOUT)
                self.log_to_file(f"Delete rule: {result.decode().strip()}")
                self.refresh_rules()
                self.show_message("Rule deleted successfully!")
            except subprocess.CalledProcessError as e:
                error_msg = e.output.decode().strip() if e.output else "No error details provided."
                self.log_to_file(f"Delete rule error: {error_msg}")
                self.show_message(f"Failed to delete rule: {error_msg}")

    def on_export_rules(self, button):
        if not self.check_dependencies([RULE_MANAGER]):
            return
        try:
            result = subprocess.check_output([RULE_MANAGER, 'export_rules'], stderr=subprocess.STDOUT)
            self.log_to_file(f"Export rules: {result.decode().strip()}")
            self.show_message("Rules exported successfully!")
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode().strip() if e.output else "No error details provided."
            self.log_to_file(f"Export rules error: {error_msg}")
            self.show_message(f"Failed to export rules: {error_msg}")

    def on_export_logs(self, button):
        if not self.check_dependencies([LOGGER]):
            return
        try:
            result = subprocess.check_output([LOGGER, 'export_logs'], stderr=subprocess.STDOUT)
            self.log_to_file(f"Export logs: {result.decode().strip()}")
            self.show_message("Logs exported successfully!")
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode().strip() if e.output else "No error details provided."
            self.log_to_file(f"Export logs error: {error_msg}")
            self.show_message(f"Failed to export logs: {error_msg}")

    def refresh_rules(self, *args):
        self.rule_store.clear()
        try:
            with open(os.path.join(BASE_DIR, 'rules.json')) as f:
                data = json.load(f)
                for rule in data:
                    self.rule_store.append([
                        rule['action'].capitalize(),
                        rule['ip'] or "Any",
                        rule['port'] or "Any",
                        rule['protocol'].upper()
                    ])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log_to_file(f"Refresh rules error: {str(e)}")
            self.show_message("Failed to load rules. Check rules.json file.")

    def check_traffic(self, button):
        dialog = Gtk.Dialog(title="Check Network Traffic", transient_for=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_margin_end(10)

        ip = Gtk.Entry()
        ip.set_placeholder_text("IP (e.g., 192.168.1.1)")
        ip.set_tooltip_text("Enter a valid IP address or leave blank")
        
        port = Gtk.Entry()
        port.set_placeholder_text("Port (e.g., 80)")
        port.set_tooltip_text("Enter a valid port number or leave blank")
        
        proto = Gtk.ComboBoxText()
        for p in ["TCP", "UDP", "All"]:
            proto.append_text(p)
        proto.set_active(0)
        proto.set_tooltip_text("Select the protocol")

        box.pack_start(ip, True, True, 0)
        box.pack_start(port, True, True, 0)
        box.pack_start(proto, True, True, 0)
        box.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            ip_text = ip.get_text().strip()
            port_text = port.get_text().strip()
            proto_text = proto.get_active_text().lower()

            if ip_text and not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_text):
                self.show_message("Invalid IP address format.")
                dialog.destroy()
                return
            if port_text and not port_text.isdigit():
                self.show_message("Port must be a number.")
                dialog.destroy()
                return

            if not self.check_dependencies([FIREWALL, LOGGER]):
                dialog.destroy()
                return

            # Execute firewall.sh
            command = [FIREWALL, ip_text, port_text, proto_text]
            self.log_to_file(f"Executing check_traffic: {' '.join(command)}")
            try:
                result = subprocess.check_output(command, stderr=subprocess.STDOUT)
                output = result.decode().strip()
                if not output:
                    self.log_to_file("Check traffic: No output returned")
                    self.show_message("No traffic data returned. Check if rules.json exists or firewall.sh is functioning correctly.")
                else:
                    self.log_to_file(f"Check traffic result: {output}")
                    self.show_message(f"Traffic Result for IP: {ip_text or 'Any'}, Port: {port_text or 'Any'}, Protocol: {proto_text.upper()}:\n{output.capitalize()}")
            except subprocess.CalledProcessError as e:
                error_output = e.output.decode().strip() if e.output else "No error details provided."
                self.log_to_file(f"Check traffic error: {str(e)}, Output: {error_output}")
                self.show_message(f"Error checking traffic: {str(e)}\nCommand: {' '.join(command)}\nOutput: {error_output}")
            except Exception as e:
                self.log_to_file(f"Check traffic unexpected error: {str(e)}")
                self.show_message(f"Unexpected error: {str(e)}\nCommand: {' '.join(command)}")
        dialog.destroy()

    def show_stats(self, button):
        if not self.check_dependencies([LOGGER]):
            return
        try:
            result = subprocess.check_output([LOGGER, 'show_stats'], stderr=subprocess.STDOUT)
            self.log_to_file(f"Show stats: {result.decode().strip()}")
            self.show_message(f"Firewall Stats:\n{result.decode().strip()}")
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode().strip() if e.output else "No error details provided."
            self.log_to_file(f"Show stats error: {error_msg}")
            self.show_message(f"Stats unavailable: {error_msg}")

    def show_message(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

if __name__ == '__main__':
    win = FirewallGUI()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
