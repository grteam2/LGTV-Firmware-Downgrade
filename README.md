# LGTV-Firmware-Downgrade

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/github/license/grteam2/LGTV-Firmware-Downgrade)](https://github.com/grteam2/LGTV-Firmware-Downgrade/blob/main/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintenance-Passive%20use-blue.svg)](https://github.com/grteam2/LGTV-Firmware-Downgrade)

> **⚠️ WARNING**: Downgrading firmware is risky and could brick your TV. Proceed at your own risk. This may void your warranty.

A comprehensive guide to downgrade LG TV Software and webOS firmware to enable root/jailbreak on webOS versions 4-6.

**Last Updated**: July 25, 2022

---

## Table of Contents

- [Verified Compatibility](#verified-compatibility)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Getting Previous Firmware](#getting-previous-firmware)
- [USB Drive Setup](#usb-drive-setup)
- [Developer Mode Setup](#developer-mode-setup)
- [Downgrade Methods](#downgrade-methods)
  - [Method 1: Web Browser](#method-1---webos-app-club-online-downgrade)
  - [Method 2: IPK File](#method-2---install-a-downgrade-ipk-file)
  - [Method 3: CLI Command](#method-3---send-a-command-via-the-webos-tv-cli)
- [Pre-Root Steps](#final-steps-before-root)
- [Rooting Process](#its-rooting-time)
- [FAQ](#faq)
- [Background](#background)
- [References](#special-thanks-and-references)
- [Support](#support)

---

## Verified Compatibility

| TV Model | Original Version | Downgraded To | Status |
|----------|------------------|---------------|--------|
| LG 43UP75006LF | 3.30.10 | 3.21.30 | ✅ Tested |

*Should work on other LG TV models with the relevant firmware.*

---

## Prerequisites

### Required Items

1. **LG TV** with Developer Mode App installed and activated
2. **LG Developer Account** - [Sign up here](https://webostv.developer.lge.com/develop/app-test/using-devmode-app/)
3. **USB Thumb Drive** (FAT32 or NTFS formatted)
4. **Previous firmware EPK file** - See [Getting Previous Firmware](#getting-previous-firmware)
5. **Homebrew Channel** (Optional)
6. **LG webOS CLI Install Package** (for Methods 2 & 3)
7. **LG Developer Manager Desktop App** - [Download](https://github.com/webosbrew/dev-manager-desktop)

### Required Downloads

| File | Purpose | Link |
|------|---------|------|
| Downgrade Launch App | Method 2 | [XDA Developers](https://forum.xda-developers.com/attachments/downgrade-launch-app_1-0-0_all-rar.5584169/) |
| Expert Mode Downgrade | Method 2 | [Download IPK](http://45.140.167.171/ipk/webos4x-6x.expertmode.downgrade_1.0.0_all.ipk) |

> ⚠️ **Security Note**: Only download IPK files from trusted sources. The IP above is from the community but use at your own risk.

---

## Quick Start

1. Get your firmware file → [Download Guide](#getting-previous-firmware)
2. Prepare USB drive → [Setup Guide](#usb-drive-setup)
3. Choose a downgrade method → [Methods](#downgrade-methods)
4. Root your TV → [Root Guide](#its-rooting-time)

---

## 🛠️ Automated Utilities

For easier deployment, use the Python automation utilities included in this repository:

### Installation

```bash
# Clone the repository
git clone https://github.com/grteam2/LGTV-Firmware-Downgrade.git
cd LGTV-Firmware-Downgrade

# Install Python dependencies (optional - only requests is required)
pip install -r requirements.txt
```

### Usage

#### Option 1: Interactive GUI (Recommended)

```bash
python gui.py
```

Features:
- 🖥️ Easy-to-use graphical interface
- 📦 Firmware finder and downloader
- 🔌 USB drive preparation
- 📡 SSH connection testing
- 🧙 Step-by-step wizard

#### Option 2: Command Line

```bash
# Interactive wizard mode
python lgtv_downgrade.py

# Prepare USB with firmware
python lgtv_downgrade.py --model LG-43UP75006LF --firmware 3.21.30 --usb /dev/sdb

# Send SSH command to TV
python lgtv_downgrade.py --ip 192.168.1.100 --send-command

# Check if firmware is rootable
python lgtv_downgrade.py --model LG-43UP75006LF --firmware 3.21.30 --find-firmware
```

#### Option 3: Individual Modules

```bash
# USB preparation only
python usb_prep.py

# SSH helper only
python ssh_helper.py

# Firmware finder
python firmware_finder.py
```

### Utility Features

| Feature | Description |
|---------|-------------|
| **Firmware Finder** | Search and find firmware for your TV model |
| **USB Prepper** | Automatically prepare USB drive with correct structure |
| **SSH Helper** | Send downgrade commands to your TV via SSH |
| **Network Scanner** | Discover LG TVs on your local network |
| **Firmware Checker** | Verify if a firmware version is rootable |
| **GUI Wizard** | Step-by-step guided process |

---

## Getting Previous Firmware

### ⚠️ IMPORTANT DISCLAIMER

Make sure you get the **right firmware** for your TV. The TV will NOT verify compatibility during installation. Installing incorrect firmware could brick your device.

### Option 1: Korean LG Website

1. Go to your region's LG support page (e.g., [UK LG Site](https://www.lg.com/uk/support/product/lg-43up75006lf.aekd))
2. Scroll down and click the **Reference** link under Software download
3. Note all compatible model numbers
4. Go to [Korean LG Driver Support](https://www.lge.co.kr/support/product-manuals?title=driver&mktModel) (translate to English)
5. Search for your TV model from the reference list
6. Download the desired firmware version

**Example**: For LG-43UP75006LF, look for `43NANO75KPA` with firmware like `UP75_82_83_NANO75_77_83KPA_LM21A_Ver.03.21.30`

### Option 2: Russian Telegram Channel

Visit the [LG webOS USB Telegram channel](https://t.me/lgwebosusb) to find firmware for your specific model.

> 💡 **Tip**: Download both your target firmware AND the latest firmware (in case you need to update back).

---

## USB Drive Setup

1. **Format** your USB drive to **FAT32** or **NTFS**
   > This will erase all data on the drive - backup first!

2. **Create folder** named `LG_DTV` in the root directory

3. **Extract** the firmware ZIP file to find the `.epk` file

4. **Copy** the `.epk` file into the `LG_DTV` folder

5. **Eject** and plug into your TV

---

## Developer Mode Setup

Required for **Method 2** and **Method 3**.

Follow the official [LG webOS Developer Mode guide](https://webostv.developer.lge.com/develop/app-test/using-devmode-app/) to:
- Install Developer Mode on your TV
- Set up the connection between your PC and TV
- Enable command line access

---

## Downgrade Methods

### ⚠️ FINAL DISCLAIMER

All methods are risky and could result in a bricked TV. This is not officially supported by LG and may void your warranty.

---

### Method 1 - WebOS App Club Online Downgrade

**Easiest method - No Developer Mode required**

1. Open your TV's **Web Browser**
2. Go to: https://webosapp.club/downgrade/
3. Click **Yes/OK** when prompted to share information
4. Select your firmware file from the USB drive
5. Wait up to 10 minutes for installation
6. Reboot when prompted

**Troubleshooting**: If you get a black screen or unexpected reboot, try Method 2.

---

### Method 2 - Install a Downgrade IPK File

1. Download the required IPK files (see [Prerequisites](#prerequisites))
2. **Install** `webos4x-6x.expertmode.downgrade_1.0.0_all.ipk` using Dev Manager
3. **Open** the newly installed app
4. **Confirm** Expert Mode access when prompted
5. **Select** your firmware file from USB drive
6. **Wait** up to 10 minutes and reboot

**If Method 2a fails:**

1. **Restart** your TV
2. **Uninstall** the expert mode downgrade app
3. **Install** `downgrade.launch.app_1.0.0_all.ipk`
4. **Open** the app and confirm Software Update
5. **Select** your firmware file and proceed

---

### Method 3 - Send Command via webOS TV CLI

**For advanced users only**

1. **Connect** to your TV via SSH:
   ```bash
   ssh -p 9922 -i ~/.ssh/tv_webos prisoner@<YOUR_TV_IP>
   ```
   Password is the passphrase shown in Developer Mode app

2. **Send** the luna command:
   ```bash
   luna-send-pub -d -n 1 -f "luna://com.webos.applicationManager/launch" '{"id": "com.webos.app.softwareupdate", "params": {"mode": "user", "flagUpdate": true}}'
   ```

3. **Confirm** Expert Mode access when prompted
4. **Select** your firmware file from USB drive

---

## Final Steps Before Root

1. ✅ **Uninstall** Developer Mode app
   - Long press the icon → Press up → Delete

2. ✅ **Verify** firmware version
   - Go to: Settings → System → System Update

3. ✅ **Disable** Auto Update
   - Turn OFF "Auto Update" in System Update settings

---

## It's Rooting Time

1. **Open** your TV's web browser and go to: https://rootmy.tv/
2. **Slide to root** (or press button/click 5 on regular remote)
3. **First reboot**: Open Home Screen when TV restarts
4. **Second reboot**: Homebrew Channel will appear
5. **Verify root status**:
   - Open Homebrew Channel → Settings (cog icon)
   - Check "Root Status: OK"

**Default SSH Credentials:**
- User: `root`
- Password: `alpine`

> 🔐 **Security**: Change your SSH password and import your SSH keys. See [RootMyTV Post Installation](https://github.com/RootMyTV/RootMyTV.github.io) for details.

---

## FAQ

### Do I need to downgrade to root?

If you're on Software Version **3.30+** (May 2022 or later), the original exploit has been patched. Developer Mode provides limited functionality but full root requires downgrade.

### Can I brick my TV?

Yes, both downgrade and root processes carry risk. However, RootMyTV includes a [Failsafe Mode](https://github.com/RootMyTV/RootMyTV.github.io) for protection.

### What if the downgrade doesn't work?

It may take several attempts. If unsuccessful, your TV may have these methods fully patched.

### How do I remove root?

A full factory reset should remove everything. See [RootMyTV FAQ](https://github.com/RootMyTV/RootMyTV.github.io) for details.

---

## Background

This guide was created after purchasing an **LG 43UP75006LF** (UK 2021 model) which had already been updated to firmware **3.30.14**, patching the root exploit.

After researching Russian forums and AVSForums, I successfully downgraded to **3.21.30**, then to **3.20.14**, enabling root access via rootmy.tv.

The downgrade process typically requires several attempts before successfully accessing the Software Update screen.

---

## Special Thanks and References

| Resource | Link |
|----------|------|
| AVS Forum Thread | [Link](https://www.avsforum.com/threads/guide-lg-webos-tvs-firmware-downgrade-advanced-users-only.3217168/) |
| Russian WebOS Forums | [Link](http://webos-forums.ru/topic3157.html) |
| XDA Developers Guide | [Link](https://forum.xda-developers.com/t/how-downgrade-software-oled65cx6la.4376371/) |
| RootMyTV | [rootmy.tv](https://rootmy.tv/) |
| Homebrew Channel | [GitHub](https://github.com/webosbrew/webos-homebrew-channel) |

### Notable Developers from Russian WebOS Forums

- **Jack Sparrow**: [Profile](http://webos-forums.ru/jacksparrow-u8940.html)
- **Mixmar**: [Profile](http://webos-forums.ru/mixmar-u2483.html)

---

## Support

- 📖 **Documentation**: [RootMyTV GitHub](https://github.com/RootMyTV/RootMyTV.github.io)
- 💬 **Community**: [Russian WebOS Forums](http://webos-forums.ru/)
- 📺 **Firmware**: [LG webOS USB Telegram](https://t.me/lgwebosusb)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Original author: [ReproDev](https://github.com/reprodev)

---

## Donate

If this guide helped you, consider supporting the project:

### Support Original Author
[![Buy Me A Coffee](https://cdn.ko-fi.com/cdn/kofi2.png?v=3)](https://ko-fi.com/reprodev)

### Donate XMR (Monero)
```
46rAWWQKFvJc5A8mp2EVBDBPofTw2KUzgXtp89anAJT3S39e5szHa46X2PMwawznCTjdcq34AvU1Ra25MYjjPAGNK8T5Wfc
```

**Made with ❤️ for the webOS community**
