#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 6 Orchestrator
Main entry point for AI + Polish phase
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_integration import LLMIntegration, NaturalLanguageCommand
from report_generator import ReportGenerator
from demo_video_generator import DemoVideoGenerator

class Phase6Orchestrator:
    """Orchestrate all Phase 6 components"""
    
    def __init__(self):
        self.llm = LLMIntegration()
        self.report_gen = ReportGenerator()
        self.video_gen = DemoVideoGenerator()
        self.nl_command = NaturalLanguageCommand(self.llm)
    
    def chat(self, message: str) -> str:
        """Chat with AI assistant"""
        return self.llm.chat(message)
    
    def analyze_target(self, target_ip: str) -> dict:
        """Analyze a target and get AI recommendations"""
        # In production, this would run actual scans
        sample_nmap = f"""
        Nmap scan report for {target_ip}
        Host is up (0.0023s latency).
        PORT   STATE SERVICE VERSION
        22/tcp open  ssh     OpenSSH 7.2p1
        80/tcp open  http    Apache httpd 2.4.18
        443/tcp open  ssl/http Apache httpd 2.4.18
        """
        return self.llm.analyze_nmap(sample_nmap)
    
    def generate_report(self, attack_results: dict, format: str = 'all') -> dict:
        """Generate professional report"""
        if format == 'all':
            return self.report_gen.generate_all(attack_results)
        elif format == 'pdf':
            return {'pdf': self.report_gen.generate_pdf(attack_results)}
        elif format == 'html':
            return {'html': self.report_gen.generate_html(attack_results)}
        elif format == 'json':
            return {'json': self.report_gen.generate_json(attack_results)}
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def create_demo_video(self) -> str:
        """Generate demo video"""
        return self.video_gen.generate_full_demo()
    
    def parse_command(self, natural_language: str) -> dict:
        """Parse natural language command"""
        return self.nl_command.parse(naturalatural_language)
    
    def run_demo(self):
        """Run complete Phase 6 demonstration"""
        print("🍀 KALIAGENT V4 - PHASE 6 DEMONSTRATION")
        print("=" * 60)
        
        # Demo 1: LLM Analysis
        print("\n[1/4] AI Target Analysis...")
        analysis = self.analyze_target("10.0.100.10")
        print(f"✅ Analysis complete: {len(str(analysis))} bytes")
        
        # Demo 2: Report Generation
        print("\n[2/4] Generating Professional Report...")
        sample_results = {
            'client': 'Internal Assessment',
            'date': '2026-04-24',
            'report_id': 'KA-V4-2026-001',
            'executive_summary': 'Penetration test identified 5 vulnerabilities. Critical findings include outdated web server software and weak authentication.',
            'methodology': 'OSSTMM-compliant penetration testing.',
            'findings': [
                {
                    'title': 'SQL Injection in Login Form',
                    'severity': 'Critical',
                    'cvss': 9.8,
                    'description': 'Authentication bypass via SQL injection.',
                    'evidence': "Payload: admin'-- successfully bypassed login",
                    'remediation': 'Implement parameterized queries.'
                },
                {
                    'title': 'Outdated Apache Web Server',
                    'severity': 'High',
                    'cvss': 7.5,
                    'description': 'Apache 2.4.18 contains multiple CVEs.',
                    'evidence': 'Nmap confirmed Apache/2.4.18 on ports 80/443',
                    'remediation': 'Upgrade to latest version.'
                }
            ],
            'conclusion': 'Significant security gaps require immediate attention.'
        }
        
        reports = self.generate_report(sample_results, 'all')
        print(f"✅ PDF: {reports.get('pdf', 'N/A')}")
        print(f"✅ HTML: {reports.get('html', 'N/A')}")
        print(f"✅ JSON: {reports.get('json', 'N/A')}")
        
        # Demo 3: Natural Language Command
        print("\n[3/4] Natural Language Command Parsing...")
        command = "Scan the 10.0.100.0/24 network for web servers and check for SQL injection vulnerabilities"
        parsed = self.parse_command(command)
        print(f"✅ Parsed: {parsed}")
        
        # Demo 4: Video Generator (script only)
        print("\n[4/4] Demo Video Generator...")
        script = self.video_gen.generate_script()
        print(f"✅ Script generated ({len(script)} bytes)")
        print("   (Video recording requires manual demo + ffmpeg)")
        
        print("\n" + "=" * 60)
        print("✅ PHASE 6 DEMONSTRATION COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    orchestrator = Phase6Orchestrator()
    orchestrator.run_demo()
