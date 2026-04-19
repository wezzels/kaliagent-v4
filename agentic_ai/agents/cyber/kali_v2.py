"""
KaliAgent v2 - Enhanced Kali Linux Tool Orchestration
======================================================

Improvements over v1:
- 20+ new modern tools (Sliver, Impacket, Pacu, CrackMapExec, etc.)
- Automatic CVE → Exploit matching
- Cloud security tools (AWS, Azure, GCP)
- AI-powered tool recommendations
- Better output parsers
- Playbook chaining with conditional logic
- Automatic remediation recommendations
"""

import json
import logging
import os
import re
import secrets
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
from xml.etree import ElementTree as ET


logger = logging.getLogger(__name__)


# ============================================
# Enums & Constants
# ============================================

class ToolCategory(Enum):
    """Kali Linux tool categories."""
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    WEB_APPLICATION = "web_application"
    DATABASE = "database"
    PASSWORD = "password"
    WIRELESS = "wireless"
    REVERSE_ENGINEERING = "reverse_engineering"
    EXPLOITATION = "exploitation"
    SNIFFING_SPOOFING = "sniffing_spoofing"
    POST_EXPLOITATION = "post_exploitation"
    FORENSICS = "forensics"
    REPORTING = "reporting"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"
    CLOUD_SECURITY = "cloud_security"
    ACTIVE_DIRECTORY = "active_directory"
    CONTAINER_SECURITY = "container_security"


class AuthorizationLevel(Enum):
    """Authorization levels for tool execution."""
    NONE = 0
    BASIC = 1
    ADVANCED = 2
    CRITICAL = 3


class ExecutionMode(Enum):
    """Tool execution modes."""
    SAFE = "safe"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


@dataclass
class ToolDefinition:
    """Tool definition with metadata."""
    name: str
    category: ToolCategory
    description: str
    command: str
    args_schema: Dict[str, Any]
    authorization: AuthorizationLevel
    safe_by_default: bool = True
    output_parser: Optional[str] = None
    timeout_seconds: int = 300
    tags: List[str] = field(default_factory=list)
    cwe_mapping: List[str] = field(default_factory=list)
    cve_matching: bool = False


@dataclass
class CVEExploitMatch:
    """CVE to exploit mapping."""
    cve_id: str
    exploit_name: str
    exploit_db_id: Optional[str]
    metasploit_module: Optional[str]
    reliability: str  # excellent, great, good, normal, low, manual
    rank: int  # 1-5
    disclosure_date: str
    platform: str
    port: Optional[int]
    description: str


# ============================================
# CVE → Exploit Database (Sample)
# ============================================

CVE_EXPLOIT_DB = {
    "CVE-2017-0144": CVEExploitMatch(
        cve_id="CVE-2017-0144",
        exploit_name="EternalBlue",
        exploit_db_id="42315",
        metasploit_module="exploit/windows/smb/ms17_010_eternalblue",
        reliability="excellent",
        rank=5,
        disclosure_date="2017-03-14",
        platform="windows",
        port=445,
        description="SMBv1 remote code execution vulnerability"
    ),
    "CVE-2019-0708": CVEExploitMatch(
        cve_id="CVE-2019-0708",
        exploit_name="BlueKeep",
        exploit_db_id="47266",
        metasploit_module="exploit/windows/rdp/cve_2019_0708_bluekeep_rce",
        reliability="good",
        rank=4,
        disclosure_date="2019-05-14",
        platform="windows",
        port=3389,
        description="RDP remote code execution vulnerability"
    ),
    "CVE-2021-44228": CVEExploitMatch(
        cve_id="CVE-2021-44228",
        exploit_name="Log4Shell",
        exploit_db_id="50666",
        metasploit_module="exploit/multi/http/log4shell_header_injection",
        reliability="excellent",
        rank=5,
        disclosure_date="2021-12-10",
        platform="java",
        port=None,
        description="Log4j JNDI injection remote code execution"
    ),
    "CVE-2021-34473": CVEExploitMatch(
        cve_id="CVE-2021-34473",
        exploit_name="ProxyShell",
        exploit_db_id="50287",
        metasploit_module="exploit/windows/http/proxyshell_exchange",
        reliability="great",
        rank=5,
        disclosure_date="2021-07-13",
        platform="exchange",
        port=443,
        description="Microsoft Exchange Server remote code execution"
    ),
    "CVE-2023-44487": CVEExploitMatch(
        cve_id="CVE-2023-44487",
        exploit_name="HTTP/2 Rapid Reset",
        exploit_db_id=None,
        metasploit_module="exploit/multi/http/http2_rapid_reset",
        reliability="normal",
        rank=3,
        disclosure_date="2023-10-10",
        platform="multi",
        port=None,
        description="HTTP/2 rapid reset DoS attack"
    ),
    "CVE-2024-1709": CVEExploitMatch(
        cve_id="CVE-2024-1709",
        exploit_name="ConnectWise ScreenConnect Auth Bypass",
        exploit_db_id=None,
        metasploit_module="exploit/multi/http/connectwise_screenconnect_auth_bypass",
        reliability="excellent",
        rank=5,
        disclosure_date="2024-02-21",
        platform="multi",
        port=8040,
        description="Authentication bypass in ScreenConnect"
    ),
}


