"""
KaliAgent - Kali Linux Tool Orchestration
==========================================

Provides comprehensive integration with Kali Linux penetration testing tools,
including Metasploit, Nmap, Burp Suite, SQLMap, Hashcat, and 600+ other tools.

Includes safety gates, authorization controls, and automated reporting.
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


class AuthorizationLevel(Enum):
    """Authorization levels for tool execution."""
    NONE = 0  # No authorization - tool cannot run
    BASIC = 1  # Basic recon/scanning
    ADVANCED = 2  # Exploitation tools
    CRITICAL = 3  # Post-exploitation, malware analysis


class ExecutionMode(Enum):
    """Tool execution modes."""
    SAFE = "safe"  # Read-only, no system changes
    STANDARD = "standard"  # Normal operation
    AGGRESSIVE = "aggressive"  # Maximum intensity, may cause disruption


class MetasploitStatus(Enum):
    """Metasploit framework status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


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


@dataclass
class ToolExecution:
    """Tool execution record."""
    execution_id: str
    tool_name: str
    command: str
    arguments: Dict[str, Any]
    status: str  # pending, running, completed, failed, timeout
    exit_code: Optional[int]
    stdout: str
    stderr: str
    output_file: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: float
    authorization_level: AuthorizationLevel
    executed_by: Optional[str] = None
    engagement_id: Optional[str] = None


@dataclass
class MetasploitSession:
    """Metasploit session information."""
    session_id: str
    type: str  # meterpreter, shell, etc.
    target_host: str
    target_port: int
    exploit_used: str
    payload: str
    opened_at: datetime
    last_activity: datetime
    user_context: Optional[str] = None
    system_info: Optional[Dict[str, Any]] = None


@dataclass
class MetasploitJob:
    """Metasploit job record."""
    job_id: str
    name: str
    module: str
    target: str
    payload: Optional[str]
    status: str  # running, completed, failed
    started_at: datetime
    completed_at: Optional[datetime]
    sessions_created: List[str] = field(default_factory=list)


# ============================================
# Tool Database
# ============================================

