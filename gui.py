#!/usr/bin/env python3
"""
LG TV Firmware Downgrade Utility - GUI
A graphical user interface for the LG TV firmware downgrade process
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

# Import our modules
from firmware_finder import FirmwareFinder, FirmwareDatabase
from usb_prep import USBPrepper
from ssh_helper import SSHHelper, TVDiscovery


class LGTVDowngradeGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("LG TV Firmware Downgrade Utility")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Variables
        self.tv_model = tk.StringVar(value="LG-43UP75006LF")
        self.target_firmware = tk.StringVar(value="3.21.30")
        self.firmware_path = tk.StringVar()
        self.usb_path = tk.StringVar()
        self.tv_ip = tk.StringVar()
        self.log_text = tk.StringVar()

        self.create_widgets()
        self.log("Welcome to LG TV Firmware Downgrade Utility!")

    def create_widgets(self):
        """Create all GUI widgets"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill='x')

        title_label = ttk.Label(
            title_frame,
            text="LG TV Firmware Downgrade Utility",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="⚠️  Risky process - Read documentation first!",
            font=('Helvetica', 10),
            foreground='red'
        )
        subtitle_label.pack()

        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Firmware
        self.create_firmware_tab(notebook)

        # Tab 2: USB Prep
        self.create_usb_tab(notebook)

        # Tab 3: SSH
        self.create_ssh_tab(notebook)

        # Tab 4: Wizard
        self.create_wizard_tab(notebook)

        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="5")
        log_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.log_output = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            wrap='word',
            font=('Consolas', 9)
        )
        self.log_output.pack(fill='both', expand=True)

        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', padx=10, pady=(0, 5))

        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief='sunken',
            anchor='w'
        )
        self.status_label.pack(fill='x')

    def create_firmware_tab(self, notebook):
        """Create firmware tab"""
        tab = ttk.Frame(notebook, padding="20")
        notebook.add(tab, text="📦 Firmware")

        # TV Model
        ttk.Label(tab, text="TV Model:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(tab, textvariable=self.tv_model, width=30).grid(row=0, column=1, pady=5, padx=5)

        # Target Firmware
        ttk.Label(tab, text="Target Firmware:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(tab, textvariable=self.target_firmware, width=30).grid(row=1, column=1, pady=5, padx=5)

        # Firmware Check
        ttk.Separator(tab, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=15)

        ttk.Button(
            tab,
            text="Check if Firmware is Rootable",
            command=self.check_firmware
        ).grid(row=3, column=0, columnspan=2, pady=5)

        # Result area
        result_frame = ttk.LabelFrame(tab, text="Result", padding="10")
        result_frame.grid(row=4, column=0, columnspan=3, sticky='nsew', pady=10)

        self.firmware_result = tk.Text(result_frame, height=6, wrap='word')
        self.firmware_result.pack(fill='both', expand=True)

        # Download guide
        ttk.Separator(tab, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky='ew', pady=15)

        ttk.Button(
            tab,
            text="Show Download Instructions",
            command=self.show_download_instructions
        ).grid(row=6, column=0, columnspan=2, pady=5)

    def create_usb_tab(self, notebook):
        """Create USB preparation tab"""
        tab = ttk.Frame(notebook, padding="20")
        notebook.add(tab, text="🔌 USB Prep")

        # Firmware selection
        ttk.Label(tab, text="Firmware File (.epk):", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(tab, textvariable=self.firmware_path, width=40).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(tab, text="Browse...", command=self.browse_firmware).grid(row=0, column=2, pady=5)

        # USB selection
        ttk.Label(tab, text="USB Drive:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(tab, textvariable=self.usb_path, width=40).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(tab, text="Browse...", command=self.browse_usb).grid(row=1, column=2, pady=5)

        # List USB drives
        ttk.Button(
            tab,
            text="🔍 List USB Drives",
            command=self.list_usb_drives
        ).grid(row=2, column=0, columnspan=3, pady=10)

        # Prepare button
        ttk.Separator(tab, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky='ew', pady=15)

        ttk.Button(
            tab,
            text="✓ Prepare USB Drive",
            command=self.prepare_usb,
            width=25
        ).grid(row=4, column=0, columnspan=3, pady=10)

    def create_ssh_tab(self, notebook):
        """Create SSH tab"""
        tab = ttk.Frame(notebook, padding="20")
        notebook.add(tab, text="📡 SSH")

        # TV IP
        ttk.Label(tab, text="TV IP Address:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(tab, textvariable=self.tv_ip, width=30).grid(row=0, column=1, pady=5, padx=5)

        # Buttons
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)

        ttk.Button(
            button_frame,
            text="🔍 Test Connection",
            command=self.test_connection
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="🚀 Send Software Update",
            command=self.send_software_update
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="📺 Scan Network",
            command=self.scan_network
        ).pack(side='left', padx=5)

        # Info area
        info_frame = ttk.LabelFrame(tab, text="SSH Information", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=10)

        info_text = """
SSH Port: 9922
User: prisoner
Password: (shown in Developer Mode app on TV)

Prerequisites:
✓ Developer Mode installed on TV
✓ TV and PC on same network
        """

        ttk.Label(info_frame, text=info_text, justify='left').pack(fill='both', expand=True)

    def create_wizard_tab(self, notebook):
        """Create wizard tab"""
        tab = ttk.Frame(notebook, padding="20")
        notebook.add(tab, text="🧙 Wizard")

        # Description
        desc_label = ttk.Label(
            tab,
            text="Interactive Wizard - Step by Step Guide",
            font=('Arial', 12, 'bold')
        )
        desc_label.pack(pady=10)

        # Methods
        methods_frame = ttk.LabelFrame(tab, text="Choose Method", padding="15")
        methods_frame.pack(fill='both', expand=True, pady=10)

        ttk.Button(
            methods_frame,
            text="1️⃣  Web Browser Method\n(Easiest - No Dev Mode)",
            command=lambda: self.run_wizard_method(1),
            width=40
        ).pack(pady=10)

        ttk.Button(
            methods_frame,
            text="2️⃣  IPK File Method\n(Requires Developer Mode)",
            command=lambda: self.run_wizard_method(2),
            width=40
        ).pack(pady=10)

        ttk.Button(
            methods_frame,
            text="3️⃣  SSH Command Method\n(Advanced)",
            command=lambda: self.run_wizard_method(3),
            width=40
        ).pack(pady=10)

        ttk.Button(
            methods_frame,
            text="4️⃣  Prepare USB Only",
            command=lambda: self.run_wizard_method(4),
            width=40
        ).pack(pady=10)

        # Donation
        donation_frame = ttk.LabelFrame(tab, text="💖 Support This Project", padding="10")
        donation_frame.pack(fill='x', pady=10)

        donation_text = """Donate XMR (Monero):
46rAWWQKFvJc5A8mp2EVBDBPofTw2KUzgXtp89anAJT3S39e5szHa46X2PMwawznCTjdcq34AvU1Ra25MYjjPAGNK8T5Wfc"""

        ttk.Label(donation_frame, text=donation_text, font=('Consolas', 8)).pack()

    def log(self, message):
        """Add message to log"""
        self.log_output.insert('end', f"[{self.get_timestamp()}] {message}\n")
        self.log_output.see('end')
        self.root.update()

    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update()

    # Button callbacks
    def browse_firmware(self):
        """Browse for firmware file"""
        filename = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=[("EPK Files", "*.epk"), ("All Files", "*.*")]
        )
        if filename:
            self.firmware_path.set(filename)
            self.log(f"Selected firmware: {filename}")

    def browse_usb(self):
        """Browse for USB drive"""
        if sys.platform == 'win32':
            from tkinter import simpledialog
            drive = simpledialog.askstring("USB Drive", "Enter drive letter (e.g., E:):")
            if drive:
                self.usb_path.set(drive + "\\" if not drive.endswith(':') else drive)
        else:
            dirname = filedialog.askdirectory(title="Select USB Drive")
            if dirname:
                self.usb_path.set(dirname)

    def check_firmware(self):
        """Check if firmware is rootable"""
        version = self.target_firmware.get()

        self.firmware_result.delete(1.0, 'end')

        if FirmwareDatabase.is_rootable(version):
            self.firmware_result.insert('end', f"✓ Firmware {version} is ROOTABLE\n\n")
            self.firmware_result.insert('end', "This version can be rooted using rootmy.tv\n")
        elif FirmwareDatabase.is_patched(version):
            self.firmware_result.insert('end', f"✗ Firmware {version} is PATCHED\n\n")
            self.firmware_result.insert('end', "You need to downgrade to a rootable version.\n")
            self.firmware_result.insert('end', f"Recommended: {FirmwareDatabase.recommend_firmware(version)}\n")
        else:
            self.firmware_result.insert('end', f"⚠ Unknown firmware version: {version}\n\n")
            self.firmware_result.insert('end', "Check the RootMyTV website for compatibility.\n")

        self.log(f"Checked firmware: {version}")

    def show_download_instructions(self):
        """Show firmware download instructions"""
        model = self.tv_model.get()
        version = self.target_firmware.get()

        finder = FirmwareFinder(model, version)
        finder.find_and_download()

    def list_usb_drives(self):
        """List available USB drives"""
        drives = USBPrepper.list_usb_drives()

        self.log(f"Found {len(drives)} USB drive(s)")

        if drives:
            msg = "Available USB Drives:\n\n"
            for i, drive in enumerate(drives, 1):
                msg += f"{i}. {drive.get('name', drive.get('path', 'Unknown'))}\n"
                msg += f"   Path: {drive['path']}\n"

            messagebox.showinfo("USB Drives", msg)
        else:
            messagebox.showwarning("No Drives", "No USB drives detected!\nPlug in a USB drive and try again.")

    def prepare_usb(self):
        """Prepare USB drive"""
        firmware = self.firmware_path.get()
        usb = self.usb_path.get()

        if not firmware:
            messagebox.showerror("Error", "Please select a firmware file")
            return

        if not usb:
            messagebox.showerror("Error", "Please select USB drive")
            return

        # Confirm
        if not messagebox.askyesno("Confirm", f"Prepare USB drive at {usb}?"):
            return

        self.update_status("Preparing USB drive...")

        try:
            prepper = USBPrepper(usb)
            if prepper.prepare_firmware(firmware):
                messagebox.showinfo("Success", "USB drive prepared successfully!")
                self.log("USB preparation completed")
            else:
                messagebox.showerror("Error", "Failed to prepare USB drive")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        self.update_status("Ready")

    def test_connection(self):
        """Test SSH connection to TV"""
        ip = self.tv_ip.get()

        if not ip:
            messagebox.showerror("Error", "Please enter TV IP address")
            return

        self.update_status("Testing connection...")

        ssh = SSHHelper(ip)
        if ssh.test_connection():
            messagebox.showinfo("Success", f"Connected to TV at {ip}")
            self.log(f"Connected to TV at {ip}")
        else:
            messagebox.showerror("Error", "Cannot connect to TV")
            self.log(f"Failed to connect to {ip}")

        self.update_status("Ready")

    def send_software_update(self):
        """Send software update command"""
        ip = self.tv_ip.get()

        if not ip:
            messagebox.showerror("Error", "Please enter TV IP address")
            return

        if not messagebox.askyesno("Confirm", "Send Software Update command to TV?"):
            return

        self.update_status("Sending command...")

        ssh = SSHHelper(ip)
        if ssh.send_software_update():
            messagebox.showinfo(
                "Success",
                "Command sent!\nCheck your TV for the Software Update menu."
            )
            self.log("Software Update command sent")
        else:
            messagebox.showerror("Error", "Failed to send command")
            self.log("Failed to send command")

        self.update_status("Ready")

    def scan_network(self):
        """Scan network for LG TVs"""
        self.update_status("Scanning network...")
        self.log("Scanning for LG TVs...")

        devices = TVDiscovery.discover()

        if devices:
            msg = f"Found {len(devices)} device(s):\n\n"
            for ip in devices:
                msg += f"• {ip}\n"

            messagebox.showinfo("Found Devices", msg)
            if len(devices) == 1:
                self.tv_ip.set(devices[0])
        else:
            messagebox.showinfo("Scan Complete", "No LG TVs found on network")

        self.update_status("Ready")

    def run_wizard_method(self, method):
        """Run specific wizard method"""
        if method == 1:
            messagebox.showinfo(
                "Web Browser Method",
                "1. Prepare USB with firmware\n2. Open browser on TV: https://webosapp.club/downgrade/\n3. Select firmware from USB"
            )
        elif method == 2:
            messagebox.showinfo(
                "IPK File Method",
                "1. Download downgrade IPK from http://45.140.167.171/ipk/\n2. Install via LG Developer Manager\n3. Open app and select firmware"
            )
        elif method == 3:
            messagebox.showinfo(
                "SSH Command Method",
                "1. Enter TV IP address\n2. Test connection\n3. Send Software Update command"
            )
        elif method == 4:
            messagebox.showinfo(
                "USB Preparation",
                "Select firmware file and USB drive, then click Prepare"
            )


def main():
    """Main entry point for GUI"""
    root = tk.Tk()
    app = LGTVDowngradeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
