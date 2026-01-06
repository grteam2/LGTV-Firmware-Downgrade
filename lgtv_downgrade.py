#!/usr/bin/env python3
"""
LG TV Firmware Downgrade Utility
Automates the firmware downgrade process for LG webOS TVs
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lgtv_downgrade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LGTVDowngrader:
    """Main class for LG TV firmware downgrade operations"""

    def __init__(self, tv_model: str, target_firmware: str):
        self.tv_model = tv_model
        self.target_firmware = target_firmware
        self.base_dir = Path(__file__).parent
        self.firmware_dir = self.base_dir / "firmware"
        self.firmware_dir.mkdir(exist_ok=True)

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")

        # Check for required commands
        import shutil
        required_commands = ['ssh', 'scp']
        missing = []

        for cmd in required_commands:
            if not shutil.which(cmd):
                missing.append(cmd)

        if missing:
            logger.error(f"Missing required commands: {', '.join(missing)}")
            logger.info("Please install OpenSSH client")
            return False

        logger.info("✓ All prerequisites met")
        return True

    def find_firmware(self) -> Optional[str]:
        """Find firmware for the specified TV model"""
        logger.info(f"Searching firmware for {self.tv_model}...")

        from firmware_finder import FirmwareFinder

        finder = FirmwareFinder(self.tv_model, self.target_firmware)
        firmware_path = finder.find_and_download()

        if firmware_path:
            logger.info(f"✓ Firmware found: {firmware_path}")
            return firmware_path
        else:
            logger.error("Firmware not found")
            return None

    def prepare_usb(self, firmware_path: str, usb_path: str) -> bool:
        """Prepare USB drive with firmware"""
        logger.info(f"Preparing USB drive at {usb_path}...")

        from usb_prep import USBPrepper

        prepper = USBPrepper(usb_path)
        success = prepper.prepare_firmware(firmware_path)

        if success:
            logger.info("✓ USB drive prepared successfully")
            return True
        else:
            logger.error("Failed to prepare USB drive")
            return False

    def connect_tv(self, tv_ip: str) -> bool:
        """Test connection to LG TV"""
        logger.info(f"Testing connection to TV at {tv_ip}...")

        from ssh_helper import SSHHelper

        ssh = SSHHelper(tv_ip)
        if ssh.test_connection():
            logger.info("✓ Connected to TV")
            return True
        else:
            logger.error("Cannot connect to TV")
            return False

    def send_downgrade_command(self, tv_ip: str) -> bool:
        """Send downgrade command via SSH"""
        logger.info("Sending downgrade command to TV...")

        from ssh_helper import SSHHelper

        ssh = SSHHelper(tv_ip)
        if ssh.send_software_update():
            logger.info("✓ Command sent successfully")
            logger.info("Please check your TV screen for the software update menu")
            return True
        else:
            logger.error("Failed to send command")
            return False

    def run_wizard(self):
        """Run interactive wizard mode"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║     LG TV Firmware Downgrade Utility - Interactive Wizard    ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  WARNING: This process carries risks. Please read the documentation
    before proceeding. You could brick your TV or void your warranty.

        """)

        # Step 1: TV Model
        print("\n📺 Step 1: Enter your TV model")
        print("   Example: LG-43UP75006LF, 43NANO75KPA, OLED65CX6LA")
        model = input("\n   TV Model: ").strip() or self.tv_model
        self.tv_model = model

        # Step 2: Target firmware
        print("\n� Step 2: Enter target firmware version")
        print("   Example: 3.21.30, 3.20.14")
        firmware = input("\n   Target Firmware: ").strip() or self.target_firmware
        self.target_firmware = firmware

        # Step 3: Choose method
        print("\n🔧 Step 3: Choose downgrade method")
        print("   1. Web Browser Method (Easiest - No Dev Mode)")
        print("   2. IPK File Method (Requires Developer Mode)")
        print("   3. SSH Command Method (Advanced)")
        print("   4. Prepare USB only")

        choice = input("\n   Choice (1-4): ").strip()

        if choice == "1":
            self.method_web_browser()
        elif choice == "2":
            self.method_ipk()
        elif choice == "3":
            self.method_ssh()
        elif choice == "4":
            self.method_usb_only()
        else:
            logger.error("Invalid choice")

    def method_web_browser(self):
        """Method 1: Web Browser Downgrade"""
        print("\n" + "="*60)
        print("METHOD 1: WebOS App Club Online Downgrade")
        print("="*60)

        firmware_path = self.find_firmware()
        if not firmware_path:
            return

        print("\n📋 Instructions:")
        print("1. Prepare your USB drive with the firmware")
        usb_path = input("\n   Enter USB drive path (e.g., /dev/sdX or E:): ").strip()
        if usb_path and self.prepare_usb(firmware_path, usb_path):
            print("\n2. On your TV:")
            print("   - Open the Web Browser")
            print("   - Go to: https://webosapp.club/downgrade/")
            print("   - Click Yes/OK when prompted")
            print("   - Select firmware from USB drive")

    def method_ipk(self):
        """Method 2: IPK File Method"""
        print("\n" + "="*60)
        print("METHOD 2: IPK File Downgrade")
        print("="*60)

        print("\n📋 Prerequisites:")
        print("✓ Developer Mode must be installed on your TV")
        print("✓ LG Developer Manager Desktop App must be installed")

        firmware_path = self.find_firmware()
        if not firmware_path:
            return

        usb_path = input("\n   Enter USB drive path: ").strip()
        if usb_path:
            self.prepare_usb(firmware_path, usb_path)

        print("\n📋 Next Steps:")
        print("1. Download: webos4x-6x.expertmode.downgrade_1.0.0_all.ipk")
        print("   From: http://45.140.167.171/ipk/")
        print("2. Install via LG Developer Manager")
        print("3. Open the app and select firmware from USB")

    def method_ssh(self):
        """Method 3: SSH Command Method"""
        print("\n" + "="*60)
        print("METHOD 3: SSH Command Downgrade")
        print("="*60)

        tv_ip = input("\n   Enter your TV IP address: ").strip()
        if not tv_ip:
            logger.error("TV IP address is required")
            return

        if not self.connect_tv(tv_ip):
            return

        firmware_path = self.find_firmware()
        if not firmware_path:
            return

        usb_path = input("\n   Enter USB drive path: ").strip()
        if usb_path:
            self.prepare_usb(firmware_path, usb_path)

        if input("\n   Send downgrade command now? (y/n): ").strip().lower() == 'y':
            self.send_downgrade_command(tv_ip)

    def method_usb_only(self):
        """Prepare USB only"""
        print("\n" + "="*60)
        print("USB PREPARATION ONLY")
        print("="*60)

        firmware_path = self.find_firmware()
        if not firmware_path:
            return

        usb_path = input("\n   Enter USB drive path: ").strip()
        if usb_path:
            self.prepare_usb(firmware_path, usb_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LG TV Firmware Downgrade Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive wizard mode
  python lgtv_downgrade.py

  # Prepare USB with firmware
  python lgtv_downgrade.py --model LG-43UP75006LF --firmware 3.21.30 --usb /dev/sdb

  # Send SSH command to TV
  python lgtv_downgrade.py --ip 192.168.1.100 --send-command

  # Find firmware only
  python lgtv_downgrade.py --model LG-43UP75006LF --firmware 3.21.30 --find-firmware
        """
    )

    parser.add_argument('--model', help='TV model number (e.g., LG-43UP75006LF)')
    parser.add_argument('--firmware', help='Target firmware version (e.g., 3.21.30)')
    parser.add_argument('--usb', help='USB drive path (e.g., /dev/sdb or E:)')
    parser.add_argument('--ip', help='TV IP address for SSH')
    parser.add_argument('--send-command', action='store_true', help='Send downgrade command via SSH')
    parser.add_argument('--find-firmware', action='store_true', help='Find firmware only')
    parser.add_argument('--wizard', action='store_true', help='Run interactive wizard (default)')

    args = parser.parse_args()

    # Default to wizard mode if no specific action requested
    if not any([args.usb, args.send_command, args.find_firmware]):
        args.wizard = True

    if args.wizard:
        downgrader = LGTVDowngrader('LG-43UP75006LF', '3.21.30')
        downgrader.run_wizard()
        return

    if not args.model or not args.firmware:
        logger.error("--model and --firmware are required")
        sys.exit(1)

    downgrader = LGTVDowngrader(args.model, args.firmware)

    if args.find_firmware:
        firmware = downgrader.find_firmware()
        if firmware:
            print(f"Firmware: {firmware}")

    if args.usb:
        if not args.find_firmware:
            logger.error("Use --find-firmware first")
            sys.exit(1)
        # We'd need the firmware path from find_firmware
        downgrader.prepare_usb("", args.usb)

    if args.send_command:
        if not args.ip:
            logger.error("--ip is required for --send-command")
            sys.exit(1)
        downgrader.send_downgrade_command(args.ip)


if __name__ == "__main__":
    main()
