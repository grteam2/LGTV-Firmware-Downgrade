"""
USB Preparation Module
Prepares USB drives with firmware for LG TV downgrade
"""

import os
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class USBPrepper:
    """Prepare USB drives for LG TV firmware downgrade"""

    def __init__(self, usb_path: str):
        self.usb_path = usb_path
        self.system = platform.system()

    def prepare_firmware(self, firmware_path: str) -> bool:
        """Prepare USB drive with firmware file"""

        # Validate firmware
        if not Path(firmware_path).exists():
            logger.error(f"Firmware not found: {firmware_path}")
            return False

        # Check if path exists
        if not os.path.exists(self.usb_path):
            logger.error(f"USB path not found: {self.usb_path}")
            return False

        # Create LG_DTV folder
        lg_dtv_path = os.path.join(self.usb_path, "LG_DTV")

        try:
            os.makedirs(lg_dtv_path, exist_ok=True)
            logger.info(f"Created LG_DTV folder: {lg_dtv_path}")
        except Exception as e:
            logger.error(f"Failed to create LG_DTV folder: {e}")
            return False

        # Copy firmware
        firmware_name = Path(firmware_path).name
        dest_path = os.path.join(lg_dtv_path, firmware_name)

        try:
            shutil.copy2(firmware_path, dest_path)
            size_mb = Path(firmware_path).stat().st_size / (1024 * 1024)
            logger.info(f"Copied firmware ({size_mb:.1f}MB): {dest_path}")
        except Exception as e:
            logger.error(f"Failed to copy firmware: {e}")
            return False

        # Verify
        if not os.path.exists(dest_path):
            logger.error("Verification failed - file not copied")
            return False

        logger.info("✓ USB drive prepared successfully")
        self._print_summary(dest_path)
        return True

    def _print_summary(self, firmware_path: str):
        """Print preparation summary"""
        size_mb = Path(firmware_path).stat().st_size / (1024 * 1024)

        print(f"""
═══════════════════════════════════════════════════════════════
                    USB PREPARATION COMPLETE
═══════════════════════════════════════════════════════════════

📁 USB Path:     {self.usb_path}
📦 Firmware:     {Path(firmware_path).name}
📏 Size:         {size_mb:.1f} MB
📂 Location:     LG_DTV/{Path(firmware_path).name}

═══════════════════════════════════════════════════════════════

✓ Your USB drive is ready!

Next steps:
1. Safely eject the USB drive
2. Plug it into your LG TV
3. Follow your chosen downgrade method

═══════════════════════════════════════════════════════════════
        """)

    @staticmethod
    def list_usb_drives() -> List[dict]:
        """List available USB drives on the system"""
        drives = []

        if platform.system() == "Windows":
            drives = USBPrepper._list_windows_drives()
        elif platform.system() == "Linux":
            drives = USBPrepper._list_linux_drives()
        elif platform.system() == "Darwin":
            drives = USBPrepper._list_macos_drives()

        return drives

    @staticmethod
    def _list_windows_drives() -> List[dict]:
        """List USB drives on Windows"""
        import win32file
        import win32api

        drives = []
        for drive in win32file.GetLogicalDriveStrings().split('\x00'):
            if drive:
                drive_type = win32file.GetDriveType(drive)
                if drive_type == win32file.DRIVE_REMOVABLE:
                    try:
                        free = win32file.GetDiskFreeSpaceEx(drive)
                        drives.append({
                            'path': drive,
                            'name': win32api.GetVolumeInformation(drive + '\\')[0],
                            'free_gb': free[0] // (1024**3),
                            'type': 'Removable'
                        })
                    except:
                        drives.append({'path': drive, 'type': 'Removable'})
        return drives

    @staticmethod
    def _list_linux_drives() -> List[dict]:
        """List USB drives on Linux"""
        drives = []

        try:
            # Use lsblk to list drives
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT', '-J'],
                capture_output=True,
                text=True
            )

            import json
            data = json.loads(result.stdout)

            for device in data.get('blockdevices', []):
                if device.get('type') == 'disk' and device.get('mountpoint'):
                    drives.append({
                        'path': device['mountpoint'],
                        'name': device['name'],
                        'size': device.get('size', 'Unknown'),
                        'type': 'USB'
                    })

        except Exception as e:
            logger.debug(f"Could not list drives: {e}")

        # Fallback: check common mount points
        common_mounts = ['/media/', '/mnt/', '/run/media/']
        for mount in common_mounts:
            if os.path.exists(mount):
                for root, dirs, _ in os.walk(mount):
                    for d in dirs:
                        full_path = os.path.join(root, d)
                        if os.path.ismount(full_path):
                            drives.append({'path': full_path, 'type': 'USB'})
                    break

        return drives

    @staticmethod
    def _list_macos_drives() -> List[dict]:
        """List USB drives on macOS"""
        drives = []

        try:
            result = subprocess.run(
                ['diskutil', 'list', '-plist', 'external'],
                capture_output=True,
                text=True
            )

            # Parse output for /Volumes paths
            volumes_path = Path('/Volumes')
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.is_dir() and not volume.name.startswith('.'):
                        drives.append({
                            'path': str(volume),
                            'name': volume.name,
                            'type': 'External'
                        })

        except Exception as e:
            logger.debug(f"Could not list drives: {e}")

        return drives

    @staticmethod
    def format_drive(usb_path: str, fs_type: str = 'FAT32') -> bool:
        """
        Format a USB drive

        WARNING: This will erase all data on the drive!

        Args:
            usb_path: Path to the USB drive
            fs_type: Filesystem type (FAT32 or NTFS)

        Returns:
            bool: True if successful
        """
        logger.warning(f"⚠️  FORMATTING WILL ERASE ALL DATA ON {usb_path}")
        confirm = input("Type 'YES' to confirm: ")

        if confirm != 'YES':
            logger.info("Format cancelled")
            return False

        logger.info(f"Formatting {usb_path} as {fs_type}...")

        if platform.system() == "Windows":
            return USBPrepper._format_windows(usb_path, fs_type)
        elif platform.system() == "Linux":
            return USBPrepper._format_linux(usb_path, fs_type)
        elif platform.system() == "Darwin":
            return USBPrepper._format_macos(usb_path, fs_type)

        logger.error("Unsupported platform")
        return False

    @staticmethod
    def _format_windows(drive: str, fs_type: str) -> bool:
        """Format drive on Windows"""
        try:
            # Remove trailing slash
            drive = drive.rstrip('\\')
            subprocess.run(
                ['format', drive, '/FS:' + fs_type, '/Q', '/Y'],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Format failed: {e}")
            return False

    @staticmethod
    def _format_linux(device: str, fs_type: str) -> bool:
        """Format drive on Linux"""
        try:
            # Unmount first
            subprocess.run(['umount', device], stderr=subprocess.DEVNULL)

            # Format
            fstype = 'vfat' if fs_type == 'FAT32' else 'ntfs'
            subprocess.run(
                ['mkfs.' + fstype, device],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Format failed: {e}")
            return False

    @staticmethod
    def _format_macos(device: str, fs_type: str) -> bool:
        """Format drive on macOS"""
        try:
            # Get disk identifier
            subprocess.run(
                ['diskutil', 'eraseDisk', fs_type, 'LGTVDOWN', device],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Format failed: {e}")
            return False


def interactive_usb_prep():
    """Interactive USB preparation wizard"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              USB Drive Preparation Wizard                     ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # List available drives
    drives = USBPrepper.list_usb_drives()

    if not drives:
        print("⚠️  No USB drives detected!")
        print("   Please plug in a USB drive and try again.")
        return

    print("📱 Detected USB Drives:")
    for i, drive in enumerate(drives, 1):
        print(f"   {i}. {drive.get('name', drive.get('path', 'Unknown'))}")
        print(f"      Path: {drive['path']}")
        print(f"      Type: {drive.get('type', 'Unknown')}")

    selection = input("\n   Select drive (number): ").strip()

    try:
        idx = int(selection) - 1
        if 0 <= idx < len(drives):
            selected = drives[idx]
            print(f"\n✓ Selected: {selected['path']}")

            firmware = input("   Enter path to firmware (.epk file): ").strip()
            if firmware:
                prepper = USBPrepper(selected['path'])
                prepper.prepare_firmware(firmware)
    except (ValueError, IndexError):
        print("Invalid selection")


if __name__ == "__main__":
    interactive_usb_prep()
