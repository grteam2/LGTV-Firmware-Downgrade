"""
SSH Helper Module
Connects to LG TVs and sends downgrade commands
"""

import socket
import subprocess
import time
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SSHHelper:
    """Helper for SSH connections to LG TV"""

    def __init__(self, tv_ip: str, port: int = 9922):
        self.tv_ip = tv_ip
        self.port = port
        self.user = "prisoner"

    def test_connection(self) -> bool:
        """Test if TV is reachable on SSH port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.tv_ip, self.port))
            sock.close()

            if result == 0:
                logger.info(f"✓ TV is reachable at {self.tv_ip}:{self.port}")
                return True
            else:
                logger.error(f"Cannot connect to TV at {self.tv_ip}:{self.port}")
                return False

        except socket.gaierror:
            logger.error(f"Invalid IP address: {self.tv_ip}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def send_software_update(self) -> bool:
        """Send luna command to open Software Update"""
        command = (
            'luna-send-pub -d -n 1 -f '
            '"luna://com.webos.applicationManager/launch" '
            '\'{"id": "com.webos.app.softwareupdate", '
            '"params": {"mode": "user", "flagUpdate": true}}\''
        )

        return self._execute_command(command)

    def send_expert_mode(self) -> bool:
        """Send luna command to open Expert Mode"""
        command = (
            'luna-send-pub -d -n 1 -f '
            '"luna://com.webos.applicationManager/launch" '
            '\'{"id": "com.webos.app.softwareupdate", '
            '"params": {"mode": "expert", "flagUpdate": true}}\''
        )

        return self._execute_command(command)

    def get_firmware_info(self) -> Optional[str]:
        """Get current firmware version"""
        command = 'luna-send-pub -n 1 "luna://com.webos.service.tvproperty/getSystemInfo" \'{}\''

        result = self._execute_command(command, capture_output=True)
        return result if result else None

    def check_developer_mode(self) -> bool:
        """Check if Developer Mode is installed"""
        command = 'luna-send-pub -n 1 "luna://com.webos.applicationManager/listApps" \'{}\''

        result = self._execute_command(command, capture_output=True)
        if result and 'developer' in result.lower():
            return True
        return False

    def _execute_command(self, command: str, capture_output: bool = False) -> Optional[str]:
        """Execute SSH command"""

        # Build SSH command
        ssh_cmd = [
            'ssh',
            '-p', str(self.port),
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ConnectTimeout=10',
            f'{self.user}@{self.tv_ip}',
            command
        ]

        try:
            logger.info(f"Executing command via SSH...")

            if capture_output:
                result = subprocess.run(
                    ssh_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.error(f"Command failed: {result.stderr}")
                    return None
            else:
                subprocess.run(ssh_cmd, check=True, timeout=30)
                return "Command sent"

        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"SSH command failed: {e}")
            return None
        except FileNotFoundError:
            logger.error("SSH client not found. Please install OpenSSH.")
            return None


class SSHConnectionWizard:
    """Interactive wizard for SSH connection setup"""

    @staticmethod
    def run():
        """Run connection wizard"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║              SSH Connection Wizard                            ║
╚═══════════════════════════════════════════════════════════════╝

This wizard will help you connect to your LG TV.

