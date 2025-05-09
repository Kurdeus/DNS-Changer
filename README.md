# DNS Changer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0%2B-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![Windows](https://img.shields.io/badge/Windows-10%2B-blue)](https://www.microsoft.com/windows)

A powerful and user-friendly Windows application that allows you to quickly change DNS settings across network interfaces. Perfect for network administrators, developers, and users who frequently need to switch between different DNS configurations.

![DNS Changer Screenshot](https://github.com/Kurdeus/DNS-Changer/blob/main/screenshot/result.png?raw=true)

## ✨ Features

- 🖥️ **Multi-Interface Support**: Set DNS servers for specific or all network interfaces
- 🔄 **Quick Switching**: Easily switch between different DNS configurations
- 💾 **Configuration Management**: Save and load frequently used DNS settings
- 🔒 **Admin Integration**: Automatically runs with administrator privileges
- 🎯 **Simple Interface**: Clean and intuitive user interface
- 🔧 **DHCP Support**: Reset DNS settings to DHCP with one click

## 📋 Requirements

- Windows 10 or later
- Python 3.8 or later (for development)
- Administrator privileges (required for changing DNS settings)

## 🚀 Installation

### For Users
1. Download the latest release from the [Releases](https://github.com/yourusername/dns-changer/releases) page
2. Run the executable file
3. The application will automatically request administrator privileges

### For Developers
```bash
# Clone the repository
git clone https://github.com/yourusername/dns-changer.git

# Navigate to the project directory
cd dns-changer

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python setup.py
```

## 💻 Usage

### Basic Usage
1. Launch the application
2. Select a network interface or check "Apply to all interfaces"
3. Enter primary and optional secondary DNS server addresses
4. Click "Set DNS" to apply the settings

### Managing DNS Configurations
1. **Save Configuration**:
   - Enter DNS server addresses
   - Click "Save DNS"
   - Provide a name for the configuration

2. **Load Configuration**:
   - Click "Load DNS"
   - Select from your saved configurations

3. **Reset to DHCP**:
   - Click "Reset to DHCP" to clear custom DNS settings

## 🛠️ Technical Details

- Built with Python and PyQt6 for a modern, responsive interface
- Uses Windows netsh commands to modify DNS settings
- Configurations are stored in a local JSON file
- Supports both IPv4 and IPv6 DNS settings

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Inspired by the need for a simple DNS management tool
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) and [Python](https://www.python.org/)

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/dns-changer](https://github.com/yourusername/dns-changer)
