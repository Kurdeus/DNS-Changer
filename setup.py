import sys
import subprocess
import ctypes
import json
import os
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QComboBox, QCheckBox, QDialog, QListWidget,
    QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt
import win32con
import win32gui
import win32process
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Restart the script with admin rights if not already running as admin."""
    if sys.platform != "win32":
        return False  # Only relevant on Windows
    try:
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        return True
    except Exception:
        return False

def get_connected_interfaces():
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'show', 'interface'],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.splitlines()
        interfaces = []
        for line in lines:
            # Include all interfaces, not just connected ones
            if line.strip() and not line.startswith('-') and not "Admin State" in line:
                parts = line.strip().split()
                if len(parts) >= 4:
                    interface_name = " ".join(parts[3:])
                    interfaces.append(interface_name)
        return interfaces
    except Exception as e:
        return []

def reset_dns_to_dhcp(interface):
    try:
        # Reset DNS for the specific interface
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'dnsservers', f'name={interface}', 'source=dhcp'],
            check=True
        )
        return True, f'DNS reset to DHCP for "{interface}"'
    except subprocess.CalledProcessError as e:
        if "requires elevation" in str(e).lower():
            return False, "The requested operation requires elevation (Run as administrator)."
        return False, f"Failed to reset DNS for {interface}: {e}"

def set_dns(interface, primary_dns, secondary_dns):
    try:
        # Set DNS for the specific interface
        subprocess.run(
            ['netsh', 'interface', 'ipv4', 'set', 'dnsservers', f'name={interface}', 'source=static', f'addr={primary_dns}', 'register=primary'],
            check=True
        )
        if secondary_dns.strip():
            subprocess.run(
                ['netsh', 'interface', 'ipv4', 'add', 'dnsservers', f'name={interface}', f'addr={secondary_dns}', 'index=2'],
                check=True
            )
        return True, f'DNS set to {primary_dns}, {secondary_dns} for "{interface}"'
    except subprocess.CalledProcessError as e:
        if "requires elevation" in str(e).lower():
            return False, "The requested operation requires elevation (Run as administrator)."
        return False, f"Failed to set DNS for {interface}: {e}"

def set_system_dns(primary_dns, secondary_dns):
    try:
        # Get all interfaces
        interfaces = get_connected_interfaces()
        success_count = 0
        failed_interfaces = []
        
        for interface in interfaces:
            try:
                subprocess.run(
                    ['netsh', 'interface', 'ipv4', 'set', 'dnsservers', f'name={interface}', 'source=static', f'addr={primary_dns}', 'register=primary'],
                    check=True
                )
                if secondary_dns.strip():
                    subprocess.run(
                        ['netsh', 'interface', 'ipv4', 'add', 'dnsservers', f'name={interface}', f'addr={secondary_dns}', 'index=2'],
                        check=True
                    )
                success_count += 1
            except subprocess.CalledProcessError:
                failed_interfaces.append(interface)
                
        if success_count == len(interfaces):
            return True, f'DNS set to {primary_dns}, {secondary_dns} for all interfaces'
        elif success_count > 0:
            return True, f'DNS set for {success_count} interfaces. Failed for: {", ".join(failed_interfaces)}'
        else:
            return False, f'Failed to set DNS for any interface'
    except Exception as e:
        return False, f"Failed to set system DNS: {e}"

def reset_system_dns_to_dhcp():
    try:
        # Get all interfaces
        interfaces = get_connected_interfaces()
        success_count = 0
        failed_interfaces = []
        
        for interface in interfaces:
            try:
                subprocess.run(
                    ['netsh', 'interface', 'ipv4', 'set', 'dnsservers', f'name={interface}', 'source=dhcp'],
                    check=True
                )
                success_count += 1
            except subprocess.CalledProcessError:
                failed_interfaces.append(interface)
                
        if success_count == len(interfaces):
            return True, f'DNS reset to DHCP for all interfaces'
        elif success_count > 0:
            return True, f'DNS reset for {success_count} interfaces. Failed for: {", ".join(failed_interfaces)}'
        else:
            return False, f'Failed to reset DNS for any interface'
    except Exception as e:
        return False, f"Failed to reset system DNS: {e}"

def load_default_dns_configs():
    """Load default DNS configurations from the online source"""
    try:
        url = "https://gist.githubusercontent.com/Kurdeus/6d503d920d063823e65ef3e0a75739c5/raw/dns.json"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to load default DNS configurations: {e}")
        return {}

class SavedDNSDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saved DNS Configurations")
        self.setMinimumWidth(300)
        self.setup_ui()
        self.load_saved_dns()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Selected")
        self.delete_btn = QPushButton("Delete Selected")
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.delete_btn)
        
        self.load_btn.clicked.connect(self.load_selected)
        self.delete_btn.clicked.connect(self.delete_selected)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def load_saved_dns(self):
        self.list_widget.clear()
        saved_dns = {}
        
        # First load local configurations
        if os.path.exists("saved_dns.json"):
            try:
                with open("saved_dns.json", "r") as f:
                    saved_dns = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load saved DNS configurations: {e}")
        
        # Then load default configurations from online source
        default_dns = load_default_dns_configs()
        
        # Merge configurations (local configurations take precedence)
        for name, config in default_dns.items():
            if name not in saved_dns:
                saved_dns[name] = config
        
        # Display all configurations
        for name, config in saved_dns.items():
            secondary = config.get('secondary', '')
            item = QListWidgetItem(f"{name}: {config['primary']}" + (f" / {secondary}" if secondary else ""))
            item.setData(Qt.ItemDataRole.UserRole, {"name": name, "config": config})
            self.list_widget.addItem(item)
    
    def load_selected(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            data = current_item.data(Qt.ItemDataRole.UserRole)
            self.parent().load_dns_config(data["config"]["primary"], data["config"].get("secondary", ""))
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Please select a DNS configuration to load.")
    
    def delete_selected(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            data = current_item.data(Qt.ItemDataRole.UserRole)
            name = data["name"]
            
            reply = QMessageBox.question(self, "Confirm Delete", 
                                        f"Are you sure you want to delete '{name}'?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    saved_dns = {}
                    if os.path.exists("saved_dns.json"):
                        with open("saved_dns.json", "r") as f:
                            saved_dns = json.load(f)
                    
                    if name in saved_dns:
                        del saved_dns[name]
                        
                        with open("saved_dns.json", "w") as f:
                            json.dump(saved_dns, f)
                        
                        self.load_saved_dns()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete DNS configuration: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please select a DNS configuration to delete.")

class DNSChangerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNS Changer")
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Interface selection
        self.interface_label = QLabel("Select Network Interface:")
        self.interface_combo = QComboBox()
        self.refresh_interfaces()
        layout.addWidget(self.interface_label)
        layout.addWidget(self.interface_combo)

        # Primary DNS
        self.primary_label = QLabel("Primary DNS IPv4:")
        self.primary_input = QLineEdit()
        self.primary_input.setPlaceholderText("e.g. 8.8.8.8")
        layout.addWidget(self.primary_label)
        layout.addWidget(self.primary_input)

        # Secondary DNS
        self.secondary_label = QLabel("Secondary DNS IPv4 (optional):")
        self.secondary_input = QLineEdit()
        self.secondary_input.setPlaceholderText("e.g. 8.8.4.4")
        layout.addWidget(self.secondary_label)
        layout.addWidget(self.secondary_input)

        # Apply to all checkbox
        self.apply_all_checkbox = QCheckBox("Apply to all interfaces")
        layout.addWidget(self.apply_all_checkbox)

        # Buttons for DNS operations
        btn_layout = QHBoxLayout()
        self.set_btn = QPushButton("Set DNS")
        self.set_btn.clicked.connect(self.on_set_dns)
        self.clear_btn = QPushButton("Reset to DHCP")
        self.clear_btn.clicked.connect(self.on_clear_dns)
        btn_layout.addWidget(self.set_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
        
        # Buttons for saving/loading DNS
        save_load_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save DNS")
        self.save_btn.clicked.connect(self.on_save_dns)
        self.load_btn = QPushButton("Load DNS")
        self.load_btn.clicked.connect(self.on_load_dns)
        save_load_layout.addWidget(self.save_btn)
        save_load_layout.addWidget(self.load_btn)
        layout.addLayout(save_load_layout)

        self.setLayout(layout)

    def refresh_interfaces(self):
        interfaces = get_connected_interfaces()
        self.interface_combo.clear()
        if interfaces:
            self.interface_combo.addItems(interfaces)
        else:
            self.interface_combo.addItem("No network interfaces found")

    def on_set_dns(self):
        if not is_admin():
            QMessageBox.critical(self, "Elevation Required", "The requested operation requires elevation (Run as administrator).")
            return
            
        primary_dns = self.primary_input.text().strip()
        secondary_dns = self.secondary_input.text().strip()
        
        if not primary_dns:
            QMessageBox.warning(self, "Error", "Primary DNS cannot be empty.")
            return
            
        if self.apply_all_checkbox.isChecked():
            # Apply to all interfaces
            ok, msg = set_system_dns(primary_dns, secondary_dns)
        else:
            # Apply to selected interface
            interface = self.interface_combo.currentText()
            if not interface or interface == "No network interfaces found":
                QMessageBox.warning(self, "Error", "No valid network interface selected.")
                return
            ok, msg = set_dns(interface, primary_dns, secondary_dns)
            
        if ok:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    def on_clear_dns(self):
        if not is_admin():
            QMessageBox.critical(self, "Elevation Required", "The requested operation requires elevation (Run as administrator).")
            return
            
        if self.apply_all_checkbox.isChecked():
            # Reset all interfaces to DHCP
            ok, msg = reset_system_dns_to_dhcp()
        else:
            # Reset selected interface to DHCP
            interface = self.interface_combo.currentText()
            if not interface or interface == "No network interfaces found":
                QMessageBox.warning(self, "Error", "No valid network interface selected.")
                return
            ok, msg = reset_dns_to_dhcp(interface)
            
        if ok:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)
    
    def on_save_dns(self):
        primary_dns = self.primary_input.text().strip()
        secondary_dns = self.secondary_input.text().strip()
        
        if not primary_dns:
            QMessageBox.warning(self, "Error", "Primary DNS cannot be empty.")
            return
        
        name, ok = QInputDialog.getText(self, "Save DNS Configuration", 
                                        "Enter a name for this DNS configuration:")
        
        if ok and name:
            try:
                saved_dns = {}
                if os.path.exists("saved_dns.json"):
                    try:
                        with open("saved_dns.json", "r") as f:
                            saved_dns = json.load(f)
                    except:
                        pass
                
                saved_dns[name] = {
                    "primary": primary_dns,
                    "secondary": secondary_dns
                }
                
                with open("saved_dns.json", "w") as f:
                    json.dump(saved_dns, f)
                
                QMessageBox.information(self, "Success", f"DNS configuration '{name}' saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save DNS configuration: {e}")
    
    def on_load_dns(self):
        dialog = SavedDNSDialog(self)
        dialog.exec()
    
    def load_dns_config(self, primary, secondary):
        self.primary_input.setText(primary)
        self.secondary_input.setText(secondary)

def main():
    if not is_admin():
        # Relaunch as admin
        if run_as_admin():
            sys.exit(0)
        else:
            print("Failed to elevate privileges. Please run as administrator.")
            sys.exit(1)
    if hasattr(sys, 'frozen'):
        # If running as compiled executable
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    else:
        # If running as script, try to hide the console window
        foreground_window = win32gui.GetForegroundWindow()
        if foreground_window:
            _, process_id = win32process.GetWindowThreadProcessId(foreground_window)
            if process_id == os.getpid():
                win32gui.ShowWindow(foreground_window, win32con.SW_HIDE)
    
    app = QApplication(sys.argv)
    window = DNSChangerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