Prerequisites:
✓ Developer Mode must be installed on your TV
✓ Your TV and PC must be on the same network
        """)

        # Step 1: Get TV IP
        print("\n📡 Step 1: Find your TV's IP address")
        print("   On your TV:")
        print("   1. Go to Settings → Network → Network Status")
        print("   2. Note the IP address (e.g., 192.168.1.100)")

        tv_ip = input("\n   Enter TV IP: ").strip()

        if not tv_ip:
            print("❌ IP address is required")
            return

        # Test connection
        print("\n🔍 Step 2: Testing connection...")
        ssh = SSHHelper(tv_ip)

        if not ssh.test_connection():
            print("\n❌ Cannot connect to TV")
            print("   Troubleshooting:")
            print("   - Verify TV is on")
            print("   - Check TV and PC are on same network")
            print("   - Make sure Developer Mode is enabled")
            return

        print("✓ Connection successful!")

        # Step 3: Choose action
        print("\n⚡ Step 3: Choose action")
        print("   1. Send Software Update command")
        print("   2. Send Expert Mode command")
        print("   3. Get firmware info")
        print("   4. Check Developer Mode")

        choice = input("\n   Choice (1-4): ").strip()

        if choice == "1":
            if ssh.send_software_update():
                print("\n✓ Software Update command sent!")
                print("   Check your TV for the Software Update menu")
        elif choice == "2":
            if ssh.send_expert_mode():
                print("\n✓ Expert Mode command sent!")
                print("   Check your TV for the Software Update menu")
        elif choice == "3":
            info = ssh.get_firmware_info()
            if info:
                print(f"\n✓ Firmware info:\n{info}")
        elif choice == "4":
            if ssh.check_developer_mode():
                print("\n✓ Developer Mode is installed")
            else:
                print("\n❌ Developer Mode not found")

    @staticmethod
    def scan_network():
        """Scan local network for LG TVs"""
        import ipaddress

        print("\n🔍 Scanning local network for LG TVs...")

        # Get local network range
        try:
            # Try to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)

            print(f"   Scanning network: {network}")

            found = []
            # Scan common IPs (limit to save time)
            for i in range(1, 255):
                ip = str(network.network_address + i)
                if SSHHelper(ip).test_connection():
                    found.append(ip)

            if found:
                print(f"\n✓ Found {len(found)} device(s):")
                for ip in found:
                    print(f"   - {ip}")
                return found
            else:
                print("\n❌ No LG TVs found")
                return []

        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []


class TVDiscovery:
    """Discover LG TVs on the local network"""

    @staticmethod
    def discover() -> list:
        """Discover LG TVs using various methods"""
        devices = []

        # Method 1: Check common mDNS/Bonjour services
        devices.extend(TVDiscovery._check_mdns())

        # Method 2: Scan common LG TV ports
        devices.extend(TVDiscovery._scan_ports())

        # Method 3: UPnP discovery
        devices.extend(TVDiscovery._upnp_discover())

        return list(set(devices))  # Remove duplicates

    @staticmethod
    def _check_mdns() -> list:
        """Check for LG TVs using mDNS/Bonjour"""
        devices = []

        try:
            # Try to resolve LG TV hostname
            # LG TVs often use hostname like LgWebOS_TV_*
            import subprocess

            result = subprocess.run(
                ['avahi-browse', '-_r', '-t', '_workstation._tcp'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if 'LG' in line.upper() or 'WEBOS' in line.upper():
                    # Extract IP from line
                    parts = line.split(';')
                    if len(parts) > 2:
                        devices.append(parts[2])

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return devices

    @staticmethod
    def _scan_ports() -> list:
        """Scan for LG TV SSH port (9922)"""
        devices = []

        # Get local network
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Scan common range (first 100 IPs)
            prefix = '.'.join(local_ip.split('.')[:3])
            for i in range(1, 100):
                ip = f"{prefix}.{i}"
                if SSHHelper(ip).test_connection():
                    devices.append(ip)

        except Exception:
            pass

        return devices

    @staticmethod
    def _upnp_discover() -> list:
        """Discover devices using UPnP"""
        devices = []

        try:
            import subprocess

            result = subprocess.run(
                ['upnpc', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.split('\n'):
                if 'LG' in line.upper():
                    # Extract IP if present
                    import re
                    ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                    if ip_match:
                        devices.append(ip_match.group(0))

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return devices


# Donation reminder
XMR_DONATION = """
═══════════════════════════════════════════════════════════════
                       SUPPORT THIS PROJECT
═══════════════════════════════════════════════════════════════

If this utility helped you, consider donating:

💖 Donate XMR (Monero):
   46rAWWQKFvJc5A8mp2EVBDBPofTw2KUzgXtp89anAJT3S39e5szHa46X2PMwawznCTjdcq34AvU1Ra25MYjjPAGNK8T5Wfc

═══════════════════════════════════════════════════════════════
"""


if __name__ == "__main__":
    SSHConnectionWizard.run()
    print(XMR_DONATION)
