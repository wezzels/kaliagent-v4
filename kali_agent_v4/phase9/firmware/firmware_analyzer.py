#!/usr/bin/env python3
"""
💾 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
Firmware Analysis Module

Comprehensive firmware security analysis:
- Firmware download (HTTP, TFTP, FTP)
- Filesystem extraction (squashfs, jffs2, yaffs, ext)
- Binary analysis
- Hardcoded credential discovery
- Backdoor detection
- Vulnerability scanning
- CVE correlation

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import os
import re
import json
import hashlib
import subprocess
import tempfile
import shutil
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import requests
import binascii

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FirmwareAnalyzer')


@dataclass
class FirmwareInfo:
    """Firmware metadata"""
    filename: str
    filepath: str
    size_bytes: int
    md5: str
    sha256: str
    vendor: str = "Unknown"
    model: str = "Unknown"
    version: str = "Unknown"
    build_date: str = "Unknown"
    architecture: str = "Unknown"
    filesystem_type: str = "Unknown"
    
    def to_dict(self) -> Dict:
        return {
            'filename': self.filename,
            'size_bytes': self.size_bytes,
            'md5': self.md5,
            'sha256': self.sha256,
            'vendor': self.vendor,
            'model': self.model,
            'version': self.version,
            'build_date': self.build_date,
            'architecture': self.architecture,
            'filesystem_type': self.filesystem_type
        }


@dataclass
class ExtractedFile:
    """Represents an extracted file from firmware"""
    path: str
    size: int
    file_type: str
    permissions: str = ""
    owner: str = ""
    group: str = ""
    is_executable: bool = False
    is_config: bool = False
    contains_credentials: bool = False
    contains_secrets: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'path': self.path,
            'size': self.size,
            'file_type': self.file_type,
            'permissions': self.permissions,
            'is_executable': self.is_executable,
            'is_config': self.is_config,
            'contains_credentials': self.contains_credentials,
            'contains_secrets': self.contains_secrets
        }


@dataclass
class Credential:
    """Discovered credential in firmware"""
    type: str  # password, api_key, token, private_key
    value: str
    context: str  # surrounding code/config
    file_path: str
    line_number: int = 0
    severity: str = "medium"
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'value': self.value[:50] + '...' if len(self.value) > 50 else self.value,
            'context': self.context,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'severity': self.severity
        }


@dataclass
class Backdoor:
    """Discovered backdoor in firmware"""
    type: str  # hardcoded_account, hidden_service, debug_interface
    description: str
    file_path: str
    severity: str = "critical"
    cve_reference: str = ""
    evidence: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'type': self.type,
            'description': self.description,
            'file_path': self.file_path,
            'severity': self.severity,
            'cve_reference': self.cve_reference,
            'evidence': self.evidence[:100] if self.evidence else ""
        }


@dataclass
class Vulnerability:
    """Discovered vulnerability in firmware"""
    cve_id: str = ""
    description: str
    severity: str = "medium"
    cvss_score: float = 0.0
    file_path: str = ""
    affected_component: str = ""
    remediation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'cve_id': self.cve_id,
            'description': self.description,
            'severity': self.severity,
            'cvss_score': self.cvss_score,
            'file_path': self.file_path,
            'affected_component': self.affected_component,
            'remediation': self.remediation
        }


@dataclass
class FirmwareAnalysisResult:
    """Complete firmware analysis result"""
    firmware: FirmwareInfo
    extraction_path: str
    extracted_files: List[ExtractedFile] = field(default_factory=list)
    credentials: List[Credential] = field(default_factory=list)
    backdoors: List[Backdoor] = field(default_factory=list)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    risk_score: float = 0.0
    analysis_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'firmware': self.firmware.to_dict(),
            'extraction_path': self.extraction_path,
            'file_count': len(self.extracted_files),
            'credential_count': len(self.credentials),
            'backdoor_count': len(self.backdoors),
            'vulnerability_count': len(self.vulnerabilities),
            'risk_score': self.risk_score,
            'analysis_time_seconds': self.analysis_time_seconds,
            'credentials': [c.to_dict() for c in self.credentials],
            'backdoors': [b.to_dict() for b in self.backdoors],
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities]
        }


class FirmwareAnalyzer:
    """
    Firmware Security Analysis Tool
    
    Capabilities:
    - Firmware download from devices
    - Filesystem extraction
    - Binary analysis
    - Credential discovery
    - Backdoor detection
    - Vulnerability scanning
    - Report generation
    """
    
    VERSION = "0.1.0"
    
    # Filesystem signatures
    FILESYSTEM_SIGNATURES = {
        b'\x68\x73\x71\x73': 'squashfs',
        b'\x28\x05\x00\x00': 'squashfs_le',
        b'\x73\x71\x73\x68': 'squashfs_be',
        b'\x4a\x46\x46\x53': 'jffs2',
        b'\x59\x41\x46\x46': 'yaffs',
        b'\x53\x46\x49\x48': 'cramfs',
        b'\x83\x52\x46\x53': 'romfs',
        b'\xef\x53': 'ext2/ext3/ext4',
        b'\x91\x23\x68\x3e': 'ubifs',
    }
    
    # Credential patterns
    CREDENTIAL_PATTERNS = [
        (r'password\s*[=:]\s*["\']?([^"\'\s]+)', 'password'),
        (r'passwd\s*[=:]\s*["\']?([^"\'\s]+)', 'password'),
        (r'pwd\s*[=:]\s*["\']?([^"\'\s]+)', 'password'),
        (r'secret\s*[=:]\s*["\']?([^"\'\s]+)', 'secret'),
        (r'api[_-]?key\s*[=:]\s*["\']?([^"\'\s]+)', 'api_key'),
        (r'apikey\s*[=:]\s*["\']?([^"\'\s]+)', 'api_key'),
        (r'token\s*[=:]\s*["\']?([^"\'\s]+)', 'token'),
        (r'auth[_-]?token\s*[=:]\s*["\']?([^"\'\s]+)', 'token'),
        (r'private[_-]?key\s*[=:]\s*["\']?([^"\'\s]+)', 'private_key'),
        (r'-----BEGIN RSA PRIVATE KEY-----', 'private_key'),
        (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'private_key'),
        (r'aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\']?([^"\'\s]+)', 'aws_key'),
        (r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?([^"\'\s]+)', 'aws_secret'),
        (r'AKIA[0-9A-Z]{16}', 'aws_access_key'),
        (r'mysql\s+.*\s+(-h\S+\s+)?(-u\S+\s+)?(-p\S+)', 'database_cred'),
        (r'mongodb://[^:]+:[^@]+@', 'database_cred'),
        (r'postgres://[^:]+:[^@]+@', 'database_cred'),
    ]
    
    # Backdoor signatures
    BACKDOOR_SIGNATURES = [
        (r'telnetd\s+-l\s+/bin/sh', 'backdoor', 'Telnet backdoor with shell'),
        (r'nc\s+-e\s+/bin/sh', 'backdoor', 'Netcat reverse shell'),
        (r'ncat\s+-e\s+/bin/sh', 'backdoor', 'Ncat reverse shell'),
        (r'666666', 'backdoor', 'Hikvision backdoor account'),
        (r'icatch99', 'backdoor', 'Dahua backdoor password'),
        (r'/dev/mem', 'backdoor', 'Direct memory access'),
        (r'debug\s*=\s*true', 'backdoor', 'Debug mode enabled'),
        (r'dropbear', 'backdoor', 'Dropbear SSH (may be legitimate)'),
        (r'busybox\s+telnetd', 'backdoor', 'Busybox telnet daemon'),
        (r'ftpd\s+-w', 'backdoor', 'FTP with write access'),
    ]
    
    # Known CVE patterns
    CVE_PATTERNS = {
        'CVE-2017-7921': r'Hikvision.*authentication.*bypass',
        'CVE-2017-7927': r'Dahua.*backdoor',
        'CVE-2018-10660': r'Reolink.*RCE',
        'CVE-2019-6993': r'SmartThings.*RCE',
        'CVE-2020-10689': r'Multiple.*hardcoded.*credentials',
    }
    
    def __init__(self, output_dir: str = None, verbose: bool = True):
        """
        Initialize Firmware Analyzer
        
        Args:
            output_dir: Output directory for extracted files
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.output_dir = output_dir or tempfile.mkdtemp(prefix='firmware_')
        self.temp_dir = tempfile.mkdtemp(prefix='fw_analysis_')
        
        # Check for required tools
        self.binwalk_available = self._check_tool('binwalk')
        self.sasquatch_available = self._check_tool('sasquatch')
        self.ubireader_available = self._check_tool('ubireader_extract_images')
        
        logger.info(f"💾 Firmware Analyzer v{self.VERSION}")
        logger.info(f"📂 Output directory: {self.output_dir}")
        logger.info(f"🔧 Binwalk: {'✅' if self.binwalk_available else '❌'}")
        logger.info(f"🔧 Sasquatch: {'✅' if self.sasquatch_available else '❌'}")
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available"""
        try:
            subprocess.run(['which', tool_name], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def download_firmware(self, url: str, output_path: str = None) -> str:
        """
        Download firmware from URL
        
        Args:
            url: Firmware download URL
            output_path: Optional output path
            
        Returns:
            Path to downloaded firmware
        """
        logger.info(f"⬇️  Downloading firmware from {url}...")
        
        if not output_path:
            filename = url.split('/')[-1] or 'firmware.bin'
            output_path = os.path.join(self.temp_dir, filename)
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            size = os.path.getsize(output_path)
            logger.info(f"✅ Downloaded {size:,} bytes to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return None
    
    def download_from_device(self, host: str, port: int = 80, 
                              endpoint: str = '/firmware.bin') -> str:
        """
        Download firmware from device
        
        Args:
            host: Device IP/hostname
            port: HTTP port
            endpoint: Firmware endpoint path
            
        Returns:
            Path to downloaded firmware
        """
        url = f"http://{host}:{port}{endpoint}"
        return self.download_firmware(url)
    
    def analyze_firmware(self, firmware_path: str) -> FirmwareAnalysisResult:
        """
        Perform complete firmware analysis
        
        Args:
            firmware_path: Path to firmware file
            
        Returns:
            Analysis result
        """
        logger.info(f"🔍 Analyzing firmware: {firmware_path}")
        
        start_time = datetime.now()
        
        # Step 1: Get firmware info
        firmware_info = self._get_firmware_info(firmware_path)
        
        # Step 2: Detect filesystem type
        fs_type = self._detect_filesystem(firmware_path)
        firmware_info.filesystem_type = fs_type
        
        # Step 3: Extract filesystem
        extraction_path = self._extract_filesystem(firmware_path, fs_type)
        
        # Step 4: Analyze extracted files
        extracted_files = self._analyze_extracted_files(extraction_path)
        
        # Step 5: Find credentials
        credentials = self._find_credentials(extraction_path)
        
        # Step 6: Detect backdoors
        backdoors = self._detect_backdoors(extraction_path)
        
        # Step 7: Scan for vulnerabilities
        vulnerabilities = self._scan_vulnerabilities(extraction_path)
        
        # Step 8: Calculate risk score
        risk_score = self._calculate_risk_score(credentials, backdoors, vulnerabilities)
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        result = FirmwareAnalysisResult(
            firmware=firmware_info,
            extraction_path=extraction_path,
            extracted_files=extracted_files,
            credentials=credentials,
            backdoors=backdoors,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            analysis_time_seconds=analysis_time
        )
        
        logger.info(f"✅ Analysis complete in {analysis_time:.2f}s")
        logger.info(f"📊 Risk Score: {risk_score}/10.0")
        logger.info(f"🔑 Credentials: {len(credentials)}")
        logger.info(f"🚪 Backdoors: {len(backdoors)}")
        logger.info(f"⚠️  Vulnerabilities: {len(vulnerabilities)}")
        
        return result
    
    def _get_firmware_info(self, filepath: str) -> FirmwareInfo:
        """Extract firmware metadata"""
        logger.debug("  Extracting firmware metadata...")
        
        filename = os.path.basename(filepath)
        size = os.path.getsize(filepath)
        
        # Calculate hashes
        with open(filepath, 'rb') as f:
            data = f.read()
            md5 = hashlib.md5(data).hexdigest()
            sha256 = hashlib.sha256(data).hexdigest()
        
        # Try to extract vendor/model from filename
        vendor = "Unknown"
        model = "Unknown"
        version = "Unknown"
        
        # Common patterns
        patterns = [
            r'([A-Za-z]+)_?(v?\d+\.\d+\.\d+)',
            r'([A-Za-z]+)-?(\w+)-?(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 1:
                    vendor = groups[0]
                if len(groups) >= 2:
                    model = groups[1]
                if len(groups) >= 3:
                    version = groups[2]
                break
        
        return FirmwareInfo(
            filename=filename,
            filepath=filepath,
            size_bytes=size,
            md5=md5,
            sha256=sha256,
            vendor=vendor,
            model=model,
            version=version
        )
    
    def _detect_filesystem(self, filepath: str) -> str:
        """Detect filesystem type from magic bytes"""
        logger.debug("  Detecting filesystem type...")
        
        with open(filepath, 'rb') as f:
            # Read first 1KB for signature detection
            header = f.read(1024)
            
            for signature, fs_type in self.FILESYSTEM_SIGNATURES.items():
                if signature in header:
                    logger.debug(f"  Found filesystem signature: {fs_type}")
                    return fs_type
        
        # Try binwalk if available
        if self.binwalk_available:
            try:
                result = subprocess.run(
                    ['binwalk', '-e', filepath],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if 'Squashfs' in result.stdout:
                    return 'squashfs'
                elif 'JFFS2' in result.stdout:
                    return 'jffs2'
            except:
                pass
        
        return 'unknown'
    
    def _extract_filesystem(self, filepath: str, fs_type: str) -> str:
        """Extract filesystem from firmware"""
        logger.info(f"  Extracting {fs_type} filesystem...")
        
        extraction_path = os.path.join(
            self.output_dir,
            f"extracted_{os.path.basename(filepath)}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        os.makedirs(extraction_path, exist_ok=True)
        
        if fs_type == 'squashfs' and self.sasquatch_available:
            # Use sasquatch for better extraction
            try:
                subprocess.run(
                    ['sasquatch', '-d', extraction_path, filepath],
                    capture_output=True,
                    timeout=60
                )
                logger.info(f"  ✅ Extracted to {extraction_path}")
                return extraction_path
            except:
                pass
        
        if self.binwalk_available:
            # Use binwalk
            try:
                subprocess.run(
                    ['binwalk', '-e', '-M', filepath],
                    capture_output=True,
                    cwd=self.output_dir,
                    timeout=120
                )
                
                # Find extracted directory
                for item in os.listdir(self.output_dir):
                    if item.startswith('_'):
                        extraction_path = os.path.join(self.output_dir, item)
                        break
                
                logger.info(f"  ✅ Extracted to {extraction_path}")
                return extraction_path
                
            except Exception as e:
                logger.error(f"  ❌ Extraction failed: {e}")
        
        # Fallback: manual extraction (limited)
        logger.warning("  ⚠️  Using manual extraction (limited)")
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            # Look for strings
            strings_path = os.path.join(extraction_path, 'strings.txt')
            strings = re.findall(b'[\\x20-\\x7e]{4,}', data)
            
            with open(strings_path, 'wb') as f:
                f.write(b'\n'.join(strings))
            
            logger.info(f"  ✅ Extracted strings to {strings_path}")
            
        except Exception as e:
            logger.error(f"  ❌ Manual extraction failed: {e}")
        
        return extraction_path
    
    def _analyze_extracted_files(self, extraction_path: str) -> List[ExtractedFile]:
        """Analyze extracted files"""
        logger.debug("  Analyzing extracted files...")
        
        files = []
        
        if not os.path.exists(extraction_path):
            return files
        
        for root, dirs, filenames in os.walk(extraction_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, extraction_path)
                
                try:
                    size = os.path.getsize(filepath)
                    file_type = self._detect_file_type(filepath)
                    is_exec = os.access(filepath, os.X_OK)
                    is_config = any(x in filename.lower() for x in ['.conf', '.config', '.cfg', '.ini', '.xml', '.json'])
                    
                    extracted_file = ExtractedFile(
                        path=rel_path,
                        size=size,
                        file_type=file_type,
                        is_executable=is_exec,
                        is_config=is_config
                    )
                    
                    files.append(extracted_file)
                    
                except Exception as e:
                    logger.debug(f"  Error analyzing {filename}: {e}")
        
        logger.debug(f"  Analyzed {len(files)} files")
        return files
    
    def _detect_file_type(self, filepath: str) -> str:
        """Detect file type"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(512)
            
            if header.startswith(b'\x7fELF'):
                return 'ELF binary'
            elif header.startswith(b'#!/'):
                return 'Script'
            elif b'<?xml' in header:
                return 'XML'
            elif b'{' in header and b'}' in header:
                return 'JSON'
            else:
                # Check extension
                ext = os.path.splitext(filepath)[1].lower()
                if ext in ['.txt', '.log']:
                    return 'Text'
                elif ext in ['.sh', '.bash']:
                    return 'Shell script'
                elif ext in ['.py', '.pl', '.rb']:
                    return 'Script'
                else:
                    return 'Unknown'
                    
        except:
            return 'Unknown'
    
    def _find_credentials(self, extraction_path: str) -> List[Credential]:
        """Find hardcoded credentials in extracted files"""
        logger.info("  🔍 Searching for credentials...")
        
        credentials = []
        
        if not os.path.exists(extraction_path):
            return credentials
        
        for root, dirs, filenames in os.walk(extraction_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    
                    # Skip binary files (except scripts)
                    if b'\x00' in content[:1024]:
                        continue
                    
                    # Decode content
                    try:
                        text = content.decode('utf-8', errors='ignore')
                    except:
                        continue
                    
                    # Search for credentials
                    for pattern, cred_type in self.CREDENTIAL_PATTERNS:
                        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                        
                        for match in matches:
                            value = match.group(1) if match.lastindex else match.group(0)
                            
                            # Skip common false positives
                            if value.lower() in ['example', 'changeme', 'your_password', 'xxx']:
                                continue
                            
                            rel_path = os.path.relpath(filepath, extraction_path)
                            line_num = text[:match.start()].count('\n') + 1
                            
                            # Determine severity
                            severity = 'medium'
                            if cred_type in ['private_key', 'aws_secret']:
                                severity = 'critical'
                            elif cred_type in ['api_key', 'token']:
                                severity = 'high'
                            
                            credential = Credential(
                                type=cred_type,
                                value=value,
                                context=text[max(0, match.start()-50):match.end()+50],
                                file_path=rel_path,
                                line_number=line_num,
                                severity=severity
                            )
                            
                            credentials.append(credential)
                            logger.debug(f"  🔑 Found {cred_type} in {rel_path}:{line_num}")
                            
                except Exception as e:
                    logger.debug(f"  Error scanning {filename}: {e}")
        
        logger.info(f"  Found {len(credentials)} credentials")
        return credentials
    
    def _detect_backdoors(self, extraction_path: str) -> List[Backdoor]:
        """Detect backdoors in extracted files"""
        logger.info("  🚪 Scanning for backdoors...")
        
        backdoors = []
        
        if not os.path.exists(extraction_path):
            return backdoors
        
        for root, dirs, filenames in os.walk(extraction_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    
                    try:
                        text = content.decode('utf-8', errors='ignore')
                    except:
                        continue
                    
                    # Search for backdoor signatures
                    for pattern, bd_type, description in self.BACKDOOR_SIGNATURES:
                        matches = re.finditer(pattern, text, re.IGNORECASE)
                        
                        for match in matches:
                            rel_path = os.path.relpath(filepath, extraction_path)
                            
                            backdoor = Backdoor(
                                type=bd_type,
                                description=description,
                                file_path=rel_path,
                                severity='critical' if bd_type == 'backdoor' else 'high',
                                evidence=match.group(0)
                            )
                            
                            backdoors.append(backdoor)
                            logger.warning(f"  🚪 Backdoor found: {description} in {rel_path}")
                            
                except Exception as e:
                    logger.debug(f"  Error scanning {filename}: {e}")
        
        logger.info(f"  Found {len(backdoors)} backdoors")
        return backdoors
    
    def _scan_vulnerabilities(self, extraction_path: str) -> List[Vulnerability]:
        """Scan for known vulnerabilities"""
        logger.info("  ⚠️  Scanning for vulnerabilities...")
        
        vulnerabilities = []
        
        if not os.path.exists(extraction_path):
            return vulnerabilities
        
        for root, dirs, filenames in os.walk(extraction_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    
                    try:
                        text = content.decode('utf-8', errors='ignore')
                    except:
                        continue
                    
                    # Check for CVE patterns
                    for cve_id, pattern in self.CVE_PATTERNS.items():
                        if re.search(pattern, text, re.IGNORECASE):
                            rel_path = os.path.relpath(filepath, extraction_path)
                            
                            vuln = Vulnerability(
                                cve_id=cve_id,
                                description=f"Known vulnerability {cve_id} detected",
                                severity='critical',
                                cvss_score=9.0,
                                file_path=rel_path,
                                affected_component=filename
                            )
                            
                            vulnerabilities.append(vuln)
                            logger.warning(f"  ⚠️  CVE found: {cve_id} in {rel_path}")
                            
                except Exception as e:
                    logger.debug(f"  Error scanning {filename}: {e}")
        
        logger.info(f"  Found {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities
    
    def _calculate_risk_score(self, credentials: List[Credential],
                               backdoors: List[Backdoor],
                               vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk score (0-10)"""
        score = 0.0
        
        # Credentials
        for cred in credentials:
            if cred.severity == 'critical':
                score += 2.0
            elif cred.severity == 'high':
                score += 1.5
            else:
                score += 0.5
        
        # Backdoors
        for backdoor in backdoors:
            if backdoor.severity == 'critical':
                score += 3.0
            else:
                score += 1.5
        
        # Vulnerabilities
        for vuln in vulnerabilities:
            if vuln.severity == 'critical':
                score += 2.5
            elif vuln.severity == 'high':
                score += 1.5
            else:
                score += 0.5
        
        return min(10.0, score)
    
    def generate_report(self, result: FirmwareAnalysisResult,
                        output_format: str = 'text') -> str:
        """
        Generate analysis report
        
        Args:
            result: Analysis result
            output_format: 'text', 'json', 'html'
            
        Returns:
            Formatted report
        """
        logger.info("📊 Generating report...")
        
        if output_format == 'json':
            return json.dumps(result.to_dict(), indent=2, default=str)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("💾 FIRMWARE SECURITY ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Firmware: {result.firmware.filename}")
        report.append(f"Vendor: {result.firmware.vendor}")
        report.append(f"Model: {result.firmware.model}")
        report.append(f"Version: {result.firmware.version}")
        report.append(f"Size: {result.firmware.size_bytes:,} bytes")
        report.append(f"MD5: {result.firmware.md5}")
        report.append(f"SHA256: {result.firmware.sha256}")
        report.append(f"Filesystem: {result.firmware.filesystem_type}")
        report.append(f"Analysis Time: {result.analysis_time_seconds:.2f}s")
        report.append("")
        
        report.append("RISK ASSESSMENT:")
        report.append("-" * 70)
        report.append(f"Risk Score: {result.risk_score}/10.0")
        
        if result.risk_score >= 8.0:
            report.append("⚠️  CRITICAL: Severe security issues detected!")
        elif result.risk_score >= 5.0:
            report.append("⚠️  HIGH: Significant security issues detected!")
        elif result.risk_score >= 2.0:
            report.append("⚠️  MEDIUM: Some security issues detected!")
        else:
            report.append("✅ LOW: No major issues detected")
        
        report.append("")
        report.append("SUMMARY:")
        report.append("-" * 70)
        report.append(f"Files Extracted: {len(result.extracted_files)}")
        report.append(f"Credentials Found: {len(result.credentials)}")
        report.append(f"Backdoors Found: {len(result.backdoors)}")
        report.append(f"Vulnerabilities: {len(result.vulnerabilities)}")
        
        if result.credentials:
            report.append("")
            report.append("CREDENTIALS FOUND:")
            report.append("-" * 70)
            for cred in result.credentials[:10]:
                report.append(f"  [{cred.severity.upper()}] {cred.type}: {cred.value[:40]}")
                report.append(f"    Location: {cred.file_path}:{cred.line_number}")
            if len(result.credentials) > 10:
                report.append(f"  ... and {len(result.credentials) - 10} more")
        
        if result.backdoors:
            report.append("")
            report.append("BACKDOORS DETECTED:")
            report.append("-" * 70)
            for backdoor in result.backdoors:
                report.append(f"  [{backdoor.severity.upper()}] {backdoor.description}")
                report.append(f"    Location: {backdoor.file_path}")
        
        if result.vulnerabilities:
            report.append("")
            report.append("VULNERABILITIES:")
            report.append("-" * 70)
            for vuln in result.vulnerabilities:
                report.append(f"  {vuln.cve_id or 'Unknown'}: {vuln.description}")
                report.append(f"    CVSS: {vuln.cvss_score} ({vuln.severity.upper()})")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        report.append("1. Change all default credentials immediately")
        report.append("2. Remove or disable backdoor accounts/services")
        report.append("3. Update firmware to latest version")
        report.append("4. Implement network segmentation")
        report.append("5. Monitor device for suspicious activity")
        report.append("6. Consider replacing device if vendor doesn't support security")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
            logger.info("🧹 Cleaned up temporary files")
        except:
            pass


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     💾 KALIAGENT v4.3.0 - FIRMWARE ANALYZER                  ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python firmware_analyzer.py <firmware.bin> [output_dir]")
        print("\nOr download from device:")
        print("  python firmware_analyzer.py --download <host> <endpoint>")
        sys.exit(1)
    
    if sys.argv[1] == '--download':
        if len(sys.argv) < 4:
            print("Usage: python firmware_analyzer.py --download <host> <endpoint>")
            sys.exit(1)
        
        host = sys.argv[2]
        endpoint = sys.argv[3]
        
        analyzer = FirmwareAnalyzer()
        firmware_path = analyzer.download_from_device(host, endpoint=endpoint)
        
        if not firmware_path:
            print("❌ Download failed")
            sys.exit(1)
    else:
        firmware_path = sys.argv[1]
    
    if not os.path.exists(firmware_path):
        print(f"❌ File not found: {firmware_path}")
        sys.exit(1)
    
    # Analyze firmware
    analyzer = FirmwareAnalyzer()
    result = analyzer.analyze_firmware(firmware_path)
    
    # Generate report
    report = analyzer.generate_report(result)
    print("\n" + report)
    
    # Save report
    report_file = f"firmware_report_{os.path.basename(firmware_path)}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_file}")
    
    # Save JSON
    json_file = f"firmware_report_{os.path.basename(firmware_path)}.json"
    with open(json_file, 'w') as f:
        f.write(analyzer.generate_report(result, output_format='json'))
    
    print(f"✅ JSON saved to: {json_file}")
    
    # Cleanup
    analyzer.cleanup()


if __name__ == "__main__":
    main()