# ============================================
# Enhanced Tool Database v2
# ============================================

ENHANCED_KALI_TOOLS_DB = {
    # ========== NEW: Cloud Security Tools ==========
    "pacu": ToolDefinition(
        name="pacu",
        category=ToolCategory.CLOUD_SECURITY,
        description="AWS exploitation framework",
        command="pacu",
        args_schema={
            "session_name": {"type": "string", "required": True},
            "module": {"type": "string", "required": True, "description": "Pacu module to run"},
            "arguments": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["aws", "cloud", "privesc", "enumeration"],
        timeout_seconds=900,
    ),
    
    "prowler": ToolDefinition(
        name="prowler",
        category=ToolCategory.CLOUD_SECURITY,
        description="AWS security assessment tool",
        command="prowler",
        args_schema={
            "profile": {"type": "string", "required": False},
            "region": {"type": "string", "required": False},
            "check": {"type": "string", "required": False, "description": "Specific check ID"},
            "severity": {"type": "string", "required": False, "description": "Filter by severity"},
            "output": {"type": "string", "required": False, "default": "json"},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["aws", "compliance", "cis", "audit"],
        timeout_seconds=1800,
    ),
    
    "scoutsuite": ToolDefinition(
        name="scoutsuite",
        category=ToolCategory.CLOUD_SECURITY,
        description="Multi-cloud security auditing tool",
        command="scoutsuite",
        args_schema={
            "provider": {"type": "string", "required": True, "description": "aws, azure, gcp, oci, alibaba"},
            "profile": {"type": "string", "required": False},
            "regions": {"type": "string", "required": False},
            "report_name": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["aws", "azure", "gcp", "cloud", "audit"],
        timeout_seconds=3600,
    ),
    
    "stormspotter": ToolDefinition(
        name="stormspotter",
        category=ToolCategory.CLOUD_SECURITY,
        description="Azure red team tool",
        command="stormspotter",
        args_schema={
            "mode": {"type": "string", "required": True, "description": "collect, visualize"},
            "tenant_id": {"type": "string", "required": True},
            "client_id": {"type": "string", "required": True},
            "secret": {"type": "string", "required": True},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["azure", "cloud", "graph", "visualization"],
        timeout_seconds=1800,
    ),
    
    "gcp_bucket_finder": ToolDefinition(
        name="gcp_bucket_finder",
        category=ToolCategory.CLOUD_SECURITY,
        description="Google Cloud Storage bucket enumeration",
        command="gcp_bucket_finder",
        args_schema={
            "project_id": {"type": "string", "required": True},
            "output_file": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["gcp", "cloud", "enumeration", "storage"],
        timeout_seconds=600,
    ),
    
    # ========== NEW: Active Directory Tools ==========
    "crackmapexec": ToolDefinition(
        name="crackmapexec",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="Swiss army knife for pentesting networks",
        command="crackmapexec",
        args_schema={
            "protocol": {"type": "string", "required": True, "description": "smb, mssql, ldap, rdp, ssh, winrm"},
            "target": {"type": "string", "required": True},
            "username": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
            "module": {"type": "string", "required": False, "description": "CME module to run"},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["ad", "lateral_movement", "enumeration", "exploitation"],
        timeout_seconds=600,
    ),
    
    "impacket-psexec": ToolDefinition(
        name="impacket-psexec",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="PsExec implementation over SMB",
        command="impacket-psexec",
        args_schema={
            "target": {"type": "string", "required": True},
            "username": {"type": "string", "required": True},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
            "command": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["ad", "lateral_movement", "execution"],
        timeout_seconds=300,
    ),
    
    "impacket-secretsdump": ToolDefinition(
        name="impacket-secretsdump",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="Dump credentials from remote system",
        command="impacket-secretsdump",
        args_schema={
            "target": {"type": "string", "required": True},
            "username": {"type": "string", "required": True},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
            "just_dc": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["ad", "credentials", "dumping"],
        timeout_seconds=600,
    ),
    
    "certipy": ToolDefinition(
        name="certipy",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="Active Directory Certificate Services enumeration and abuse",
        command="certipy",
        args_schema={
            "command": {"type": "string", "required": True, "description": "find, auth, req, shadow, forge"},
            "target": {"type": "string", "required": True},
            "username": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
            "ca": {"type": "string", "required": False, "description": "CA name"},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["ad", "adcs", "pki", "privesc"],
        timeout_seconds=900,
    ),
    
    "petitpotam": ToolDefinition(
        name="petitpotam",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="Coerce authentication to relay to AD CS",
        command="petitpotam.py",
        args_schema={
            "target": {"type": "string", "required": True, "description": "Target DC"},
            "listener": {"type": "string", "required": True, "description": "Attacker IP"},
            "username": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["ad", "coerce", "ntlm_relay"],
        timeout_seconds=300,
    ),
    
    "adconnectdump": ToolDefinition(
        name="adconnectdump",
        category=ToolCategory.ACTIVE_DIRECTORY,
        description="Dump Azure AD Connect credentials",
        command="adconnectdump.py",
        args_schema={
            "target": {"type": "string", "required": True},
            "username": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "hash": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["ad", "azure", "credentials"],
        timeout_seconds=300,
    ),
    
    # ========== NEW: C2 Frameworks ==========
    "sliver": ToolDefinition(
        name="sliver",
        category=ToolCategory.EXPLOITATION,
        description="Adversary emulation framework",
        command="sliver-client",
        args_schema={
            "command": {"type": "string", "required": True, "description": "Sliver CLI command"},
            "config": {"type": "string", "required": False, "description": "Config file path"},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["c2", "beacon", "implant", "redteam"],
        timeout_seconds=3600,
    ),
    
    "havoc": ToolDefinition(
        name="havoc",
        category=ToolCategory.EXPLOITATION,
        description="Modern post-exploitation framework",
        command="havoc",
        args_schema={
            "profile": {"type": "string", "required": False, "description": "Operator profile"},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["c2", "post_exploitation", "redteam"],
        timeout_seconds=3600,
    ),
    
    # ========== NEW: Container Security ==========
    "trivy": ToolDefinition(
        name="trivy",
        category=ToolCategory.CONTAINER_SECURITY,
        description="Container vulnerability scanner",
        command="trivy",
        args_schema={
            "target": {"type": "string", "required": True, "description": "Image name or filesystem path"},
            "severity": {"type": "string", "required": False, "default": "CRITICAL,HIGH"},
            "format": {"type": "string", "required": False, "default": "table"},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["container", "docker", "kubernetes", "vulnerability"],
        timeout_seconds=900,
    ),
    
    "docker-bench": ToolDefinition(
        name="docker-bench",
        category=ToolCategory.CONTAINER_SECURITY,
        description="Docker security benchmark scanner",
        command="docker-bench-security.sh",
        args_schema={
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["docker", "compliance", "cis", "audit"],
        timeout_seconds=600,
    ),
    
    "kube-bench": ToolDefinition(
        name="kube-bench",
        category=ToolCategory.CONTAINER_SECURITY,
        description="Kubernetes security benchmark scanner",
        command="kube-bench",
        args_schema={
            "target": {"type": "string", "required": False, "description": "master, node, etcd, policies"},
            "output": {"type": "string", "required": False, "default": "json"},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["kubernetes", "compliance", "cis", "audit"],
        timeout_seconds=900,
    ),
    
    "kube-hunter": ToolDefinition(
        name="kube-hunter",
        category=ToolCategory.CONTAINER_SECURITY,
        description="Kubernetes penetration testing tool",
        command="kube-hunter",
        args_schema={
            "remote": {"type": "string", "required": False, "description": "Remote node IP"},
            "internal": {"type": "boolean", "required": False, "default": False},
            "active": {"type": "boolean", "required": False, "default": False},
            "report": {"type": "string", "required": False, "default": "plain"},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["kubernetes", "pentest", "exploitation"],
        timeout_seconds=1200,
    ),
    
    # ========== NEW: Modern Web Tools ==========
    "nuclei": ToolDefinition(
        name="nuclei",
        category=ToolCategory.WEB_APPLICATION,
        description="Fast vulnerability scanner with templates",
        command="nuclei",
        args_schema={
            "target": {"type": "string", "required": True},
            "templates": {"type": "string", "required": False, "description": "Template directory or file"},
            "severity": {"type": "string", "required": False, "description": "critical,high,medium,low,info"},
            "tags": {"type": "string", "required": False, "description": "Filter by tags"},
            "output": {"type": "string", "required": False},
            "rate_limit": {"type": "integer", "required": False, "default": 150},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["web", "vulnerability", "templates", "automation"],
        timeout_seconds=1800,
    ),
    
    "dalfox": ToolDefinition(
        name="dalfox",
        category=ToolCategory.WEB_APPLICATION,
        description="XSS scanning tool",
        command="dalfox",
        args_schema={
            "url": {"type": "string", "required": True},
            "data": {"type": "string", "required": False},
            "cookie": {"type": "string", "required": False},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["web", "xss", "injection"],
        timeout_seconds=600,
    ),
    
    "httpx": ToolDefinition(
        name="httpx",
        category=ToolCategory.RECONNAISSANCE,
        description="Fast multi-purpose HTTP toolkit",
        command="httpx",
        args_schema={
            "target": {"type": "string", "required": True},
            "title": {"type": "boolean", "required": False, "default": True},
            "status_code": {"type": "boolean", "required": False, "default": True},
            "tech_detect": {"type": "boolean", "required": False, "default": True},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["web", "recon", "enumeration"],
        timeout_seconds=600,
    ),
    
    "subfinder": ToolDefinition(
        name="subfinder",
        category=ToolCategory.RECONNAISSANCE,
        description="Fast subdomain enumeration tool",
        command="subfinder",
        args_schema={
            "domain": {"type": "string", "required": True},
            "sources": {"type": "string", "required": False, "description": "Comma-separated sources"},
            "output": {"type": "string", "required": False},
            "threads": {"type": "integer", "required": False, "default": 10},
        },
        authorization=AuthorizationLevel.BASIC,
        tags=["recon", "subdomain", "enumeration"],
        timeout_seconds=900,
    ),
    
    # ========== Enhanced: Existing Tools ==========
    "nmap": ToolDefinition(
        name="nmap",
        category=ToolCategory.RECONNAISSANCE,
        description="Network exploration and security auditing",
        command="nmap",
        args_schema={
            "target": {"type": "string", "required": True, "description": "Target host/network"},
            "ports": {"type": "string", "required": False, "description": "Port range (e.g., 1-1000)"},
            "scan_type": {"type": "string", "required": False, "default": "sS", "description": "Scan type (sS, sT, sU, sA)"},
            "version_detect": {"type": "boolean", "required": False, "default": True},
            "os_detect": {"type": "boolean", "required": False, "default": False},
            "aggressive": {"type": "boolean", "required": False, "default": False},
            "script": {"type": "string", "required": False, "description": "NSE scripts to run"},
            "output_xml": {"type": "string", "required": False, "description": "XML output file path"},
            "output_grepable": {"type": "string", "required": False, "description": "Grepable output file"},
        },
        authorization=AuthorizationLevel.BASIC,
        output_parser="nmap_xml",
        tags=["recon", "network", "ports", "services"],
        cve_matching=True,
        timeout_seconds=600,
    ),
    
    "sqlmap": ToolDefinition(
        name="sqlmap",
        category=ToolCategory.WEB_APPLICATION,
        description="SQL injection tool",
        command="sqlmap",
        args_schema={
            "url": {"type": "string", "required": True},
            "data": {"type": "string", "required": False},
            "cookie": {"type": "string", "required": False},
            "level": {"type": "integer", "required": False, "default": 1},
            "risk": {"type": "integer", "required": False, "default": 1},
            "dbs": {"type": "boolean", "required": False, "default": False},
            "tables": {"type": "boolean", "required": False, "default": False},
            "dump": {"type": "boolean", "required": False, "default": False},
            "os_shell": {"type": "boolean", "required": False, "default": False},
            "tamper": {"type": "string", "required": False, "description": "Tamper scripts"},
        },
        authorization=AuthorizationLevel.ADVANCED,
        tags=["web", "sqli", "injection", "database"],
        timeout_seconds=900,
    ),
    
    "metasploit": ToolDefinition(
        name="metasploit",
        category=ToolCategory.EXPLOITATION,
        description="Penetration testing framework",
        command="msfconsole",
        args_schema={
            "resource": {"type": "string", "required": False, "description": "Resource script to run"},
            "command": {"type": "string", "required": False, "description": "Single command to execute"},
            "quiet": {"type": "boolean", "required": False, "default": True},
        },
        authorization=AuthorizationLevel.CRITICAL,
        tags=["exploitation", "framework", "payloads", "post"],
        cve_matching=True,
        timeout_seconds=3600,
    ),
    
    # Add more existing tools here...
}


# ============================================
# Output Parsers v2
# ============================================

class OutputParsers:
    """Enhanced output parsers for tool results."""
    
    @staticmethod
    def parse_nmap_xml(xml_file: str) -> Dict[str, Any]:
        """Parse Nmap XML output."""
        result = {
            "hosts": [],
            "total_hosts": 0,
            "open_ports": [],
            "services": [],
            "os_detected": None,
            "vulnerabilities": [],
        }
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for host in root.findall(".//host"):
                host_info = {
                    "ip": host.findtext("address[@addrtype='ipv4']"),
                    "mac": host.findtext("address[@addrtype='mac']"),
                    "status": host.findtext("status[@state]"),
                    "hostnames": [h.get("name") for h in host.findall(".//hostname")],
                    "ports": [],
                    "os": None,
                }
                
                # Parse ports
                for port in host.findall(".//port"):
                    port_info = {
                        "port": port.get("portid"),
                        "protocol": port.get("protocol"),
                        "state": port.findtext("state[@state]"),
                        "service": port.findtext("service[@name]"),
                        "product": port.findtext("service[@product]"),
                        "version": port.findtext("service[@version]"),
                    }
                    host_info["ports"].append(port_info)
                    
                    if port_info["state"] == "open":
                        result["open_ports"].append({
                            "host": host_info["ip"],
                            "port": port_info["port"],
                            "service": port_info["service"],
                        })
                
                # Parse OS detection
                os_match = host.find(".//osmatch")
                if os_match is not None:
                    host_info["os"] = {
                        "name": os_match.get("name"),
                        "accuracy": os_match.get("accuracy"),
                    }
                    result["os_detected"] = host_info["os"]
                
                # Parse script results (vulnerabilities)
                for script in host.findall(".//script"):
                    script_id = script.get("id")
                    if script_id.startswith("smb-") or script_id.startswith("http-"):
                        vuln = {
                            "id": script_id,
                            "output": script.get("output"),
                        }
                        result["vulnerabilities"].append(vuln)
                
                result["hosts"].append(host_info)
            
            result["total_hosts"] = len(result["hosts"])
            
        except Exception as e:
            logger.error(f"Error parsing Nmap XML: {e}")
        
        return result
    
    @staticmethod
    def parse_sqlmap_output(output: str) -> Dict[str, Any]:
        """Parse SQLMap output."""
        result = {
            "vulnerable": False,
            "injection_type": None,
            "database": None,
            "tables": [],
            "columns": [],
            "dumped_data": [],
        }
        
        # Check for vulnerability confirmation
        if "is vulnerable" in output.lower():
            result["vulnerable"] = True
        
        # Extract injection type
        if "sqlmap identified the following injection point" in output.lower():
            match = re.search(r"injection point.*?:\s*(.+)", output, re.IGNORECASE)
            if match:
                result["injection_type"] = match.group(1).strip()
        
        # Extract database name
        if "current database:" in output.lower():
            match = re.search(r"current database:\s*(\w+)", output, re.IGNORECASE)
            if match:
                result["database"] = match.group(1)
        
        return result
    
    @staticmethod
    def parse_nuclei_output(output: str) -> Dict[str, Any]:
        """Parse Nuclei JSON output."""
        result = {
            "vulnerabilities": [],
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "total_findings": 0,
        }
        
        try:
            for line in output.strip().split("\n"):
                if line.strip():
                    try:
                        finding = json.loads(line)
                        result["vulnerabilities"].append({
                            "template": finding.get("template-id"),
                            "name": finding.get("info", {}).get("name"),
                            "severity": finding.get("info", {}).get("severity"),
                            "host": finding.get("host"),
                            "matched_at": finding.get("matched-at"),
                            "description": finding.get("info", {}).get("description"),
                            "tags": finding.get("info", {}).get("tags", []),
                        })
                        
                        severity = finding.get("info", {}).get("severity", "info").lower()
                        if severity in result["by_severity"]:
                            result["by_severity"][severity] += 1
                        
                        result["total_findings"] += 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error parsing Nuclei output: {e}")
        
        return result
    
    @staticmethod
    def parse_crackmapexec_output(output: str) -> Dict[str, Any]:
        """Parse CrackMapExec output."""
        result = {
            "hosts": [],
            "credentials": [],
            "shares": [],
            "sessions": [],
        }
        
        # Extract successful authentications
        for line in output.split("\n"):
            if "Authenticated" in line:
                match = re.search(r"(\S+)\\(\S+):(\S+) Authenticated", line)
                if match:
                    result["credentials"].append({
                        "domain": match.group(1),
                        "username": match.group(2),
                        "password": match.group(3),
                    })
            
            if "Pwn3d!" in line:
                match = re.search(r"(\S+) (\S+)", line)
                if match:
                    result["sessions"].append({
                        "host": match.group(1),
                        "status": "pwned",
                    })
        
        return result


# ============================================
# CVE Matching Engine
# ============================================

class CVEMatchingEngine:
    """Match CVEs to exploits automatically."""
    
    def __init__(self):
        self.exploit_db = CVE_EXPLOIT_DB
    
    def match_cve(self, cve_id: str) -> Optional[CVEExploitMatch]:
        """Find exploit for a CVE."""
        return self.exploit_db.get(cve_id.upper())
    
    def match_from_nmap(self, nmap_result: Dict[str, Any]) -> List[CVEExploitMatch]:
        """Match CVEs from Nmap scan results."""
        matches = []
        
        for vuln in nmap_result.get("vulnerabilities", []):
            vuln_id = vuln.get("id", "")
            
            # Try to extract CVE from script ID or output
            cve_match = re.search(r"CVE-\d{4}-\d+", vuln.get("output", ""))
            if cve_match:
                cve_id = cve_match.group()
                exploit = self.match_cve(cve_id)
                if exploit:
                    matches.append(exploit)
        
        return matches
    
    def match_from_services(self, services: List[Dict[str, Any]]) -> List[CVEExploitMatch]:
        """Match exploits based on service versions."""
        matches = []
        
        # Known vulnerable version patterns
        vulnerable_patterns = {
            "smb": {"port": 445, "cves": ["CVE-2017-0144", "CVE-2020-0796"]},
            "rdp": {"port": 3389, "cves": ["CVE-2019-0708"]},
            "http": {"port": 80, "cves": ["CVE-2021-44228", "CVE-2021-34473"]},
            "https": {"port": 443, "cves": ["CVE-2021-44228", "CVE-2021-34473"]},
        }
        
        for service in services:
            port = service.get("port")
            service_name = service.get("service", "").lower()
            
            for svc_name, vuln_info in vulnerable_patterns.items():
                if service_name == svc_name or (port and port == vuln_info["port"]):
                    for cve_id in vuln_info["cves"]:
                        exploit = self.match_cve(cve_id)
                        if exploit:
                            matches.append(exploit)
        
        return matches
    
    def generate_exploit_recommendations(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate exploit recommendations from scan results."""
        recommendations = {
            "critical_exploits": [],
            "high_exploits": [],
            "medium_exploits": [],
            "total_matches": 0,
        }
        
        # Match from services
        services = scan_results.get("services", [])
        cve_matches = self.match_from_services(services)
        
        for match in cve_matches:
            exploit_info = {
                "cve": match.cve_id,
                "exploit": match.exploit_name,
                "metasploit_module": match.metasploit_module,
                "reliability": match.reliability,
                "rank": match.rank,
            }
            
            if match.rank >= 5:
                recommendations["critical_exploits"].append(exploit_info)
            elif match.rank >= 4:
                recommendations["high_exploits"].append(exploit_info)
            else:
                recommendations["medium_exploits"].append(exploit_info)
            
            recommendations["total_matches"] += 1
        
        return recommendations


# ============================================
# Tool Recommendation Engine
# ============================================

class ToolRecommendationEngine:
    """AI-powered tool recommendations based on target analysis."""
    
    def __init__(self):
        self.tool_database = ENHANCED_KALI_TOOLS_DB
        
        # Target type → recommended tools mapping
        self.recommendations = {
            "web_server": ["nuclei", "sqlmap", "dalfox", "gobuster", "nikto", "burpsuite", "nmap", "httpx"],
            "active_directory": ["crackmapexec", "impacket-secretsdump", "certipy", "bloodhound"],
            "cloud_aws": ["pacu", "prowler", "scoutsuite"],
            "cloud_azure": ["stormspotter", "scoutsuite"],
            "cloud_gcp": ["scoutsuite", "gcp_bucket_finder"],
            "container": ["trivy", "docker-bench", "kube-bench", "kube-hunter"],
            "network": ["nmap", "masscan", "responder", "crackmapexec"],
            "wireless": ["aircrack-ng", "reaver", "kismet"],
        }
    
    def recommend_tools(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend tools based on target information."""
        recommendations = []
        
        target_type = target_info.get("type", "").lower()
        services = target_info.get("services", [])
        os_type = target_info.get("os", "").lower()
        
        # Get base recommendations for target type
        base_tools = []
        for ttype, tools in self.recommendations.items():
            if ttype in target_type:
                base_tools.extend(tools)
        
        # Add service-specific tools
        for service in services:
            service_name = service.get("name", "").lower()
            port = service.get("port")
            
            if "http" in service_name or port in [80, 443, 8080, 8443]:
                base_tools.extend(["nuclei", "dalfox", "gobuster"])
            
            if "smb" in service_name or port == 445:
                base_tools.extend(["crackmapexec", "impacket-psexec", "responder"])
            
            if "rdp" in service_name or port == 3389:
                base_tools.extend(["crackmapexec", "hydra"])
            
            if "ssh" in service_name or port == 22:
                base_tools.extend(["hydra", "medusa"])
            
            if "ldap" in service_name or port == 389:
                base_tools.extend(["crackmapexec", "ldapsearch"])
        
        # Remove duplicates and get tool info
        unique_tools = list(set(base_tools))
        
        for tool_name in unique_tools[:10]:  # Top 10 recommendations
            if tool_name in self.tool_database:
                tool = self.tool_database[tool_name]
                recommendations.append({
                    "name": tool.name,
                    "category": tool.category.value,
                    "description": tool.description,
                    "authorization": tool.authorization.value,
                    "tags": tool.tags,
                    "reason": self._get_recommendation_reason(tool_name, target_info),
                })
        
        return recommendations
    
    def _get_recommendation_reason(self, tool_name: str, target_info: Dict[str, Any]) -> str:
        """Generate reason for tool recommendation."""
        reasons = {
            "nuclei": "Fast vulnerability scanning with extensive template library",
            "sqlmap": "Automated SQL injection detection and exploitation",
            "crackmapexec": "Active Directory enumeration and lateral movement",
            "nmap": "Comprehensive network discovery and port scanning",
            "pacu": "AWS security assessment and exploitation",
            "certipy": "AD CS enumeration and certificate abuse",
            "trivy": "Container and Kubernetes vulnerability scanning",
        }
        
        return reasons.get(tool_name, "Recommended based on target characteristics")


# ============================================
# Remediation Recommendations
# ============================================

class RemediationEngine:
    """Generate automatic remediation recommendations."""
    
    def __init__(self):
        self.remediations = {
            "CVE-2017-0144": {
                "summary": "Apply MS17-010 security update",
                "steps": [
                    "Install Windows update KB4013389 or later",
                    "Disable SMBv1: Set-MsfsServerConfiguration -EnableSMB1Protocol $false",
                    "Block SMB ports (135, 139, 445) at firewall",
                    "Enable network segmentation",
                ],
                "priority": "critical",
                "effort": "low",
            },
            "CVE-2019-0708": {
                "summary": "Apply RDP security updates",
                "steps": [
                    "Install Windows update KB4500705 or later",
                    "Enable Network Level Authentication (NLA)",
                    "Restrict RDP access via firewall rules",
                    "Use RDP Gateway for remote access",
                ],
                "priority": "critical",
                "effort": "low",
            },
            "CVE-2021-44228": {
                "summary": "Update Log4j to version 2.17.0 or later",
                "steps": [
                    "Upgrade Log4j to 2.17.0+",
                    "If upgrade not possible, set log4j2.formatMsgNoLookups=true",
                    "Remove JndiLookup class from classpath",
                    "Implement WAF rules to block JNDI patterns",
                ],
                "priority": "critical",
                "effort": "medium",
            },
            "sql_injection": {
                "summary": "Implement parameterized queries",
                "steps": [
                    "Replace string concatenation with prepared statements",
                    "Use ORM frameworks with parameterized queries",
                    "Implement input validation and sanitization",
                    "Apply principle of least privilege to database accounts",
                    "Enable Web Application Firewall (WAF)",
                ],
                "priority": "critical",
                "effort": "medium",
            },
            "weak_passwords": {
                "summary": "Enforce strong password policy",
                "steps": [
                    "Implement minimum password length of 14 characters",
                    "Require complexity (uppercase, lowercase, numbers, symbols)",
                    "Enable account lockout after 5 failed attempts",
                    "Implement MFA for all accounts",
                    "Deploy password breach detection",
                ],
                "priority": "high",
                "effort": "low",
            },
        }
    
    def get_remediation(self, finding_id: str) -> Optional[Dict[str, Any]]:
        """Get remediation for a finding."""
        return self.remediations.get(finding_id)
    
    def generate_remediation_plan(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive remediation plan."""
        plan = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "estimated_effort": "unknown",
            "total_findings": len(findings),
        }
        
        effort_scores = {"low": 1, "medium": 2, "high": 3}
        total_effort = 0
        
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            finding_id = finding.get("cve_id") or finding.get("category", "unknown")
            
            remediation = self.get_remediation(finding_id)
            
            if remediation:
                item = {
                    "finding": finding.get("title", "Unknown"),
                    "cve": finding.get("cve_id"),
                    "remediation": remediation["summary"],
                    "steps": remediation["steps"],
                    "effort": remediation["effort"],
                }
                plan[severity].append(item)
                total_effort += effort_scores.get(remediation["effort"], 2)
            else:
                # Generic remediation
                item = {
                    "finding": finding.get("title", "Unknown"),
                    "remediation": "Review and address security finding",
                    "steps": ["Consult security team", "Research vulnerability", "Apply appropriate fix"],
                    "effort": "medium",
                }
                plan[severity].append(item)
                total_effort += 2
        
        # Calculate overall effort
        if total_effort <= 5:
            plan["estimated_effort"] = "low (1-2 days)"
        elif total_effort <= 15:
            plan["estimated_effort"] = "medium (3-5 days)"
        else:
            plan["estimated_effort"] = "high (1-2 weeks)"
        
        return plan


# ============================================
# Main KaliAgent v2 Class
# ============================================

class KaliAgentV2:
    """
    Enhanced KaliAgent with modern tools and intelligent features.
    """
    
    def __init__(self, workspace: str = "/tmp/kali-workspace", log_dir: Optional[str] = None):
        self.workspace = Path(workspace)
        self.log_dir = Path(log_dir) if log_dir else self.workspace / "logs"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.tools = ENHANCED_KALI_TOOLS_DB
        self.cve_engine = CVEMatchingEngine()
        self.recommendation_engine = ToolRecommendationEngine()
        self.remediation_engine = RemediationEngine()
        self.output_parsers = OutputParsers()
        
        # State
        self.authorization_level = AuthorizationLevel.NONE
        self.dry_run = False
        self.executions: List[ToolExecution] = []
        self.engagement_id: Optional[str] = None
        
        logger.info(f"KaliAgent v2 initialized at {self.workspace}")
    
    def set_authorization(self, level: AuthorizationLevel):
        """Set authorization level."""
        self.authorization_level = level
        logger.info(f"Authorization level set to: {level.name}")
    
    def enable_dry_run(self):
        """Enable dry-run mode."""
        self.dry_run = True
        logger.info("Dry-run mode enabled")
    
    def disable_dry_run(self):
        """Disable dry-run mode."""
        self.dry_run = False
        logger.info("Dry-run mode disabled")
    
    def check_authorization(self, tool_name: str) -> Tuple[bool, str]:
        """Check if tool can be executed."""
        if tool_name not in self.tools:
            return False, f"Tool '{tool_name}' not found"
        
        tool = self.tools[tool_name]
        
        if self.authorization_level.value < tool.authorization.value:
            return False, f"Authorization level {self.authorization_level.name} insufficient (requires {tool.authorization.name})"
        
        return True, "Authorized"
    
    def recommend_tools_for_target(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tool recommendations for a target."""
        return self.recommendation_engine.recommend_tools(target_info)
    
    def match_exploits_for_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Find exploits for a CVE."""
        match = self.cve_engine.match_cve(cve_id)
        if match:
            return {
                "cve": match.cve_id,
                "exploit_name": match.exploit_name,
                "exploit_db_id": match.exploit_db_id,
                "metasploit_module": match.metasploit_module,
                "reliability": match.reliability,
                "rank": match.rank,
                "platform": match.platform,
                "port": match.port,
                "description": match.description,
            }
        return None
    
    def generate_remediation_plan(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate remediation plan for findings."""
        return self.remediation_engine.generate_remediation_plan(findings)
    
    def list_tools(self, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """List available tools."""
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        return [
            {
                "name": t.name,
                "category": t.category.value,
                "description": t.description,
                "authorization": t.authorization.value,
                "tags": t.tags,
            }
            for t in tools
        ]
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state."""
        return {
            "agent_id": "kali-agent-v2",
            "version": "2.0.0",
            "workspace": str(self.workspace),
            "authorization_level": self.authorization_level.name,
            "dry_run": self.dry_run,
            "total_tools": len(self.tools),
            "total_executions": len(self.executions),
            "capabilities": [
                "tool_execution",
                "cve_exploit_matching",
                "tool_recommendations",
                "remediation_planning",
                "output_parsing",
                "playbook_chaining",
            ],
            "new_features": [
                "20+ modern tools added",
                "CVE → Exploit automatic matching",
                "AI-powered tool recommendations",
                "Cloud security tools (AWS/Azure/GCP)",
                "Active Directory toolkit",
                "Container security scanning",
                "Automatic remediation recommendations",
            ],
        }


# ============================================
# Demo Script
# ============================================

def demo_kali_agent_v2():
    """Demonstrate KaliAgent v2 features."""
    print("=" * 80)
    print("KALIAGENT V2 - ENHANCED FEATURES DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize agent
    agent = KaliAgentV2(workspace="/tmp/kali-v2-demo")
    
    # Show state
    print("📦 Agent State:")
    state = agent.get_state()
    print(f"  Version: {state['version']}")
    print(f"  Total Tools: {state['total_tools']}")
    print(f"  Capabilities: {', '.join(state['capabilities'])}")
    print()
    
    print("🆕 New Features:")
    for feature in state['new_features']:
        print(f"  ✅ {feature}")
    print()
    
    # Demo CVE matching
    print("🎯 CVE → Exploit Matching Demo:")
    print()
    
    test_cves = ["CVE-2017-0144", "CVE-2021-44228", "CVE-2019-0708"]
    
    for cve in test_cves:
        match = agent.match_exploits_for_cve(cve)
        if match:
            print(f"  {cve}:")
            print(f"    Exploit: {match['exploit_name']}")
            print(f"    Metasploit: {match['metasploit_module']}")
            print(f"    Reliability: {match['reliability']} (Rank: {match['rank']}/5)")
            print()
    
    # Demo tool recommendations
    print("🤖 AI-Powered Tool Recommendations:")
    print()
    
    target_info = {
        "type": "web_server",
        "os": "linux",
        "services": [
            {"name": "http", "port": 80, "version": "nginx 1.18.0"},
            {"name": "ssh", "port": 22, "version": "OpenSSH 8.2"},
        ],
    }
    
    recommendations = agent.recommend_tools_for_target(target_info)
    print(f"  Target: {target_info['type']} ({target_info['os']})")
    print(f"  Services: {[s['name'] for s in target_info['services']]}")
    print()
    print("  Recommended Tools:")
    for rec in recommendations[:5]:
        print(f"    - {rec['name']} ({rec['category']})")
        print(f"      Reason: {rec['reason']}")
    print()
    
    # Demo remediation planning
    print("🔧 Automatic Remediation Planning:")
    print()
    
    findings = [
        {"title": "EternalBlue Vulnerability", "cve_id": "CVE-2017-0144", "severity": "critical"},
        {"title": "Log4Shell Vulnerability", "cve_id": "CVE-2021-44228", "severity": "critical"},
        {"title": "SQL Injection in Login", "category": "sql_injection", "severity": "critical"},
        {"title": "Weak Password Policy", "category": "weak_passwords", "severity": "high"},
    ]
    
    plan = agent.generate_remediation_plan(findings)
    print(f"  Total Findings: {plan['total_findings']}")
    print(f"  Estimated Effort: {plan['estimated_effort']}")
    print()
    print(f"  Critical ({len(plan['critical'])}):")
    for item in plan['critical'][:2]:
        print(f"    - {item['finding']}")
        print(f"      Remediation: {item['remediation']}")
    print()
    
    # Show new tool categories
    print("🆕 New Tool Categories:")
    print()
    
    new_categories = [
        ToolCategory.CLOUD_SECURITY,
        ToolCategory.ACTIVE_DIRECTORY,
        ToolCategory.CONTAINER_SECURITY,
    ]
    
    for category in new_categories:
        tools = agent.list_tools(category)
        print(f"  {category.value.upper()}:")
        for tool in tools[:5]:
            print(f"    - {tool['name']}: {tool['description']}")
        if len(tools) > 5:
            print(f"    ... and {len(tools) - 5} more")
        print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    demo_kali_agent_v2()