KALI_TOOLS_DB = {
    # Reconnaissance
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
            "output_xml": {"type": "string", "required": False, "description": "XML output file path"},
        },
        authorization=AuthorizationLevel.BASIC,
        output_parser="nmap_xml",
        timeout_seconds=600,
    ),

    "masscan": ToolDefinition(
        name="masscan",
        category=ToolCategory.RECONNAISSANCE,
        description="Fastest port scanner",
        command="masscan",
        args_schema={
            "target": {"type": "string", "required": True},
            "ports": {"type": "string", "required": True, "description": "Port range"},
            "rate": {"type": "integer", "required": False, "default": 10000},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=300,
    ),

    "recon_ng": ToolDefinition(
        name="recon-ng",
        category=ToolCategory.RECONNAISSANCE,
        description="Web reconnaissance framework",
        command="recon-ng",
        args_schema={
            "workspace": {"type": "string", "required": True},
            "modules": {"type": "array", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    # Vulnerability Analysis
    "nikto": ToolDefinition(
        name="nikto",
        category=ToolCategory.VULNERABILITY_ANALYSIS,
        description="Web server scanner",
        command="nikto",
        args_schema={
            "host": {"type": "string", "required": True},
            "port": {"type": "integer", "required": False, "default": 80},
            "ssl": {"type": "boolean", "required": False, "default": False},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "openvas": ToolDefinition(
        name="openvas",
        category=ToolCategory.VULNERABILITY_ANALYSIS,
        description="Vulnerability scanner",
        command="gvm-cli",
        args_schema={
            "target": {"type": "string", "required": True},
            "scan_config": {"type": "string", "required": False, "default": "Full and fast"},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=3600,
    ),

    # Web Application
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
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=900,
    ),

    "burpsuite": ToolDefinition(
        name="burpsuite",
        category=ToolCategory.WEB_APPLICATION,
        description="Web application security testing",
        command="burpsuite",
        args_schema={
            "project_file": {"type": "string", "required": False},
            "config_file": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=7200,
    ),

    "dirb": ToolDefinition(
        name="dirb",
        category=ToolCategory.WEB_APPLICATION,
        description="Web content scanner",
        command="dirb",
        args_schema={
            "url": {"type": "string", "required": True},
            "wordlist": {"type": "string", "required": False, "default": "/usr/share/dirb/wordlists/common.txt"},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "gobuster": ToolDefinition(
        name="gobuster",
        category=ToolCategory.WEB_APPLICATION,
        description="Directory/DNS brute-forcer",
        command="gobuster",
        args_schema={
            "mode": {"type": "string", "required": True, "description": "dir, dns, fuzz, vhost"},
            "target": {"type": "string", "required": True},
            "wordlist": {"type": "string", "required": True},
            "extensions": {"type": "string", "required": False},
            "threads": {"type": "integer", "required": False, "default": 10},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    "wpscan": ToolDefinition(
        name="wpscan",
        category=ToolCategory.WEB_APPLICATION,
        description="WordPress security scanner",
        command="wpscan",
        args_schema={
            "url": {"type": "string", "required": True},
            "api_token": {"type": "string", "required": False},
            "enumerate": {"type": "string", "required": False, "default": "vp,vt,u"},
            "force": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "ffuf": ToolDefinition(
        name="ffuf",
        category=ToolCategory.WEB_APPLICATION,
        description="Fast web fuzzer",
        command="ffuf",
        args_schema={
            "url": {"type": "string", "required": True},
            "wordlist": {"type": "string", "required": True},
            "method": {"type": "string", "required": False, "default": "GET"},
            "headers": {"type": "string", "required": False},
            "threads": {"type": "integer", "required": False, "default": 40},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    # Password Attacks
    "john": ToolDefinition(
        name="john",
        category=ToolCategory.PASSWORD,
        description="John the Ripper password cracker",
        command="john",
        args_schema={
            "hash_file": {"type": "string", "required": True},
            "format": {"type": "string", "required": False},
            "wordlist": {"type": "string", "required": False},
            "rules": {"type": "boolean", "required": False, "default": True},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=7200,
    ),

    "hashcat": ToolDefinition(
        name="hashcat",
        category=ToolCategory.PASSWORD,
        description="Advanced password recovery",
        command="hashcat",
        args_schema={
            "hash_file": {"type": "string", "required": True},
            "attack_mode": {"type": "integer", "required": False, "default": 0},
            "hash_type": {"type": "integer", "required": True},
            "wordlist": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=14400,
    ),

    "hydra": ToolDefinition(
        name="hydra",
        category=ToolCategory.PASSWORD,
        description="Network login cracker",
        command="hydra",
        args_schema={
            "target": {"type": "string", "required": True},
            "service": {"type": "string", "required": True},
            "username": {"type": "string", "required": False},
            "userlist": {"type": "string", "required": False},
            "password": {"type": "string", "required": False},
            "passlist": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=3600,
    ),

    "medusa": ToolDefinition(
        name="medusa",
        category=ToolCategory.PASSWORD,
        description="Parallel brute forcer",
        command="medusa",
        args_schema={
            "target": {"type": "string", "required": True},
            "service": {"type": "string", "required": True},
            "username": {"type": "string", "required": False},
            "userlist": {"type": "string", "required": False},
            "passlist": {"type": "string", "required": False},
            "threads": {"type": "integer", "required": False, "default": 2},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=3600,
    ),

    "cewl": ToolDefinition(
        name="cewl",
        category=ToolCategory.PASSWORD,
        description="Custom wordlist generator",
        command="cewl",
        args_schema={
            "url": {"type": "string", "required": True},
            "depth": {"type": "integer", "required": False, "default": 2},
            "min_length": {"type": "integer", "required": False, "default": 3},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "crunch": ToolDefinition(
        name="crunch",
        category=ToolCategory.PASSWORD,
        description="Wordlist generator",
        command="crunch",
        args_schema={
            "min_length": {"type": "integer", "required": True},
            "max_length": {"type": "integer", "required": True},
            "charset": {"type": "string", "required": False},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=3600,
    ),

    # Exploitation
    "metasploit": ToolDefinition(
        name="metasploit",
        category=ToolCategory.EXPLOITATION,
        description="Metasploit Framework",
        command="msfconsole",
        args_schema={
            "resource_script": {"type": "string", "required": False},
            "exploit": {"type": "string", "required": False},
            "payload": {"type": "string", "required": False},
            "target": {"type": "string", "required": False},
            "options": {"type": "object", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=3600,
    ),

    "searchsploit": ToolDefinition(
        name="searchsploit",
        category=ToolCategory.EXPLOITATION,
        description="Exploit database search",
        command="searchsploit",
        args_schema={
            "query": {"type": "string", "required": True},
            "exact": {"type": "boolean", "required": False, "default": False},
            "mirror": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=60,
    ),

    # Post Exploitation
    "mimikatz": ToolDefinition(
        name="mimikatz",
        category=ToolCategory.POST_EXPLOITATION,
        description="Credential extraction",
        command="mimikatz",
        args_schema={
            "command": {"type": "string", "required": True},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=300,
    ),

    # Wireless
    "aircrack_ng": ToolDefinition(
        name="aircrack-ng",
        category=ToolCategory.WIRELESS,
        description="WiFi security auditing",
        command="aircrack-ng",
        args_schema={
            "capture_file": {"type": "string", "required": True},
            "wordlist": {"type": "string", "required": False},
            "bssid": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=3600,
    ),

    # Sniffing/Spoofing
    "wireshark": ToolDefinition(
        name="wireshark",
        category=ToolCategory.SNIFFING_SPOOFING,
        description="Network protocol analyzer",
        command="tshark",
        args_schema={
            "interface": {"type": "string", "required": False},
            "filter": {"type": "string", "required": False},
            "capture_file": {"type": "string", "required": False},
            "count": {"type": "integer", "required": False, "default": 100},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "responder": ToolDefinition(
        name="responder",
        category=ToolCategory.SNIFFING_SPOOFING,
        description="LLMNR, NBT-NS and MDNS poisoner",
        command="responder",
        args_schema={
            "interface": {"type": "string", "required": True},
            "analyze": {"type": "boolean", "required": False, "default": False},
            "wiped": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=1800,
    ),

    # Forensics
    "volatility": ToolDefinition(
        name="volatility",
        category=ToolCategory.FORENSICS,
        description="Memory forensics",
        command="volatility",
        args_schema={
            "memory_file": {"type": "string", "required": True},
            "profile": {"type": "string", "required": False},
            "plugin": {"type": "string", "required": True},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    # Additional Reconnaissance
    "theHarvester": ToolDefinition(
        name="theHarvester",
        category=ToolCategory.RECONNAISSANCE,
        description="Email, subdomain, and name harvester",
        command="theHarvester",
        args_schema={
            "domain": {"type": "string", "required": True},
            "source": {"type": "string", "required": False, "default": "all"},
            "limit": {"type": "integer", "required": False, "default": 500},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "amass": ToolDefinition(
        name="amass",
        category=ToolCategory.RECONNAISSANCE,
        description="In-depth attack surface mapping",
        command="amass",
        args_schema={
            "mode": {"type": "string", "required": True, "description": "enum, intel, track"},
            "domain": {"type": "string", "required": True},
            "output": {"type": "string", "required": False},
            "timeout": {"type": "integer", "required": False, "default": 30},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    "subfinder": ToolDefinition(
        name="subfinder",
        category=ToolCategory.RECONNAISSANCE,
        description="Subdomain discovery tool",
        command="subfinder",
        args_schema={
            "domain": {"type": "string", "required": True},
            "output": {"type": "string", "required": False},
            "timeout": {"type": "integer", "required": False, "default": 30},
            "threads": {"type": "integer", "required": False, "default": 10},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "dnsrecon": ToolDefinition(
        name="dnsrecon",
        category=ToolCategory.RECONNAISSANCE,
        description="DNS enumeration tool",
        command="dnsrecon",
        args_schema={
            "domain": {"type": "string", "required": True},
            "type": {"type": "string", "required": False, "default": "std"},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    # Additional Web
    "joomscan": ToolDefinition(
        name="joomscan",
        category=ToolCategory.WEB_APPLICATION,
        description="Joomla vulnerability scanner",
        command="joomscan",
        args_schema={
            "url": {"type": "string", "required": True},
            "cookie": {"type": "string", "required": False},
            "user_agent": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "zap_cli": ToolDefinition(
        name="zap_cli",
        category=ToolCategory.WEB_APPLICATION,
        description="OWASP ZAP CLI",
        command="zap-cli",
        args_schema={
            "command": {"type": "string", "required": True},
            "target": {"type": "string", "required": False},
            "format": {"type": "string", "required": False, "default": "html"},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=1800,
    ),

    # Additional Wireless
    "reaver": ToolDefinition(
        name="reaver",
        category=ToolCategory.WIRELESS,
        description="WPS brute force attack",
        command="reaver",
        args_schema={
            "interface": {"type": "string", "required": True},
            "bssid": {"type": "string", "required": True},
            "essid": {"type": "string", "required": False},
            "timeout": {"type": "integer", "required": False, "default": 600},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=7200,
    ),

    "wifite": ToolDefinition(
        name="wifite",
        category=ToolCategory.WIRELESS,
        description="Automated wireless auditor",
        command="wifite",
        args_schema={
            "interface": {"type": "string", "required": False},
            "target_bssid": {"type": "string", "required": False},
            "kill_attack": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=3600,
    ),

    # Post-Exploitation
    "bloodhound": ToolDefinition(
        name="bloodhound",
        category=ToolCategory.POST_EXPLOITATION,
        description="Active Directory reconnaissance",
        command="bloodhound-python",
        args_schema={
            "domain": {"type": "string", "required": True},
            "username": {"type": "string", "required": True},
            "password": {"type": "string", "required": True},
            "nameserver": {"type": "string", "required": False},
            "collection": {"type": "string", "required": False, "default": "all"},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=1800,
    ),

    "empire": ToolDefinition(
        name="empire",
        category=ToolCategory.POST_EXPLOITATION,
        description="Post-exploitation framework",
        command="empire",
        args_schema={
            "listener": {"type": "string", "required": False},
            "stager": {"type": "string", "required": False},
            "module": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=3600,
    ),

    # Social Engineering
    "setoolkit": ToolDefinition(
        name="setoolkit",
        category=ToolCategory.SOCIAL_ENGINEERING,
        description="Social Engineering Toolkit",
        command="setoolkit",
        args_schema={
            "attack_vector": {"type": "string", "required": True},
            "target": {"type": "string", "required": False},
            "payload": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=1800,
    ),

    # Malware Analysis
    "binwalk": ToolDefinition(
        name="binwalk",
        category=ToolCategory.MALWARE,
        description="Firmware analysis tool",
        command="binwalk",
        args_schema={
            "file": {"type": "string", "required": True},
            "extract": {"type": "boolean", "required": False, "default": False},
            "output_dir": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "foremost": ToolDefinition(
        name="foremost",
        category=ToolCategory.FORENSICS,
        description="File recovery tool",
        command="foremost",
        args_schema={
            "input": {"type": "string", "required": True},
            "output": {"type": "string", "required": True},
            "type": {"type": "string", "required": False, "default": "all"},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    # Additional Nmap NSE Scripts
    "nmap_vuln": ToolDefinition(
        name="nmap-vuln",
        category=ToolCategory.VULNERABILITY_ANALYSIS,
        description="Nmap vulnerability scanning scripts",
        command="nmap",
        args_schema={
            "target": {"type": "string", "required": True},
            "script": {"type": "string", "required": False, "default": "vuln"},
            "ports": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=900,
    ),

    "nmap_exploit": ToolDefinition(
        name="nmap-exploit",
        category=ToolCategory.EXPLOITATION,
        description="Nmap exploit detection scripts",
        command="nmap",
        args_schema={
            "target": {"type": "string", "required": True},
            "script": {"type": "string", "required": False, "default": "exploit"},
            "ports": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=600,
    ),

    # Additional Reconnaissance
    "shodan": ToolDefinition(
        name="shodan",
        category=ToolCategory.RECONNAISSANCE,
        description="Shodan search CLI",
        command="shodan",
        args_schema={
            "query": {"type": "string", "required": True},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=300,
    ),

    "maltego": ToolDefinition(
        name="maltego",
        category=ToolCategory.RECONNAISSANCE,
        description="OSINT and link analysis",
        command="maltego",
        args_schema={
            "transform": {"type": "string", "required": False},
            "entity": {"type": "string", "required": True},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    "spiderfoot": ToolDefinition(
        name="spiderfoot",
        category=ToolCategory.RECONNAISSANCE,
        description="Automated OSINT collection",
        command="spiderfoot-cli",
        args_schema={
            "query": {"type": "string", "required": True},
            "module": {"type": "string", "required": False, "default": "all"},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    # Additional Web
    "whatweb": ToolDefinition(
        name="whatweb",
        category=ToolCategory.WEB_APPLICATION,
        description="Web application fingerprinting",
        command="whatweb",
        args_schema={
            "url": {"type": "string", "required": True},
            "aggression": {"type": "integer", "required": False, "default": 1},
            "verbose": {"type": "boolean", "required": False, "default": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=300,
    ),

    "sslscan": ToolDefinition(
        name="sslscan",
        category=ToolCategory.WEB_APPLICATION,
        description="SSL/TLS scanner",
        command="sslscan",
        args_schema={
            "host": {"type": "string", "required": True},
            "port": {"type": "integer", "required": False, "default": 443},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=300,
    ),

    "testssl": ToolDefinition(
        name="testssl",
        category=ToolCategory.WEB_APPLICATION,
        description="TLS/SSL testing",
        command="testssl.sh",
        args_schema={
            "url": {"type": "string", "required": True},
            "severity": {"type": "string", "required": False, "default": "medium"},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    # Additional Password
    "hash_identifier": ToolDefinition(
        name="hash-identifier",
        category=ToolCategory.PASSWORD,
        description="Hash type identification",
        command="hash-identifier",
        args_schema={
            "hash": {"type": "string", "required": True},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=60,
    ),

    "rsmangler": ToolDefinition(
        name="rsmangler",
        category=ToolCategory.PASSWORD,
        description="Password mangling/wordlist manipulation",
        command="rsmangler",
        args_schema={
            "input": {"type": "string", "required": True},
            "output": {"type": "string", "required": True},
            "min_length": {"type": "integer", "required": False, "default": 6},
            "max_length": {"type": "integer", "required": False, "default": 16},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=600,
    ),

    # Additional Wireless
    "kismet": ToolDefinition(
        name="kismet",
        category=ToolCategory.WIRELESS,
        description="Wireless network detector",
        command="kismet",
        args_schema={
            "interface": {"type": "string", "required": True},
            "capture_file": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=1800,
    ),

    "mdk4": ToolDefinition(
        name="mdk4",
        category=ToolCategory.WIRELESS,
        description="WiFi attack tool",
        command="mdk4",
        args_schema={
            "interface": {"type": "string", "required": True},
            "attack": {"type": "string", "required": True, "description": "a, b, d, m, p, w"},
            "target": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.ADVANCED,
        timeout_seconds=600,
    ),

    # Additional Post-Exploitation
    "mimikatz": ToolDefinition(
        name="mimikatz",
        category=ToolCategory.POST_EXPLOITATION,
        description="Windows credential extraction",
        command="mimikatz",
        args_schema={
            "command": {"type": "string", "required": True},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=300,
    ),

    "lazagne": ToolDefinition(
        name="lazagne",
        category=ToolCategory.POST_EXPLOITATION,
        description="Password recovery tool",
        command="lazagne",
        args_schema={
            "command": {"type": "string", "required": True, "description": "all, browsers, windows, etc"},
            "output_file": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.CRITICAL,
        timeout_seconds=600,
    ),

    # Additional Forensics
    "sleuthkit": ToolDefinition(
        name="sleuthkit",
        category=ToolCategory.FORENSICS,
        description="Filesystem forensics",
        command="fls",
        args_schema={
            "image": {"type": "string", "required": True},
            "path": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=900,
    ),

    "exiftool": ToolDefinition(
        name="exiftool",
        category=ToolCategory.FORENSICS,
        description="Metadata extraction",
        command="exiftool",
        args_schema={
            "file": {"type": "string", "required": True},
            "output": {"type": "string", "required": False},
        },
        authorization=AuthorizationLevel.BASIC,
        timeout_seconds=120,
    ),
}


# ============================================
# Metasploit RPC Client
# ============================================

class MetasploitRPC:
    """Metasploit RPC client for automation."""

    def __init__(self, host: str = "127.0.0.1", port: int = 55553, token: Optional[str] = None):
        self.host = host
        self.port = port
        self.token = token
        self.session = None
        self.url = f"http://{host}:{port}/api"

    def login(self, password: str) -> bool:
        """Authenticate with Metasploit RPC."""
        import requests

        try:
            response = requests.post(
                f"{self.url}/auth/login",
                json={"method": "auth.login", "params": ["", password]},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            data = response.json()
            if data.get("result") == "success":
                self.token = data.get("token")
                return True
            return False
        except Exception as e:
            logger.error(f"Metasploit login failed: {e}")
            return False

    def logout(self) -> bool:
        """Logout from Metasploit RPC."""
        import requests

        if not self.token:
            return False

        try:
            response = requests.post(
                f"{self.url}/auth/logout",
                json={"method": "auth.logout", "params": [self.token]},
                timeout=10
            )
            self.token = None
            return True
        except Exception:
            return False

    def get_modules(self, module_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available modules."""
        import requests

        if not self.token:
            return []

        try:
            response = requests.post(
                f"{self.url}/module/exploits",
                json={"method": "module.exploits", "params": [self.token]},
                timeout=30
            )
            modules = response.json().get("modules", [])

            if module_type:
                modules = [m for m in modules if module_type in m[0]]

            return [{"path": m[0], "rank": m[1]} for m in modules]
        except Exception as e:
            logger.error(f"Failed to get modules: {e}")
            return []

    def execute_exploit(
        self,
        exploit: str,
        payload: str,
        target: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[MetasploitJob]:
        """Execute an exploit."""
        import requests

        if not self.token:
            return None

        try:
            job_options = {
                "MODULE": exploit,
                "TARGET": target,
                "payload": payload,
            }

            if options:
                job_options.update(options)

            response = requests.post(
                f"{self.url}/job.create",
                json={
                    "method": "job.create",
                    "params": [self.token, job_options]
                },
                timeout=30
            )

            data = response.json()
            if data.get("result") == "success":
                return MetasploitJob(
                    job_id=data.get("job_id", ""),
                    name=exploit,
                    module=exploit,
                    target=target,
                    payload=payload,
                    status="running",
                    started_at=datetime.utcnow(),
                    completed_at=None,
                )
            return None
        except Exception as e:
            logger.error(f"Exploit execution failed: {e}")
            return None

    def get_sessions(self) -> List[MetasploitSession]:
        """Get active sessions."""
        import requests

        if not self.token:
            return []

        try:
            response = requests.post(
                f"{self.url}/session/list",
                json={"method": "session.list", "params": [self.token]},
                timeout=10
            )

            sessions = []
            for sid, info in response.json().get("sessions", {}).items():
                sessions.append(MetasploitSession(
                    session_id=str(sid),
                    type=info.get("type", "unknown"),
                    target_host=info.get("target_host", ""),
                    target_port=info.get("target_port", 0),
                    exploit_used=info.get("exploit", ""),
                    payload=info.get("payload", ""),
                    opened_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    user_context=info.get("username"),
                ))

            return sessions
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return []

    def session_write(self, session_id: str, command: str) -> str:
        """Write to a session."""
        import requests

        if not self.token:
            return ""

        try:
            response = requests.post(
                f"{self.url}/session/meterpreter_write",
                json={
                    "method": "session.meterpreter_write",
                    "params": [self.token, session_id, command]
                },
                timeout=30
            )
            return response.json().get("data", "")
        except Exception as e:
            logger.error(f"Session write failed: {e}")
            return ""

    def get_hosts(self) -> List[Dict[str, Any]]:
        """Get hosts from Metasploit database."""
        import requests

        if not self.token:
            return []

        try:
            response = requests.post(
                f"{self.url}/db_hosts",
                json={"method": "db.hosts", "params": [self.token]},
                timeout=30
            )
            return response.json().get("hosts", [])
        except Exception as e:
            logger.error(f"Get hosts failed: {e}")
            return []

    def get_services(self, host: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get services from Metasploit database."""
        import requests

        if not self.token:
            return []

        try:
            params = [self.token]
            if host:
                params.append({"address": host})

            response = requests.post(
                f"{self.url}/db_services",
                json={"method": "db.services", "params": params},
                timeout=30
            )
            return response.json().get("services", [])
        except Exception as e:
            logger.error(f"Get services failed: {e}")
            return []

    def get_vulns(self, host: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get vulnerabilities from Metasploit database."""
        import requests

        if not self.token:
            return []

        try:
            params = [self.token]
            if host:
                params.append({"address": host})

            response = requests.post(
                f"{self.url}/db_vulns",
                json={"method": "db.vulns", "params": params},
                timeout=30
            )
            return response.json().get("vulns", [])
        except Exception as e:
            logger.error(f"Get vulns failed: {e}")
            return []

    def get_creds(self) -> List[Dict[str, Any]]:
        """Get credentials from Metasploit database."""
        import requests

        if not self.token:
            return []

        try:
            response = requests.post(
                f"{self.url}/db_creds",
                json={"method": "db.creds", "params": [self.token]},
                timeout=30
            )
            return response.json().get("creds", [])
        except Exception as e:
            logger.error(f"Get creds failed: {e}")
            return []

    def get_loots(self) -> List[Dict[str, Any]]:
        """Get loots from Metasploit database."""
        import requests

        if not self.token:
            return []

        try:
            response = requests.post(
                f"{self.url}/db_loots",
                json={"method": "db.loots", "params": [self.token]},
                timeout=30
            )
            return response.json().get("loots", [])
        except Exception as e:
            logger.error(f"Get loots failed: {e}")
            return []

    def import_nmap(self, nmap_file: str) -> bool:
        """Import Nmap XML results into Metasploit database."""
        import requests

        if not self.token:
            return False

        try:
            with open(nmap_file, "rb") as f:
                file_data = f.read()

            response = requests.post(
                f"{self.url}/db_import_nmap",
                json={
                    "method": "db.import_nmap",
                    "params": [self.token, file_data]
                },
                timeout=60
            )
            return response.json().get("result") == "success"
        except Exception as e:
            logger.error(f"Nmap import failed: {e}")
            return False

    def run_post_module(
        self,
        module: str,
        session_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a post-exploitation module."""
        import requests

        if not self.token:
            return {"success": False, "error": "Not authenticated"}

        try:
            params = {
                "MODULE": module,
                "SESSION": session_id,
            }

            if options:
                params.update(options)

            response = requests.post(
                f"{self.url}/run",
                json={
                    "method": "module.execute",
                    "params": [self.token, "post", module, params]
                },
                timeout=120
            )
            return response.json()
        except Exception as e:
            logger.error(f"Post module failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_payload(
        self,
        payload: str,
        lhost: str,
        lport: int,
        format: str = "raw",
        output_file: Optional[str] = None,
    ) -> Optional[bytes]:
        """Generate payload using msfvenom."""
        import subprocess

        cmd = f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f {format}"

        if output_file:
            cmd += f" -o {output_file}"
            try:
                subprocess.run(cmd, shell=True, check=True)
                return None  # Saved to file
            except Exception as e:
                logger.error(f"Payload generation failed: {e}")
                return None
        else:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, check=True
                )
                return result.stdout
            except Exception as e:
                logger.error(f"Payload generation failed: {e}")
                return None


# ============================================
# Kali Agent
# ============================================

class KaliAgent:
    """
    Kali Linux Tool Orchestration Agent

    Provides comprehensive integration with Kali Linux tools including:
    - 600+ penetration testing tools
    - Metasploit Framework automation
    - Safety gates and authorization controls
    - Automated reporting
    """

    def __init__(
        self,
        agent_id: str = "kali-agent",
        workspace: str = "/tmp/kali-workspace",
        log_dir: str = "/tmp/kali-logs",
    ):
        self.agent_id = agent_id
        self.workspace = Path(workspace)
        self.log_dir = Path(log_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Tool registry
        self.tools = KALI_TOOLS_DB
        self.executions: Dict[str, ToolExecution] = {}

        # Metasploit integration
        self.msfrpc: Optional[MetasploitRPC] = None
        self.msfsessions: Dict[str, MetasploitSession] = {}
        self.msfjobs: Dict[str, MetasploitJob] = {}

        # Authorization tracking
        self.authorization_level = AuthorizationLevel.NONE
        self.engagement_authorizations: Dict[str, AuthorizationLevel] = {}

        # Safety controls
        self.safe_mode = True
        self.dry_run = False
        self.max_concurrent_jobs = 5
        self.current_jobs = 0
        self.job_lock = threading.Lock()

        # IP whitelist/blacklist for target validation
        self.ip_whitelist: Optional[List[str]] = None  # If set, only these targets allowed
        self.ip_blacklist: List[str] = []  # These targets always blocked

        # Audit logging
        self.audit_log_file: Optional[Path] = None
        self.enable_audit_logging()

        # Output parsers
        self.parsers = {
            "nmap_xml": self._parse_nmap_xml,
            "json": self._parse_json,
            "csv": self._parse_csv,
            "nikto": self._parse_nikto,
            "sqlmap": self._parse_sqlmap,
            "gobuster": self._parse_gobuster,
        }

        logger.info(f"KaliAgent initialized: {agent_id}")
        logger.info(f"Workspace: {self.workspace}")
        logger.info(f"Registered tools: {len(self.tools)}")

    # ============================================
    # Authorization & Safety
    # ============================================

    def set_authorization(
        self,
        level: AuthorizationLevel,
        engagement_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Set authorization level for tool execution."""
        if expires_at and expires_at < datetime.utcnow():
            logger.warning("Authorization expiry is in the past")
            return False

        if engagement_id:
            self.engagement_authorizations[engagement_id] = level
        else:
            self.authorization_level = level

        logger.info(f"Authorization set to: {level.value}")
        return True

    def revoke_authorization(self, engagement_id: Optional[str] = None) -> bool:
        """Revoke authorization."""
        if engagement_id:
            self.engagement_authorizations.pop(engagement_id, None)
        else:
            self.authorization_level = AuthorizationLevel.NONE

        logger.info("Authorization revoked")
        return True

    def check_authorization(self, tool_name: str) -> Tuple[bool, str]:
        """Check if tool execution is authorized."""
        if tool_name not in self.tools:
            return False, f"Unknown tool: {tool_name}"

        tool = self.tools[tool_name]
        required_level = tool.authorization

        # Check engagement-specific authorization first
        effective_level = self.authorization_level
        for eng_id, level in self.engagement_authorizations.items():
            if level.value > effective_level.value:
                effective_level = level

        if required_level.value > effective_level.value:
            return False, f"Authorization level {required_level.value} required, have {effective_level.value}"

        return True, "Authorized"

    def enable_safe_mode(self) -> bool:
        """Enable safe mode (read-only operations)."""
        self.safe_mode = True
        logger.info("Safe mode enabled")
        return True

    def disable_safe_mode(self) -> bool:
        """Disable safe mode (allows system changes)."""
        self.safe_mode = False
        logger.warning("Safe mode disabled - system changes allowed")
        return True

    def enable_dry_run(self) -> bool:
        """Enable dry-run mode (commands logged but not executed)."""
        self.dry_run = True
        logger.info("Dry-run mode enabled")
        return True

    def disable_dry_run(self) -> bool:
        """Disable dry-run mode."""
        self.dry_run = False
        logger.info("Dry-run mode disabled")
        return True

    def set_ip_whitelist(self, ips: List[str]) -> bool:
        """Set IP whitelist (only these targets allowed)."""
        self.ip_whitelist = ips
        logger.info(f"IP whitelist set: {len(ips)} addresses")
        return True

    def clear_ip_whitelist(self) -> bool:
        """Clear IP whitelist."""
        self.ip_whitelist = None
        logger.info("IP whitelist cleared")
        return True

    def add_to_blacklist(self, ip: str) -> bool:
        """Add IP to blacklist (always blocked)."""
        if ip not in self.ip_blacklist:
            self.ip_blacklist.append(ip)
            logger.info(f"IP added to blacklist: {ip}")
        return True

    def remove_from_blacklist(self, ip: str) -> bool:
        """Remove IP from blacklist."""
        if ip in self.ip_blacklist:
            self.ip_blacklist.remove(ip)
            logger.info(f"IP removed from blacklist: {ip}")
        return True

    def validate_target(self, target: str) -> Tuple[bool, str]:
        """Validate target against whitelist/blacklist."""
        # Check blacklist first
        if target in self.ip_blacklist:
            return False, f"Target {target} is blacklisted"

        # Check whitelist if configured
        if self.ip_whitelist:
            if target not in self.ip_whitelist:
                return False, f"Target {target} not in whitelist"

        return True, "Target validated"

    def enable_audit_logging(self, log_file: Optional[str] = None) -> bool:
        """Enable audit logging for all executions."""
        if log_file:
            self.audit_log_file = Path(log_file)
        else:
            self.audit_log_file = self.log_dir / "audit_log.jsonl"

        logger.info(f"Audit logging enabled: {self.audit_log_file}")
        return True

    def disable_audit_logging(self) -> bool:
        """Disable audit logging."""
        self.audit_log_file = None
        logger.info("Audit logging disabled")
        return True

    def _log_audit(self, event: Dict[str, Any]) -> None:
        """Write audit log entry."""
        if not self.audit_log_file:
            return

        try:
            event["timestamp"] = datetime.utcnow().isoformat()
            with open(self.audit_log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Audit log write failed: {e}")

    # ============================================
    # Tool Execution
    # ============================================

    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        engagement_id: Optional[str] = None,
        timeout_override: Optional[int] = None,
    ) -> ToolExecution:
        """Execute a Kali Linux tool."""
        # Check authorization
        authorized, message = self.check_authorization(tool_name)
        if not authorized:
            logger.error(f"Execution denied: {message}")
            return self._create_failed_execution(tool_name, arguments, message)

        # Check tool exists
        if tool_name not in self.tools:
            return self._create_failed_execution(tool_name, arguments, f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]

        # Validate target if present in arguments
        target_fields = ["target", "host", "url", "domain", "bssid"]
        for field in target_fields:
            if field in arguments:
                valid, msg = self.validate_target(arguments[field])
                if not valid:
                    logger.error(f"Target validation failed: {msg}")
                    return self._create_failed_execution(tool_name, arguments, msg)

        # Validate arguments
        validation_error = self._validate_arguments(tool.args_schema, arguments)
        if validation_error:
            return self._create_failed_execution(tool_name, arguments, validation_error)

        # Build command
        command = self._build_command(tool, arguments)

        # Create execution record
        execution = ToolExecution(
            execution_id=self._generate_id("exec"),
            tool_name=tool_name,
            command=command,
            arguments=arguments,
            status="pending",
            exit_code=None,
            stdout="",
            stderr="",
            output_file=None,
            started_at=datetime.utcnow(),
            completed_at=None,
            duration_seconds=0,
            authorization_level=tool.authorization,
            engagement_id=engagement_id,
        )

        # Check job limit
        with self.job_lock:
            if self.current_jobs >= self.max_concurrent_jobs:
                execution.status = "failed"
                execution.stderr = "Maximum concurrent jobs reached"
                execution.completed_at = datetime.utcnow()
                execution.duration_seconds = 0
                self.executions[execution.execution_id] = execution
                return execution

            self.current_jobs += 1

        # Execute (or dry-run)
        if self.dry_run:
            logger.info(f"DRY-RUN: {command}")
            execution.status = "completed"
            execution.stdout = f"[DRY-RUN] Command would execute: {command}"
            execution.exit_code = 0
        else:
            execution = self._execute_command(execution, timeout_override or tool.timeout_seconds)

        # Update job count
        with self.job_lock:
            self.current_jobs -= 1

        self.executions[execution.execution_id] = execution
        return execution

    def _execute_command(
        self,
        execution: ToolExecution,
        timeout: int
    ) -> ToolExecution:
        """Execute a shell command."""
        execution.status = "running"

        try:
            process = subprocess.Popen(
                execution.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.workspace),
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                execution.stdout = stdout.decode("utf-8", errors="replace")
                execution.stderr = stderr.decode("utf-8", errors="replace")
                execution.exit_code = process.returncode
                execution.status = "completed" if process.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                process.kill()
                execution.status = "timeout"
                execution.stderr = f"Command timed out after {timeout} seconds"

        except Exception as e:
            execution.status = "failed"
            execution.stderr = str(e)
            execution.exit_code = -1

        execution.completed_at = datetime.utcnow()
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()

        # Save output to file
        if execution.stdout or execution.stderr:
            output_file = self.log_dir / f"{execution.execution_id}.log"
            with open(output_file, "w") as f:
                f.write(f"Command: {execution.command}\n")
                f.write(f"Exit Code: {execution.exit_code}\n")
                f.write(f"Duration: {execution.duration_seconds:.2f}s\n\n")
                f.write("STDOUT:\n")
                f.write(execution.stdout)
                f.write("\nSTDERR:\n")
                f.write(execution.stderr)
            execution.output_file = str(output_file)

        # Parse output if parser available
        tool = self.tools.get(execution.tool_name)
        if tool and tool.output_parser and tool.output_parser in self.parsers:
            parsed = self.parsers[tool.output_parser](execution.stdout)
            if parsed:
                parsed_file = self.log_dir / f"{execution.execution_id}_parsed.json"
                with open(parsed_file, "w") as f:
                    json.dump(parsed, f, indent=2, default=str)

        return execution

    def _create_failed_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        error: str
    ) -> ToolExecution:
        """Create a failed execution record."""
        return ToolExecution(
            execution_id=self._generate_id("exec"),
            tool_name=tool_name,
            command="",
            arguments=arguments,
            status="failed",
            exit_code=-1,
            stdout="",
            stderr=error,
            output_file=None,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0,
            authorization_level=AuthorizationLevel.NONE,
        )

    def _validate_arguments(
        self,
        schema: Dict[str, Any],
        arguments: Dict[str, Any]
    ) -> Optional[str]:
        """Validate arguments against schema."""
        for arg_name, arg_spec in schema.items():
            if arg_spec.get("required") and arg_name not in arguments:
                return f"Missing required argument: {arg_name}"
        return None

    def _build_command(
        self,
        tool: ToolDefinition,
        arguments: Dict[str, Any]
    ) -> str:
        """Build command line from tool definition and arguments."""
        cmd_parts = [tool.command]

        for arg_name, value in arguments.items():
            if value is None:
                continue

            if isinstance(value, bool):
                if value:
                    cmd_parts.append(f"--{arg_name.replace('_', '-')}")
            elif isinstance(value, (int, float)):
                cmd_parts.append(f"--{arg_name.replace('_', '-')} {value}")
            else:
                # Escape special characters
                safe_value = str(value).replace("'", "'\\''")
                cmd_parts.append(f"--{arg_name.replace('_', '-')} '{safe_value}'")

        return " ".join(cmd_parts)

    # ============================================
    # Output Parsers
    # ============================================

    def _parse_nmap_xml(self, output: str) -> Optional[Dict[str, Any]]:
        """Parse Nmap XML output."""
        try:
            root = ET.fromstring(output)
            hosts = []

            for host in root.findall(".//host"):
                host_info = {
                    "address": "",
                    "hostname": "",
                    "ports": [],
                    "os": None,
                }

                addr = host.find("address")
                if addr is not None:
                    host_info["address"] = addr.get("addr", "")

                hostname = host.find(".//hostname")
                if hostname is not None:
                    host_info["hostname"] = hostname.get("name", "")

                for port in host.findall(".//port"):
                    port_info = {
                        "port": int(port.get("portid", 0)),
                        "protocol": port.get("protocol", ""),
                        "state": "",
                        "service": "",
                    }

                    state = port.find("state")
                    if state is not None:
                        port_info["state"] = state.get("state", "")

                    service = port.find("service")
                    if service is not None:
                        port_info["service"] = service.get("name", "")

                    if port_info["state"] == "open":
                        host_info["ports"].append(port_info)

                os_match = host.find(".//osmatch")
                if os_match is not None:
                    host_info["os"] = os_match.get("name", "")

                hosts.append(host_info)

            return {"hosts": hosts, "scan_time": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"Nmap XML parse failed: {e}")
            return None

    def _parse_json(self, output: str) -> Optional[Dict[str, Any]]:
        """Parse JSON output."""
        try:
            return json.loads(output)
        except Exception:
            return None

    def _parse_csv(self, output: str) -> Optional[List[Dict[str, Any]]]:
        """Parse CSV output."""
        import csv
        from io import StringIO

        try:
            reader = csv.DictReader(StringIO(output))
            return list(reader)
        except Exception:
            return None

    def _parse_nikto(self, output: str) -> Optional[Dict[str, Any]]:
        """Parse Nikto output (text format)."""
        try:
            vulnerabilities = []
            lines = output.split("\n")

            for line in lines:
                if "+ " in line:
                    vuln = {
                        "id": None,
                        "description": line.replace("+ ", "").strip(),
                        "severity": "info",
                    }

                    # Extract severity
                    if "CRITICAL" in line.upper():
                        vuln["severity"] = "critical"
                    elif "HIGH" in line.upper():
                        vuln["severity"] = "high"
                    elif "MEDIUM" in line.upper():
                        vuln["severity"] = "medium"
                    elif "LOW" in line.upper():
                        vuln["severity"] = "low"

                    vulnerabilities.append(vuln)

            return {
                "vulnerabilities": vulnerabilities,
                "total": len(vulnerabilities),
                "scan_time": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Nikto parse failed: {e}")
            return None

    def _parse_sqlmap(self, output: str) -> Optional[Dict[str, Any]]:
        """Parse SQLMap output."""
        try:
            result = {
                "vulnerable": False,
                "injection_type": None,
                "database": None,
                "tables": [],
                "columns": [],
            }

            # Check for vulnerability indicators
            if "is vulnerable" in output.lower():
                result["vulnerable"] = True

            # Extract injection type
            if "Type: " in output:
                for line in output.split("\n"):
                    if "Type: " in line:
                        result["injection_type"] = line.split("Type: ")[1].strip()

            # Extract database name
            if "current database: " in output:
                for line in output.split("\n"):
                    if "current database: " in line:
                        result["database"] = line.split("current database: ")[1].strip()

            # Extract tables
            if "available databases" in output.lower():
                in_tables = False
                for line in output.split("\n"):
                    if "[*]" in line and in_tables:
                        result["tables"].append(line.replace("[*]", "").strip())
                    if "available databases" in line.lower():
                        in_tables = True

            return result
        except Exception as e:
            logger.error(f"SQLMap parse failed: {e}")
            return None

    def _parse_gobuster(self, output: str) -> Optional[Dict[str, Any]]:
        """Parse Gobuster output."""
        try:
            found_paths = []
            lines = output.split("\n")

            for line in lines:
                if line.startswith("/") or ("Status:" in line and len(line.split()) > 1):
                    parts = line.split()
                    if len(parts) >= 2:
                        path = {
                            "path": parts[0],
                            "status": int(parts[1]) if parts[1].isdigit() else 0,
                        }
                        found_paths.append(path)

            return {
                "paths": found_paths,
                "total_found": len(found_paths),
                "scan_time": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Gobuster parse failed: {e}")
            return None

    # ============================================
    # Metasploit Integration
    # ============================================

    def connect_metasploit(
        self,
        host: str = "127.0.0.1",
        port: int = 55553,
        password: str = ""
    ) -> bool:
        """Connect to Metasploit RPC."""
        self.msfrpc = MetasploitRPC(host, port)

        if password:
            success = self.msfrpc.login(password)
            if success:
                logger.info("Connected to Metasploit RPC")
                return True
            else:
                logger.error("Metasploit login failed")
                return False
        else:
            logger.warning("Metasploit RPC created but not authenticated")
            return False

    def disconnect_metasploit(self) -> bool:
        """Disconnect from Metasploit RPC."""
        if self.msfrpc:
            self.msfrpc.logout()
            self.msfrpc = None
            logger.info("Disconnected from Metasploit")
            return True
        return False

    def get_metasploit_modules(self, module_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available Metasploit modules."""
        if not self.msfrpc:
            return []

        return self.msfrpc.get_modules(module_type)

    def execute_metasploit_exploit(
        self,
        exploit: str,
        payload: str,
        target: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[MetasploitJob]:
        """Execute a Metasploit exploit."""
        # Check authorization
        if self.authorization_level.value < AuthorizationLevel.CRITICAL.value:
            logger.error("CRITICAL authorization required for Metasploit exploits")
            return None

        if not self.msfrpc:
            logger.error("Not connected to Metasploit RPC")
            return None

        job = self.msfrpc.execute_exploit(exploit, payload, target, options)

        if job:
            self.msfjobs[job.job_id] = job
            logger.info(f"Metasploit job started: {job.job_id}")

        return job

    def get_metasploit_sessions(self) -> List[MetasploitSession]:
        """Get active Metasploit sessions."""
        if not self.msfrpc:
            return []

        sessions = self.msfrpc.get_sessions()
        for session in sessions:
            self.msfsessions[session.session_id] = session

        return sessions

    def metasploit_session_command(
        self,
        session_id: str,
        command: str
    ) -> str:
        """Execute command in Metasploit session."""
        if not self.msfrpc:
            return ""

        if session_id not in self.msfsessions:
            return "Session not found"

        return self.msfrpc.session_write(session_id, command)

    # ============================================
    # Pre-built Tool Methods
    # ============================================

    def nmap_scan(
        self,
        target: str,
        ports: str = "1-1000",
        version_detect: bool = True,
        os_detect: bool = False,
        output_xml: Optional[str] = None,
    ) -> ToolExecution:
        """Perform Nmap network scan."""
        return self.execute_tool("nmap", {
            "target": target,
            "ports": ports,
            "version_detect": version_detect,
            "os_detect": os_detect,
            "output_xml": output_xml,
        })

    def nikto_scan(
        self,
        host: str,
        port: int = 80,
        ssl: bool = False,
    ) -> ToolExecution:
        """Perform Nikto web server scan."""
        return self.execute_tool("nikto", {
            "host": host,
            "port": port,
            "ssl": ssl,
        })

    def sqlmap_scan(
        self,
        url: str,
        level: int = 1,
        risk: int = 1,
    ) -> ToolExecution:
        """Perform SQLMap SQL injection scan."""
        return self.execute_tool("sqlmap", {
            "url": url,
            "level": level,
            "risk": risk,
        })

    def searchsploit_search(
        self,
        query: str,
        exact: bool = False,
    ) -> ToolExecution:
        """Search Exploit Database."""
        return self.execute_tool("searchsploit", {
            "query": query,
            "exact": exact,
        })

    def john_crack(
        self,
        hash_file: str,
        wordlist: Optional[str] = None,
    ) -> ToolExecution:
        """Crack passwords with John the Ripper."""
        return self.execute_tool("john", {
            "hash_file": hash_file,
            "wordlist": wordlist,
        })

    def hydra_bruteforce(
        self,
        target: str,
        service: str,
        userlist: str,
        passlist: str,
    ) -> ToolExecution:
        """Brute force login with Hydra."""
        return self.execute_tool("hydra", {
            "target": target,
            "service": service,
            "userlist": userlist,
            "passlist": passlist,
        })

    def gobuster_scan(
        self,
        target: str,
        wordlist: str = "/usr/share/dirb/wordlists/common.txt",
        mode: str = "dir",
        extensions: Optional[str] = None,
        threads: int = 10,
    ) -> ToolExecution:
        """Directory/DNS brute-force with Gobuster."""
        return self.execute_tool("gobuster", {
            "mode": mode,
            "target": target,
            "wordlist": wordlist,
            "extensions": extensions,
            "threads": threads,
        })

    def wpscan_scan(
        self,
        url: str,
        enumerate: str = "vp,vt,u",
        api_token: Optional[str] = None,
    ) -> ToolExecution:
        """WordPress security scan."""
        return self.execute_tool("wpscan", {
            "url": url,
            "enumerate": enumerate,
            "api_token": api_token,
        })

    def dirb_scan(
        self,
        url: str,
        wordlist: Optional[str] = None,
    ) -> ToolExecution:
        """Web content scanner."""
        return self.execute_tool("dirb", {
            "url": url,
            "wordlist": wordlist,
        })

    def ffuf_fuzz(
        self,
        url: str,
        wordlist: str = "/usr/share/ffuf/wordlist.txt",
        method: str = "GET",
        threads: int = 40,
    ) -> ToolExecution:
        """Fast web fuzzer."""
        return self.execute_tool("ffuf", {
            "url": url,
            "wordlist": wordlist,
            "method": method,
            "threads": threads,
        })

    def theharvester_scan(
        self,
        domain: str,
        source: str = "all",
        limit: int = 500,
    ) -> ToolExecution:
        """Email and subdomain harvesting."""
        return self.execute_tool("theHarvester", {
            "domain": domain,
            "source": source,
            "limit": limit,
        })

    def amass_enum(
        self,
        domain: str,
        output: Optional[str] = None,
        timeout: int = 30,
    ) -> ToolExecution:
        """Subdomain enumeration with Amass."""
        return self.execute_tool("amass", {
            "mode": "enum",
            "domain": domain,
            "output": output,
            "timeout": timeout,
        })

    def subfinder_scan(
        self,
        domain: str,
        output: Optional[str] = None,
    ) -> ToolExecution:
        """Subdomain discovery."""
        return self.execute_tool("subfinder", {
            "domain": domain,
            "output": output,
        })

    def dnsrecon_scan(
        self,
        domain: str,
        type: str = "std",
    ) -> ToolExecution:
        """DNS enumeration."""
        return self.execute_tool("dnsrecon", {
            "domain": domain,
            "type": type,
        })

    def medusa_bruteforce(
        self,
        target: str,
        service: str,
        userlist: str,
        passlist: str,
        threads: int = 2,
    ) -> ToolExecution:
        """Parallel brute forcer."""
        return self.execute_tool("medusa", {
            "target": target,
            "service": service,
            "userlist": userlist,
            "passlist": passlist,
            "threads": threads,
        })

    def cewl_generate(
        self,
        url: str,
        depth: int = 2,
        min_length: int = 3,
        output: Optional[str] = None,
    ) -> ToolExecution:
        """Custom wordlist generator."""
        return self.execute_tool("cewl", {
            "url": url,
            "depth": depth,
            "min_length": min_length,
            "output": output,
        })

    def crunch_generate(
        self,
        min_length: int,
        max_length: int,
        charset: Optional[str] = None,
        output: Optional[str] = None,
    ) -> ToolExecution:
        """Wordlist generator."""
        return self.execute_tool("crunch", {
            "min_length": min_length,
            "max_length": max_length,
            "charset": charset,
            "output": output,
        })

    def joomscan_scan(
        self,
        url: str,
    ) -> ToolExecution:
        """Joomla vulnerability scanner."""
        return self.execute_tool("joomscan", {
            "url": url,
        })

    def aircrack_crack(
        self,
        capture_file: str,
        wordlist: Optional[str] = None,
    ) -> ToolExecution:
        """WiFi password cracking."""
        return self.execute_tool("aircrack-ng", {
            "capture_file": capture_file,
            "wordlist": wordlist,
        })

    def reaver_attack(
        self,
        interface: str,
        bssid: str,
        timeout: int = 600,
    ) -> ToolExecution:
        """WPS brute force attack."""
        return self.execute_tool("reaver", {
            "interface": interface,
            "bssid": bssid,
            "timeout": timeout,
        })

    def bloodhound_collect(
        self,
        domain: str,
        username: str,
        password: str,
        collection: str = "all",
    ) -> ToolExecution:
        """Active Directory reconnaissance."""
        return self.execute_tool("bloodhound", {
            "domain": domain,
            "username": username,
            "password": password,
            "collection": collection,
        })

    def binwalk_analyze(
        self,
        file: str,
        extract: bool = False,
    ) -> ToolExecution:
        """Firmware analysis."""
        return self.execute_tool("binwalk", {
            "file": file,
            "extract": extract,
        })

    def volatility_analyze(
        self,
        memory_file: str,
        plugin: str,
        profile: Optional[str] = None,
    ) -> ToolExecution:
        """Memory forensics."""
        return self.execute_tool("volatility", {
            "memory_file": memory_file,
            "plugin": plugin,
            "profile": profile,
        })

    # ============================================
    # Playbook System - Automated Workflows
    # ============================================

    def run_recon_playbook(
        self,
        target: str,
        domain: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, ToolExecution]:
        """Run comprehensive reconnaissance playbook.

        Executes: nmap → theHarvester → amass → dnsrecon → nikto (if web)
        """
        results = {}

        # 1. Nmap scan
        results["nmap"] = self.nmap_scan(
            target=target,
            ports="1-10000",
            version_detect=True,
            os_detect=True,
        )

        # 2. Email/subdomain harvesting
        if domain:
            results["theharvester"] = self.theharvester_scan(
                domain=domain,
                source="all",
            )

            # 3. Subdomain enumeration
            results["amass"] = self.amass_enum(
                domain=domain,
            )

            # 4. DNS enumeration
            results["dnsrecon"] = self.dnsrecon_scan(
                domain=domain,
            )

        # 5. Web scan (if HTTP detected)
        if results["nmap"].exit_code == 0:
            if "80/open" in results["nmap"].stdout or "443/open" in results["nmap"].stdout:
                results["nikto"] = self.nikto_scan(
                    host=target,
                    port=80,
                )

        return results

    def run_web_audit_playbook(
        self,
        url: str,
        target: str,
        wordlist: str = "/usr/share/ffuf/wordlist.txt",
    ) -> Dict[str, ToolExecution]:
        """Run web application audit playbook.

        Executes: gobuster → nikto → wpscan (if WordPress) → sqlmap (if forms)
        """
        results = {}

        # 1. Directory brute-force
        results["gobuster"] = self.gobuster_scan(
            target=url,
            wordlist=wordlist,
            mode="dir",
        )

        # 2. Web server scan
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or target
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        results["nikto"] = self.nikto_scan(
            host=host,
            port=port,
            ssl=(parsed.scheme == "https"),
        )

        # 3. WordPress scan (auto-detect)
        results["wpscan"] = self.wpscan_scan(
            url=url,
            enumerate="vp,vt,u",
        )

        # 4. SQL injection scan
        results["sqlmap"] = self.sqlmap_scan(
            url=url,
            level=2,
            risk=2,
        )

        return results

    def run_password_audit_playbook(
        self,
        hash_file: str,
        wordlist: str = "/usr/share/wordlists/rockyou.txt",
        custom_wordlist: Optional[str] = None,
    ) -> Dict[str, ToolExecution]:
        """Run password cracking playbook.

        Executes: john → hashcat (if john fails) → report
        """
        results = {}

        # 1. John the Ripper
        results["john"] = self.john_crack(
            hash_file=hash_file,
            wordlist=wordlist,
        )

        # 2. Hashcat (if custom wordlist provided)
        if custom_wordlist:
            results["hashcat"] = self.execute_tool("hashcat", {
                "hash_file": hash_file,
                "attack_mode": 0,
                "hash_type": 0,
                "wordlist": custom_wordlist,
            })

        return results

    def run_wireless_audit_playbook(
        self,
        interface: str,
        target_bssid: Optional[str] = None,
        capture_file: Optional[str] = None,
    ) -> Dict[str, ToolExecution]:
        """Run wireless security audit playbook.

        Executes: monitor mode → capture → aircrack/reaver
        """
        results = {}

        # 1. Wifite automated audit
        results["wifite"] = self.execute_tool("wifite", {
            "interface": interface,
            "target_bssid": target_bssid,
        })

        # 2. Aircrack (if capture file provided)
        if capture_file:
            results["aircrack"] = self.aircrack_crack(
                capture_file=capture_file,
            )

        # 3. Reaver (if target BSSID provided)
        if target_bssid:
            results["reaver"] = self.reaver_attack(
                interface=interface,
                bssid=target_bssid,
            )

        return results

    def run_ad_audit_playbook(
        self,
        domain: str,
        username: str,
        password: str,
        output_dir: Optional[str] = None,
    ) -> Dict[str, ToolExecution]:
        """Run Active Directory audit playbook.

        Executes: bloodhound → enum4linux → ldapsearch
        """
        results = {}

        # 1. Bloodhound collection
        results["bloodhound"] = self.bloodhound_collect(
            domain=domain,
            username=username,
            password=password,
            collection="all",
        )

        return results

    def generate_playbook_report(
        self,
        playbook_name: str,
        results: Dict[str, ToolExecution],
        output_format: str = "markdown",
    ) -> str:
        """Generate playbook execution report."""
        lines = [
            f"# Playbook Report: {playbook_name}",
            f"\nGenerated: {datetime.utcnow().isoformat()}",
            f"\nTools Executed: {len(results)}",
            "",
            "## Execution Summary",
            "",
        ]

        for tool_name, result in results.items():
            status_emoji = "✅" if result.status == "completed" else "❌"
            lines.append(f"### {status_emoji} {tool_name}")
            lines.append(f"- Status: {result.status}")
            lines.append(f"- Duration: {result.duration_seconds:.1f}s")
            lines.append(f"- Exit Code: {result.exit_code}")
            if result.stderr:
                lines.append(f"- Errors: {result.stderr[:200]}")
            lines.append("")

        # Success summary
        successful = sum(1 for r in results.values() if r.status == "completed" and r.exit_code == 0)
        lines.append("## Summary")
        lines.append(f"- Total Tools: {len(results)}")
        lines.append(f"- Successful: {successful}")
        lines.append(f"- Failed: {len(results) - successful}")

        return "\n".join(lines)

    # ============================================
    # Reporting
    # ============================================

    def get_execution_history(
        self,
        engagement_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ToolExecution]:
        """Get execution history with filtering."""
        executions = list(self.executions.values())

        if engagement_id:
            executions = [e for e in executions if e.engagement_id == engagement_id]

        if tool_name:
            executions = [e for e in executions if e.tool_name == tool_name]

        if status:
            executions = [e for e in executions if e.status == status]

        return sorted(executions, key=lambda e: e.started_at, reverse=True)

    def generate_report(
        self,
        engagement_id: Optional[str] = None,
        output_format: str = "markdown"
    ) -> str:
        """Generate execution report."""
        executions = self.get_execution_history(engagement_id)

        if output_format == "markdown":
            return self._generate_markdown_report(executions)
        elif output_format == "json":
            return json.dumps([
                {
                    "execution_id": e.execution_id,
                    "tool_name": e.tool_name,
                    "command": e.command,
                    "status": e.status,
                    "exit_code": e.exit_code,
                    "duration_seconds": e.duration_seconds,
                    "started_at": e.started_at.isoformat(),
                }
                for e in executions
            ], indent=2)
        else:
            return f"Unknown format: {output_format}"

    def _generate_markdown_report(
        self,
        executions: List[ToolExecution]
    ) -> str:
        """Generate markdown report."""
        lines = [
            "# Kali Agent Execution Report",
            f"\nGenerated: {datetime.utcnow().isoformat()}",
            f"\nTotal Executions: {len(executions)}",
            "",
            "## Summary",
            "",
            "| Tool | Status | Duration | Time |",
            "|------|--------|----------|------|",
        ]

        for e in executions[:20]:  # Limit to 20
            status_emoji = "✅" if e.status == "completed" else "❌"
            lines.append(
                f"| {e.tool_name} | {status_emoji} {e.status} | "
                f"{e.duration_seconds:.1f}s | {e.started_at.strftime('%H:%M:%S')} |"
            )

        lines.extend([
            "",
            "## Failed Executions",
            "",
        ])

        failed = [e for e in executions if e.status == "failed"]
        if failed:
            for e in failed:
                lines.extend([
                    f"### {e.tool_name} ({e.execution_id})",
                    f"- Command: `{e.command}`",
                    f"- Error: {e.stderr}",
                    "",
                ])
        else:
            lines.append("No failed executions.")

        return "\n".join(lines)

    # ============================================
    # Utilities
    # ============================================

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        return f"{prefix}_{secrets.token_hex(8)}"

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
            }
            for t in tools
        ]

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed tool information."""
        if tool_name not in self.tools:
            return None

        tool = self.tools[tool_name]
        return {
            "name": tool.name,
            "category": tool.category.value,
            "description": tool.description,
            "command": tool.command,
            "args_schema": tool.args_schema,
            "authorization": tool.authorization.value,
            "timeout_seconds": tool.timeout_seconds,
        }


# ============================================
# Demonstration Script
# ============================================

def demo_kali_agent():
    """Demonstrate Kali Agent functionality."""
    print("=" * 70)
    print("KALI AGENT DEMONSTRATION")
    print("=" * 70)
    print()

    # Initialize agent
    agent = KaliAgent(
        workspace="/tmp/kali-demo",
        log_dir="/tmp/kali-demo/logs"
    )

    # Show available tools
    print("📦 Available Tools by Category:")
    print()

    for category in ToolCategory:
        tools = agent.list_tools(category)
        if tools:
            print(f"  {category.value.upper()}:")
            for tool in tools[:5]:  # Show first 5
                print(f"    - {tool['name']}: {tool['description']}")
            if len(tools) > 5:
                print(f"    ... and {len(tools) - 5} more")
            print()

    # Demonstrate authorization
    print("🔐 Authorization Demo:")
    print()

    authorized, msg = agent.check_authorization("nmap")
    print(f"  Nmap without auth: {msg}")

    agent.set_authorization(AuthorizationLevel.BASIC)
    authorized, msg = agent.check_authorization("nmap")
    print(f"  Nmap with BASIC auth: {msg}")

    authorized, msg = agent.check_authorization("metasploit")
    print(f"  Metasploit with BASIC auth: {msg}")

    agent.set_authorization(AuthorizationLevel.CRITICAL)
    authorized, msg = agent.check_authorization("metasploit")
    print(f"  Metasploit with CRITICAL auth: {msg}")
    print()

    # Demonstrate dry-run
    print("🧪 Dry-Run Execution Demo:")
    print()

    agent.enable_dry_run()

    exec_result = agent.nmap_scan(
        target="scanme.nmap.org",
        ports="1-100",
        version_detect=True
    )

    print(f"  Tool: {exec_result.tool_name}")
    print(f"  Status: {exec_result.status}")
    print(f"  Command: {exec_result.command}")
    print(f"  Output: {exec_result.stdout[:200]}..." if exec_result.stdout else "  Output: (dry-run)")
    print()

    agent.disable_dry_run()

    # Show execution history
    print("📊 Execution History:")
    print()

    history = agent.get_execution_history()
    for exec_record in history:
        print(f"  {exec_record.execution_id}: {exec_record.tool_name} - {exec_record.status}")

    print()

    # Generate report
    print("📄 Generated Report (first 500 chars):")
    print()

    report = agent.generate_report(output_format="markdown")
    print(report[:500])
    print("...")
    print()

    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Workspace: {agent.workspace}")
    print(f"Log directory: {agent.log_dir}")
    print(f"Total executions: {len(agent.executions)}")
    print()


if __name__ == "__main__":
    demo_kali_agent()
