#!/usr/bin/env python3
"""
📡 KaliAgent v4.3.0 - Phase 9: IoT Exploitation
MQTT Protocol Client & Security Testing

Tests MQTT brokers for security vulnerabilities including:
- Anonymous access
- Topic enumeration
- Credential harvesting
- Unauthorized publish/subscribe
- MQTT-SN testing

Author: KaliAgent Team
Started: April 27, 2026
Status: Alpha (0.1.0)
"""

import logging
import socket
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MQTTClient')

# Try to import paho-mqtt, fall back to socket-based implementation
try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False
    logger.warning("paho-mqtt not installed, using socket-based implementation")
    logger.warning("Install with: pip install paho-mqtt")


@dataclass
class MQTTTopic:
    """Represents an MQTT topic"""
    name: str
    messages: List[str] = field(default_factory=list)
    message_count: int = 0
    last_message: str = ""
    last_seen: datetime = None
    sensitive: bool = False
    credentials_found: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'message_count': self.message_count,
            'last_message': self.last_message,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'sensitive': self.sensitive,
            'credentials_found': self.credentials_found
        }


@dataclass
class MQTTBroker:
    """Represents an MQTT broker"""
    host: str
    port: int = 1883
    ssl_port: int = 8883
    anonymous_access: bool = False
    topics: List[MQTTTopic] = field(default_factory=list)
    credentials_harvested: List[Dict] = field(default_factory=list)
    vulnerabilities: List[Dict] = field(default_factory=list)
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'anonymous_access': self.anonymous_access,
            'topic_count': len(self.topics),
            'credentials_harvested': len(self.credentials_harvested),
            'vulnerabilities': self.vulnerabilities,
            'risk_score': self.risk_score
        }


