#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 6: LLM Integration
AI-powered attack planning, natural language commands, and auto-reporting
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class LLMIntegration:
    """Local LLM integration via Ollama for attack planning and reporting"""
    
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "qwen3.5:cloud"):
        self.ollama_host = ollama_host
        self.model = model
        self.session_context = []
    
    def generate(self, prompt: str, system: str = None, stream: bool = False) -> str:
        """Generate text using local Ollama LLM"""
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.extend(self.session_context)
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # Store in context
            assistant_message = result.get("message", {}).get("content", "")
            self.session_context.append({"role": "user", "content": prompt})
            self.session_context.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            return f"LLM Error: {str(e)}"
    
    def analyze_nmap(self, nmap_output: str) -> Dict:
        """Analyze Nmap scan results and recommend attack vectors"""
        system_prompt = """You are a cybersecurity expert analyzing Nmap scan results.
Provide:
1. Target summary (OS, services, open ports)
2. Vulnerability assessment (potential weaknesses)
3. Recommended attack vectors (prioritized by likelihood of success)
4. Specific tools/commands to use
5. Risk level (Low/Medium/High/Critical)

Be concise and actionable. Format as JSON."""
        
        response = self.generate(nmap_output, system=system_prompt)
        
        # Try to parse as JSON
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {"analysis": response, "format": "text"}
    
    def plan_attack(self, target_info: Dict, goal: str) -> Dict:
        """Generate an attack plan based on target intelligence"""
        system_prompt = """You are a red team operator planning an attack.
Create a step-by-step attack plan including:
1. Reconnaissance steps
2. Initial exploitation method
3. Post-exploitation actions
4. Persistence mechanisms
5. Lateral movement opportunities
6. Evidence collection

Format as JSON with fields: plan_name, steps (array), estimated_time, risk_level, tools_required."""
        
        prompt = f"""Target Intelligence:
{json.dumps(target_info, indent=2)}

Attack Goal: {goal}

Generate a complete attack plan."""
        
        response = self.generate(prompt, system=system_prompt)
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {"plan": response, "format": "text"}
    
    def generate_report(self, attack_results: Dict, report_type: str = "pentest") -> str:
        """Generate professional penetration test report"""
        system_prompt = f"""You are a professional penetration tester writing a client report.
Report Type: {report_type}

Include:
1. Executive Summary (non-technical, risk-focused)
2. Scope of Engagement
3. Methodology
4. Findings (with CVSS scores where applicable)
5. Evidence (reference screenshots/logs)
6. Remediation Recommendations
7. Conclusion

Use professional language. Format with markdown headers."""
        
        prompt = f"""Attack Results:
{json.dumps(attack_results, indent=2)}

Generate a complete {report_type} report."""
        
        return self.generate(prompt, system=system_prompt)
    
    def chat(self, message: str, context: str = None) -> str:
        """Chat interface for attack assistance"""
        system_prompt = """You are a cybersecurity assistant helping a penetration tester.
Provide helpful, accurate information about:
- Exploitation techniques
- Tool usage (Nmap, Metasploit, Burp, etc.)
- Vulnerability analysis
- Post-exploitation strategies
- Report writing

Always emphasize: ONLY test systems you own or have written permission to test.
Be concise and practical."""
        
        if context:
            full_message = f"Context: {context}\n\nQuestion: {message}"
        else:
            full_message = message
        
        return self.generate(full_message, system=system_prompt)
    
    def clear_context(self):
        """Clear session context"""
        self.session_context = []


class NaturalLanguageCommand:
    """Parse natural language commands into KaliAgent actions"""
    
    def __init__(self, llm: LLMIntegration):
        self.llm = llm
    
    def parse(self, command: str) -> Dict:
        """Convert natural language to structured command"""
        system_prompt = """You are a command parser for a penetration testing tool.
Convert natural language requests into structured JSON commands.

Supported command types:
- scan: {type: "scan", target: "IP/CIDR", scan_type: "nmap|nikto|sqlmap"}
- attack: {type: "attack", target: "IP", attack_type: "web|wifi|network", method: "specific method"}
- exploit: {type: "exploit", target: "IP", cve: "CVE-XXXX-XXXX"}
- report: {type: "report", format: "pdf|html", scope: "description"}
- status: {type: "status"}

Return ONLY valid JSON with no explanation."""
        
        response = self.llm.generate(command, system=system_prompt)
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {"error": "Could not parse command", "original": command}


# Example usage
if __name__ == "__main__":
    llm = LLMIntegration()
    
    # Test Nmap analysis
    nmap_sample = """
    Starting Nmap 7.94
    Nmap scan report for 10.0.100.10
    Host is up (0.0023s latency).
    Not shown: 997 closed ports
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.2p1
    80/tcp open  http    Apache httpd 2.4.18
    443/tcp open  ssl/http Apache httpd 2.4.18
    """
    
    print("🔍 Analyzing Nmap scan...")
    analysis = llm.analyze_nmap(nmap_sample)
    print(json.dumps(analysis, indent=2))
    
    # Test attack planning
    print("\n📋 Generating attack plan...")
    target_info = {
        "ip": "10.0.100.10",
        "os": "Ubuntu 16.04",
        "services": ["ssh", "http", "https"],
        "vulnerabilities": ["Apache 2.4.18 (outdated)"]
    }
    plan = llm.plan_attack(target_info, "Gain initial access and establish persistence")
    print(json.dumps(plan, indent=2))
    
    # Test natural language parsing
    print("\n🗣️ Parsing natural language command...")
    nl_cmd = NaturalLanguageCommand(llm)
    parsed = nl_cmd.parse("Scan the 10.0.100.0/24 network for web servers and check for SQL injection")
    print(json.dumps(parsed, indent=2))
