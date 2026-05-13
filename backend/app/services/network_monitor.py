"""
Real-time Network Monitoring Service
Uses packet capture to monitor device connections and network traffic
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging
import subprocess
import platform
import re

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Real-time network monitoring using packet capture"""

    def __init__(self, interface: str = None):
        self.interface = interface or self._detect_interface()
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        self.device_cache = {}  # MAC -> device info cache

    def _detect_interface(self) -> str:
        """
        Auto-detect the primary network interface
        """
        try:
            system = platform.system()

            if system == "Linux":
                # Get default interface
                result = subprocess.run(['ip', 'route', 'show', 'default'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    match = re.search(r'dev\s+(\w+)', result.stdout)
                    if match:
                        return match.group(1)

            elif system == "Darwin":  # macOS
                result = subprocess.run(['netstat', '-rn'],
                                      capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'default' in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            return parts[5]  # interface name

            elif system == "Windows":
                result = subprocess.run(['netsh', 'interface', 'show', 'interface'],
                                      capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Connected' in line:
                        parts = line.split()
                        return parts[3] if len(parts) > 3 else 'Ethernet'

            # Fallback
            return "eth0" if system == "Linux" else "en0"

        except Exception as e:
            logger.error(f"Could not detect network interface: {str(e)}")
            return "eth0"

    def add_callback(self, callback: Callable):
        """
        Add callback function for device detection events
        """
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """
        Remove callback function
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, event_type: str, data: Dict):
        """
        Notify all registered callbacks
        """
        for callback in self.callbacks:
            try:
                asyncio.run(callback(event_type, data))
            except Exception as e:
                logger.error(f"Callback error: {str(e)}")

    async def start_monitoring(self) -> bool:
        """
        Start real-time network monitoring
        """
        if self.is_monitoring:
            return False

        try:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

            logger.info(f"Started network monitoring on interface {self.interface}")
            return True

        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            self.is_monitoring = False
            return False

    def stop_monitoring(self):
        """
        Stop network monitoring
        """
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped network monitoring")

    def _monitor_loop(self):
        """
        Main monitoring loop - runs in separate thread
        """
        while self.is_monitoring:
            try:
                # ARP scan for devices
                devices = self._arp_scan()
                self._process_devices(devices)

                # DHCP monitoring
                dhcp_devices = self._monitor_dhcp()
                if dhcp_devices:
                    self._process_dhcp_devices(dhcp_devices)

                # Sleep before next scan
                time.sleep(30)  # Scan every 30 seconds

            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(5)  # Wait before retrying

    def _arp_scan(self) -> List[Dict]:
        """
        Perform ARP scan to discover devices on network
        """
        try:
            system = platform.system()

            if system == "Linux":
                # Use arping or arp-scan if available
                try:
                    result = subprocess.run(['arp-scan', '--localnet', '--quiet'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return self._parse_arp_scan_output(result.stdout)
                except FileNotFoundError:
                    pass

                # Fallback to arp command
                result = subprocess.run(['arp', '-n'], capture_output=True, text=True)
                if result.returncode == 0:
                    return self._parse_arp_output(result.stdout)

            elif system == "Darwin":  # macOS
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                if result.returncode == 0:
                    return self._parse_arp_output(result.stdout)

            elif system == "Windows":
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
                if result.returncode == 0:
                    return self._parse_windows_arp_output(result.stdout)

            return []

        except Exception as e:
            logger.error(f"ARP scan failed: {str(e)}")
            return []

    def _parse_arp_scan_output(self, output: str) -> List[Dict]:
        """Parse arp-scan output"""
        devices = []
        lines = output.strip().split('\n')

        for line in lines:
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    ip = parts[0].strip()
                    mac = parts[1].strip()
                    hostname = parts[2].strip() if len(parts) > 2 else ""

                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': hostname,
                        'method': 'arp_scan',
                        'last_seen': datetime.utcnow()
                    })

        return devices

    def _parse_arp_output(self, output: str) -> List[Dict]:
        """Parse standard arp command output"""
        devices = []
        lines = output.strip().split('\n')

        for line in lines:
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[2] if platform.system() == "Darwin" else parts[2]

                # Skip incomplete entries
                if mac != '(incomplete)' and mac != '<incomplete>':
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': '',
                        'method': 'arp',
                        'last_seen': datetime.utcnow()
                    })

        return devices

    def _parse_windows_arp_output(self, output: str) -> List[Dict]:
        """Parse Windows arp command output"""
        devices = []
        lines = output.strip().split('\n')

        for line in lines:
            if 'dynamic' in line.lower():
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]

                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': '',
                        'method': 'arp_windows',
                        'last_seen': datetime.utcnow()
                    })

        return devices

    def _monitor_dhcp(self) -> List[Dict]:
        """
        Monitor DHCP leases for new devices
        """
        try:
            system = platform.system()
            dhcp_devices = []

            if system == "Linux":
                # Check common DHCP lease files
                lease_files = [
                    '/var/lib/dhcp/dhclient.leases',
                    '/var/lib/dhcpcd/dhcpcd.leases',
                    '/var/lib/NetworkManager/dhclient-*.leases'
                ]

                for lease_file in lease_files:
                    try:
                        with open(lease_file, 'r') as f:
                            content = f.read()
                            # Parse DHCP leases (simplified)
                            # This is a basic implementation
                            pass
                    except FileNotFoundError:
                        continue

            # For now, return empty list - DHCP monitoring needs more complex implementation
            return dhcp_devices

        except Exception as e:
            logger.error(f"DHCP monitoring failed: {str(e)}")
            return []

    def _process_devices(self, devices: List[Dict]):
        """
        Process discovered devices and notify callbacks
        """
        for device in devices:
            mac = device['mac'].upper()
            ip = device['ip']

            # Check if this is a new or updated device
            if mac not in self.device_cache:
                # New device detected
                self.device_cache[mac] = device
                self._notify_callbacks('device_connected', device)
                logger.info(f"New device detected: {mac} ({ip})")

            elif self.device_cache[mac]['ip'] != ip:
                # IP address changed
                old_ip = self.device_cache[mac]['ip']
                self.device_cache[mac] = device
                self._notify_callbacks('device_ip_changed', {
                    'mac': mac,
                    'old_ip': old_ip,
                    'new_ip': ip,
                    'device': device
                })
                logger.info(f"Device IP changed: {mac} ({old_ip} -> {ip})")

            # Update last seen
            self.device_cache[mac]['last_seen'] = device['last_seen']

    def _process_dhcp_devices(self, dhcp_devices: List[Dict]):
        """
        Process DHCP-discovered devices
        """
        for device in dhcp_devices:
            self._notify_callbacks('dhcp_device', device)

    def get_connected_devices(self) -> List[Dict]:
        """
        Get list of currently connected devices
        """
        return list(self.device_cache.values())

    def get_device_info(self, mac: str) -> Optional[Dict]:
        """
        Get information about a specific device
        """
        return self.device_cache.get(mac.upper())
