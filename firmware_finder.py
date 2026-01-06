"""
Firmware Finder Module
Searches and downloads LG TV firmware from various sources
"""

import os
import re
import requests
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FirmwareFinder:
    """Find and download LG TV firmware"""

    def __init__(self, tv_model: str, target_version: str):
        self.tv_model = tv_model.upper()
        self.target_version = target_version
        self.firmware_dir = Path(__file__).parent / "firmware"
        self.firmware_dir.mkdir(exist_ok=True)

        # Known firmware sources and patterns
        self.lg_sites = {
            'korea': 'https://www.lge.co.kr/support/product-manuals',
            'uk': 'https://www.lg.com/uk/support',
            'us': 'https://www.lg.com/us/support',
        }

    def find_and_download(self) -> Optional[str]:
        """Main method to find and download firmware"""

        # First, check if we already have it downloaded
        cached = self._check_cache()
        if cached:
            logger.info(f"Using cached firmware: {cached}")
            return cached

        # Try different search strategies
        logger.info("Searching for firmware...")

        # Strategy 1: Extract model base and search
        model_base = self._extract_model_base()
        logger.info(f"Model base: {model_base}")

        # Since we can't actually scrape LG sites (they require JS),
        # we'll provide guidance to the user
        return self._provide_manual_instructions(model_base)

    def _check_cache(self) -> Optional[str]:
        """Check if firmware is already downloaded"""
        pattern = re.compile(rf'.*{self.target_version.replace(".", r"\.")}\.epk', re.IGNORECASE)

        for file in self.firmware_dir.glob("*.epk"):
            if pattern.match(file.name):
                return str(file)

        return None

    def _extract_model_base(self) -> str:
        """Extract base model number from TV model"""
        # Remove common prefixes
        model = self.tv_model.replace("LG-", "").replace("LG", "")
        # Get the alphanumeric part (usually first 10-15 chars)
        match = re.match(r'([A-Z0-9]{6,15})', model)
        return match.group(1) if match else model

    def _provide_manual_instructions(self, model_base: str) -> Optional[str]:
        """Provide manual download instructions"""

        instructions = f"""
═══════════════════════════════════════════════════════════════
                   FIRMWARE DOWNLOAD GUIDE
═══════════════════════════════════════════════════════════════

🔍 Searching for: {self.tv_model} → {self.target_version}

Since firmware downloads require authentication and JavaScript,
please download manually using one of these methods:

═══════════════════════════════════════════════════════════════

OPTION 1: Korean LG Website (Recommended)
────────────────────────────────────────────────────────────
1. Go to: https://www.lge.co.kr/support/product-manuals
2. Translate to English (right-click → Translate)
3. Search for your model: {model_base}
4. Download firmware version: {self.target_version}

OPTION 2: Your Region's LG Website
────────────────────────────────────────────────────────────
1. Go to your region's LG support site
2. Find your TV model's support page
3. Look for "Reference Models" - note compatible models
4. Download the desired firmware

OPTION 3: Telegram Channel
────────────────────────────────────────────────────────────
1. Join: https://t.me/lgwebosusb
2. Search for your TV model
3. Download the firmware file

═══════════════════════════════════════════════════════════════

After downloading, place the .epk file in:
{self.firmware_dir.absolute()}

Then run this utility again.
═══════════════════════════════════════════════════════════════
        """

        print(instructions)
        return None

    def verify_firmware(self, firmware_path: str) -> bool:
        """Verify firmware file is valid"""
        path = Path(firmware_path)

        if not path.exists():
            logger.error(f"Firmware file not found: {firmware_path}")
            return False

        if not path.suffix.lower() == '.epk':
            logger.error(f"Invalid firmware format: {path.suffix}")
            return False

        # Check file size (should be at least 100MB)
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb < 100:
            logger.warning(f"Firmware file seems small: {size_mb:.1f}MB")
            return False

        logger.info(f"Firmware verified: {path.name} ({size_mb:.1f}MB)")
        return True

    def get_compatible_models(self) -> List[str]:
        """Get list of known compatible models"""
        # This is a static list - in a real implementation,
        # you might scrape this from LG's reference database
        compat_map = {
            '43UP75006LF': ['43NANO75KPA', '43NANO77KPA', '43UP75', '43UP77'],
            '55UP75006LF': ['55NANO75KPA', '55NANO77KPA', '55UP75', '55UP77'],
            '65UP75006LF': ['65NANO75KPA', '65NANO77KPA', '65UP75', '65UP77'],
        }

        return compat_map.get(self._extract_model_base(), [])

    def search_local_network(self) -> Optional[Dict]:
        """Search for LG TVs on local network"""
        import socket
        import subprocess

        logger.info("Scanning local network for LG TVs...")

        try:
            # Try arp-scan if available
            result = subprocess.run(
                ['arp-scan', '--localnet'],
                capture_output=True,
                text=True,
                timeout=30
            )

            lg_tvs = []
            for line in result.stdout.split('\n'):
                if 'LG' in line.upper():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        lg_tvs.append({
                            'ip': parts[0],
                            'mac': parts[1] if len(parts) > 1 else 'Unknown'
                        })

            if lg_tvs:
                logger.info(f"Found {len(lg_tvs)} LG TV(s)")
                return lg_tvs[0] if lg_tvs else None

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        logger.info("No LG TVs found on local network")
        return None


class FirmwareDatabase:
    """Database of known firmware versions and their characteristics"""

    # Known rootable firmware versions
    ROOTABLE_FIRMWARE = {
        'webOS 4.x': ['4.x.x', '03.21.30', '03.20.14', '03.21.40'],
        'webOS 5.x': ['05.00.00', '05.10.00', '05.20.00'],
        'webOS 6.x': ['06.00.00', '06.10.00'],
    }

    # Patched (non-rootable) versions
    PATCHED_FIRMWARE = [
        '03.30.10',  # May 2022 - Original exploit patched
        '03.30.14',
        '03.40.xx',
    ]

    @classmethod
    def is_rootable(cls, version: str) -> bool:
        """Check if firmware version is rootable"""
        for versions in cls.ROOTABLE_FIRMWARE.values():
            if version in versions:
                return True
        return False

    @classmethod
    def is_patched(cls, version: str) -> bool:
        """Check if firmware version has exploit patched"""
        for patched in cls.PATCHED_FIRMWARE:
            if version.startswith(patched.rstrip('x')):
                return True
        return False

    @classmethod
    def recommend_firmware(cls, current_version: str) -> Optional[str]:
        """Recommended firmware to downgrade to"""
        if cls.is_rootable(current_version):
            return current_version  # Already rootable

        # Recommend last known rootable version
        return '03.21.30'  # Generally safe bet for many models