class MQTTClient:
    """
    MQTT Security Testing Client
    
    Capabilities:
    - Broker discovery
    - Anonymous access testing
    - Topic enumeration
    - Message interception
    - Credential harvesting
    - Unauthorized publish testing
    - Security assessment
    """
    
    VERSION = "0.1.0"
    
    # Common MQTT topics to check
    COMMON_TOPICS = [
        '#',  # All topics (wildcard)
        '+/+/+/+/+',  # Multi-level wildcard test
        'home/#',
        'home/+/+',
        'iot/#',
        'device/#',
        'sensor/#',
        'test/#',
        'system/#',
        'config/#',
        'command/#',
        'status/#',
        'data/#',
        'telemetry/#',
        'events/#',
        'alerts/#',
        'notifications/#',
        'logs/#',
        'debug/#',
        'admin/#',
        'control/#',
        'set/#',
        'get/#',
    ]
    
    # Sensitive topic patterns
    SENSITIVE_PATTERNS = [
        'password',
        'passwd',
        'pwd',
        'secret',
        'token',
        'api_key',
        'apikey',
        'auth',
        'credential',
        'login',
        'username',
        'user',
        'admin',
        'config',
        'private',
        'secure',
        'key',
        'cert',
        'certificate',
    ]
    
    def __init__(self, host: str, port: int = 1883, timeout: int = 5, verbose: bool = True):
        """
        Initialize MQTT Client
        
        Args:
            host: Broker hostname or IP
            port: Broker port (default: 1883)
            timeout: Connection timeout in seconds
            verbose: Enable verbose logging
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        self.broker = MQTTBroker(host=host, port=port)
        self.client = None
        self.connected = False
        self.messages_received = []
        self.topics_discovered = {}
        
        logger.info(f"📡 MQTT Client v{self.VERSION} initialized")
        logger.info(f"🎯 Target: {host}:{port}")
    
    def connect(self, username: str = None, password: str = None, 
                client_id: str = None, anonymous: bool = False) -> bool:
        """
        Connect to MQTT broker
        
        Args:
            username: Optional username
            password: Optional password
            client_id: Client identifier
            anonymous: Try anonymous connection
            
        Returns:
            True if connection successful
        """
        logger.info(f"🔌 Connecting to {self.host}:{self.port}...")
        
        if PAHO_AVAILABLE:
            return self._connect_paho(username, password, client_id, anonymous)
        else:
            return self._connect_socket()
    
    def _connect_paho(self, username: str = None, password: str = None,
                      client_id: str = None, anonymous: bool = False) -> bool:
        """Connect using paho-mqtt library"""
        try:
            client_id = client_id or f"kaliagent_mqtt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.client = mqtt.Client(client_id=client_id, clean_session=True)
            
            if username and password:
                self.client.username_pw_set(username, password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            
            # Connect
            result = self.client.connect(self.host, self.port, self.timeout)
            
            if result == 0:
                self.client.loop_start()
                self.connected = True
                logger.info(f"✅ Connected to broker")
                
                if anonymous:
                    self.broker.anonymous_access = True
                    logger.warning("⚠️  ANONYMOUS ACCESS ALLOWED!")
                
                return True
            else:
                logger.error(f"❌ Connection failed with code: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def _connect_socket(self) -> bool:
        """Connect using raw socket (fallback)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            
            # Send MQTT CONNECT packet (minimal)
            connect_packet = bytes([
                0x10, 0x12,  # Fixed header
                0x00, 0x04, ord('M'), ord('Q'), ord('T'), ord('T'),  # Protocol name
                0x04,  # Protocol level (3.1.1)
                0x02,  # Connect flags
                0x00, 0x3C,  # Keepalive
                0x00, 0x00,  # Client ID length (empty)
            ])
            
            sock.send(connect_packet)
            
            # Check for CONNACK
            response = sock.recv(4)
            if len(response) >= 4 and response[0] == 0x20:
                self.connected = True
                logger.info(f"✅ Connected to broker (socket mode)")
                self.broker.anonymous_access = True
                logger.warning("⚠️  ANONYMOUS ACCESS ALLOWED!")
                sock.close()
                return True
            
            sock.close()
            return False
            
        except Exception as e:
            logger.error(f"❌ Socket connection error: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """paho-mqtt connect callback"""
        if rc == 0:
            logger.info("✅ Connected to broker")
            self.connected = True
        else:
            logger.error(f"❌ Connection failed with code: {rc}")
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """paho-mqtt message callback"""
        try:
            payload = msg.payload.decode('utf-8', errors='ignore')
            topic = msg.topic
            
            logger.debug(f"📨 [{topic}]: {payload[:100]}")
            
            self.messages_received.append({
                'topic': topic,
                'payload': payload,
                'timestamp': datetime.now()
            })
            
            # Track topics
            if topic not in self.topics_discovered:
                self.topics_discovered[topic] = MQTTTopic(name=topic)
            
            self.topics_discovered[topic].messages.append(payload)
            self.topics_discovered[topic].message_count += 1
            self.topics_discovered[topic].last_message = payload
            self.topics_discovered[topic].last_seen = datetime.now()
            
            # Check for sensitive data
            self._check_sensitive_data(topic, payload)
            
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
    
    def _check_sensitive_data(self, topic: str, payload: str):
        """Check for sensitive data in topic or payload"""
        combined = f"{topic} {payload}".lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in combined:
                logger.warning(f"⚠️  SENSITIVE DATA in {topic}: {payload[:50]}")
                
                if topic not in self.topics_discovered:
                    self.topics_discovered[topic] = MQTTTopic(name=topic)
                
                self.topics_discovered[topic].sensitive = True
                
                # Check for credentials
                if any(x in combined for x in ['password', 'passwd', 'pwd', 'secret', 'token', 'api_key']):
                    self.topics_discovered[topic].credentials_found = True
                    self.broker.credentials_harvested.append({
                        'topic': topic,
                        'data': payload,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.critical(f"🔑 CREDENTIALS FOUND in {topic}!")
                break
    
    def connect_anonymous(self) -> bool:
        """Test anonymous connection"""
        logger.info("🔓 Testing anonymous access...")
        return self.connect(anonymous=True)
    
    def list_topics(self, wildcard: str = '#', timeout: int = 5) -> List[str]:
        """
        List topics by subscribing to wildcard
        
        Args:
            wildcard: Topic wildcard (default: '#' for all)
            timeout: How long to listen
            
        Returns:
            List of discovered topics
        """
        logger.info(f"🔍 Enumerating topics with wildcard: {wildcard}...")
        
        if not self.connected:
            if not self.connect_anonymous():
                return []
        
        if PAHO_AVAILABLE and self.client:
            try:
                self.client.subscribe(wildcard, qos=0)
                logger.info(f"✅ Subscribed to {wildcard}")
                
                # Listen for messages
                import time
                time.sleep(timeout)
                
                topics = list(self.topics_discovered.keys())
                logger.info(f"📊 Discovered {len(topics)} topics")
                
                return topics
                
            except Exception as e:
                logger.error(f"❌ Topic enumeration error: {e}")
                return []
        else:
            logger.error("❌ Cannot enumerate topics without paho-mqtt")
            return []
    
    def harvest_credentials(self) -> List[Dict]:
        """
        Harvest credentials from MQTT topics
        
        Returns:
            List of harvested credentials
        """
        logger.info("🔑 Harvesting credentials...")
        
        if not self.connected:
            if not self.connect_anonymous():
                return []
        
        # Subscribe to common sensitive topics
        sensitive_topics = [
            'admin/#',
            'config/#',
            'credentials/#',
            'auth/#',
            'login/#',
            'password/#',
            'secret/#',
            'token/#',
            'api/#',
            'system/#',
        ]
        
        if PAHO_AVAILABLE and self.client:
            try:
                for topic in sensitive_topics:
                    self.client.subscribe(topic, qos=0)
                
                logger.info(f"✅ Subscribed to {len(sensitive_topics)} sensitive topics")
                
                # Listen for 10 seconds
                import time
                time.sleep(10)
                
                credentials = self.broker.credentials_harvested
                logger.info(f"🔑 Harvested {len(credentials)} credentials")
                
                return credentials
                
            except Exception as e:
                logger.error(f"❌ Credential harvesting error: {e}")
                return []
        else:
            logger.error("❌ Cannot harvest credentials without paho-mqtt")
            return []
    
    def test_publish(self, topic: str = 'test/kaliagent', 
                     payload: str = 'KaliAgent MQTT Test') -> bool:
        """
        Test unauthorized publish
        
        Args:
            topic: Topic to publish to
            payload: Message payload
            
        Returns:
            True if publish successful
        """
        logger.info(f"📤 Testing publish to {topic}...")
        
        if not self.connected:
            if not self.connect_anonymous():
                return False
        
        if PAHO_AVAILABLE and self.client:
            try:
                result = self.client.publish(topic, payload)
                result.wait_for_publish()
                
                if result.rc == 0:
                    logger.warning(f"⚠️  UNAUTHORIZED PUBLISH SUCCESSFUL!")
                    self.broker.vulnerabilities.append({
                        'type': 'unauthorized_publish',
                        'topic': topic,
                        'severity': 'high',
                        'cvss': 7.5,
                        'description': f'Anonymous publish allowed to {topic}'
                    })
                    return True
                else:
                    logger.info(f"ℹ️  Publish rejected")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Publish error: {e}")
                return False
        else:
            logger.error("❌ Cannot test publish without paho-mqtt")
            return False
    
    def calculate_risk_score(self) -> float:
        """
        Calculate broker risk score (0-10)
        
        Returns:
            Risk score
        """
        score = 5.0  # Base score
        
        # Anonymous access
        if self.broker.anonymous_access:
            score += 2.0
        
        # Credentials harvested
        if self.broker.credentials_harvested:
            score += min(2.0, len(self.broker.credentials_harvested) * 0.5)
        
        # Unauthorized publish
        for vuln in self.broker.vulnerabilities:
            if vuln.get('type') == 'unauthorized_publish':
                score += 1.0
        
        # Many topics discovered
        if len(self.broker.topics) > 10:
            score += 0.5
        
        self.broker.risk_score = min(10.0, score)
        return self.broker.risk_score
    
    def generate_report(self, output_format: str = 'text') -> str:
        """
        Generate MQTT security assessment report
        
        Args:
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report
        """
        logger.info("📊 Generating report...")
        
        self.calculate_risk_score()
        self.broker.topics = list(self.topics_discovered.values())
        
        if output_format == 'json':
            return json.dumps(self.broker.to_dict(), indent=2, default=str)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("📡 MQTT SECURITY ASSESSMENT REPORT")
        report.append("=" * 70)
        report.append(f"Broker: {self.broker.host}:{self.broker.port}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Risk Score: {self.broker.risk_score}/10.0")
        report.append("")
        
        report.append("FINDINGS:")
        report.append("-" * 70)
        
        if self.broker.anonymous_access:
            report.append("⚠️  CRITICAL: Anonymous access allowed!")
        
        if self.broker.credentials_harvested:
            report.append(f"🔑 CRITICAL: {len(self.broker.credentials_harvested)} credentials harvested!")
            for cred in self.broker.credentials_harvested[:5]:
                report.append(f"   - {cred['topic']}: {cred['data'][:50]}")
        
        for vuln in self.broker.vulnerabilities:
            report.append(f"⚠️  {vuln['severity'].upper()}: {vuln['description']}")
        
        report.append("")
        report.append("TOPICS DISCOVERED:")
        report.append("-" * 70)
        for topic in list(self.topics_discovered.values())[:20]:
            report.append(f"  {topic.name} ({topic.message_count} messages)")
        
        if len(self.topics_discovered) > 20:
            report.append(f"  ... and {len(self.topics_discovered) - 20} more")
        
        report.append("")
        report.append("RECOMMENDATIONS:")
        report.append("-" * 70)
        report.append("1. Enable authentication (username/password)")
        report.append("2. Implement TLS/SSL encryption")
        report.append("3. Configure ACLs for topic access")
        report.append("4. Disable anonymous access")
        report.append("5. Monitor and log all connections")
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_assessment(self) -> str:
        """
        Run complete MQTT security assessment
        
        Returns:
            Assessment report
        """
        logger.info("🚀 Starting MQTT security assessment...")
        
        # Step 1: Test anonymous access
        if self.connect_anonymous():
            logger.info("✅ Anonymous access successful")
            
            # Step 2: List topics
            topics = self.list_topics(timeout=5)
            
            # Step 3: Harvest credentials
            creds = self.harvest_credentials()
            
            # Step 4: Test publish
            self.test_publish()
        else:
            logger.info("ℹ️  Anonymous access denied")
            self.broker.vulnerabilities.append({
                'type': 'auth_required',
                'severity': 'info',
                'description': 'Authentication required (good practice)'
            })
        
        # Generate report
        report = self.generate_report()
        
        logger.info("✅ Assessment complete!")
        return report
    
    def disconnect(self):
        """Disconnect from broker"""
        if PAHO_AVAILABLE and self.client:
            self.client.loop_stop()
            self.client.disconnect()
        
        self.connected = False
        logger.info("🔌 Disconnected from broker")


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📡 KALIAGENT v4.3.0 - MQTT SECURITY TESTER               ║
║                    Phase 9: Alpha 0.1.0                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
    
    # Initialize client
    mqtt_client = MQTTClient(host=host, port=port, verbose=True)
    
    # Run assessment
    report = mqtt_client.run_assessment()
    
    # Print report
    print("\n" + report)
    
    # Save to file
    with open(f'mqtt_assessment_{host.replace(".", "_")}.txt', 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: mqtt_assessment_{host.replace('.', '_')}.txt")
    
    # Cleanup
    mqtt_client.disconnect()


if __name__ == "__main__":
    main()
