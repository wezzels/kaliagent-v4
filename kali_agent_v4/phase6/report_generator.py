#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 6: Professional Reporting
Generate client-ready PDF/HTML/DOCX penetration test reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas


class ReportGenerator:
    """Generate professional penetration test reports in multiple formats"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for reports"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#0f3460'),
            spaceAfter=6,
            spaceBefore=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=8,
            textColor=colors.HexColor('#e94560'),
            backColor=colors.HexColor('#f5f5f5'),
            borderWidth=1,
            borderColor=colors.HexColor('#cccccc'),
            spaceAfter=12
        ))
    
    def generate_pdf(self, report_data: Dict, filename: str = None) -> str:
        """Generate PDF report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pentest_report_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title Page
        story.append(Paragraph("PENETRATION TEST REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Client: {report_data.get('client', 'Internal Assessment')}", self.styles['Heading3']))
        story.append(Paragraph(f"Date: {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}", self.styles['Heading3']))
        story.append(Paragraph(f"Report ID: {report_data.get('report_id', 'N/A')}", self.styles['Heading3']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        executive_summary = report_data.get('executive_summary', 'No executive summary provided.')
        story.append(Paragraph(executive_summary, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Risk Summary Table
        story.append(Paragraph("RISK SUMMARY", self.styles['SectionHeader']))
        findings = report_data.get('findings', [])
        
        # Count by severity
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}
        for finding in findings:
            severity = finding.get('severity', 'Info')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        risk_data = [
            ['Severity', 'Count', 'Color'],
            ['Critical', str(severity_counts['Critical']), 'Critical'],
            ['High', str(severity_counts['High']), 'High'],
            ['Medium', str(severity_counts['Medium']), 'Medium'],
            ['Low', str(severity_counts['Low']), 'Low'],
            ['Informational', str(severity_counts['Info']), 'Info']
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(risk_table)
        story.append(PageBreak())
        
        # Methodology
        story.append(Paragraph("METHODOLOGY", self.styles['SectionHeader']))
        methodology = report_data.get('methodology', 'Standard penetration testing methodology was followed.')
        story.append(Paragraph(methodology, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Findings
        story.append(Paragraph("DETAILED FINDINGS", self.styles['SectionHeader']))
        
        for i, finding in enumerate(findings, 1):
            story.append(Paragraph(f"Finding #{i}: {finding.get('title', 'Unknown')}", self.styles['SubsectionHeader']))
            
            # Severity badge
            severity = finding.get('severity', 'Info')
            severity_color = {
                'Critical': '#e94560',
                'High': '#ff6b6b',
                'Medium': '#feca57',
                'Low': '#48dbfb',
                'Info': '#c8d6e5'
            }.get(severity, '#95a5a6')
            
            story.append(Paragraph(f"<b>Severity:</b> <font color='{severity_color}'>{severity}</font>", self.styles['BodyText']))
            story.append(Paragraph(f"<b>CVSS Score:</b> {finding.get('cvss', 'N/A')}", self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph("<b>Description:</b>", self.styles['SubsectionHeader']))
            story.append(Paragraph(finding.get('description', 'No description provided.'), self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph("<b>Evidence:</b>", self.styles['SubsectionHeader']))
            evidence = finding.get('evidence', 'No evidence provided.')
            story.append(Paragraph(f"<i>{evidence}</i>", self.styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph("<b>Remediation:</b>", self.styles['SubsectionHeader']))
            story.append(Paragraph(finding.get('remediation', 'No remediation provided.'), self.styles['BodyText']))
            story.append(Spacer(1, 0.3*inch))
        
        # Conclusion
        story.append(Paragraph("CONCLUSION", self.styles['SectionHeader']))
        conclusion = report_data.get('conclusion', 'Assessment complete.')
        story.append(Paragraph(conclusion, self.styles['BodyText']))
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def generate_html(self, report_data: Dict, filename: str = None) -> str:
        """Generate HTML report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pentest_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        findings = report_data.get('findings', [])
        findings_html = ""
        for i, finding in enumerate(findings, 1):
            severity = finding.get('severity', 'Info')
            severity_class = severity.lower()
            findings_html += f"""
            <div class="finding">
                <h3>Finding #{i}: {finding.get('title', 'Unknown')}</h3>
                <p><strong>Severity:</strong> <span class="severity-{severity_class}">{severity}</span></p>
                <p><strong>CVSS:</strong> {finding.get('cvss', 'N/A')}</p>
                <h4>Description</h4>
                <p>{finding.get('description', 'No description provided.')}</p>
                <h4>Evidence</h4>
                <pre>{finding.get('evidence', 'No evidence provided.')}</pre>
                <h4>Remediation</h4>
                <p>{finding.get('remediation', 'No remediation provided.')}</p>
            </div>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Penetration Test Report - {report_data.get('client', 'Internal')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a2e;
            text-align: center;
            border-bottom: 3px solid #16213e;
            padding-bottom: 20px;
        }}
        h2 {{
            color: #16213e;
            border-left: 4px solid #0f3460;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #0f3460;
        }}
        .severity-critical {{ color: #e94560; font-weight: bold; }}
        .severity-high {{ color: #ff6b6b; font-weight: bold; }}
        .severity-medium {{ color: #feca57; font-weight: bold; }}
        .severity-low {{ color: #48dbfb; font-weight: bold; }}
        .severity-info {{ color: #95a5a6; }}
        .finding {{
            background: #fafafa;
            border-left: 4px solid #0f3460;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 4px 4px 0;
        }}
        pre {{
            background: #1a1a2e;
            color: #e94560;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
        }}
        .risk-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .risk-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .risk-card.critical {{ border-top: 4px solid #e94560; }}
        .risk-card.high {{ border-top: 4px solid #ff6b6b; }}
        .risk-card.medium {{ border-top: 4px solid #feca57; }}
        .risk-card.low {{ border-top: 4px solid #48dbfb; }}
        .risk-card.info {{ border-top: 4px solid #c8d6e5; }}
        .risk-count {{
            font-size: 2em;
            font-weight: bold;
            color: #16213e;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PENETRATION TEST REPORT</h1>
        
        <p><strong>Client:</strong> {report_data.get('client', 'Internal Assessment')}</p>
        <p><strong>Date:</strong> {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}</p>
        <p><strong>Report ID:</strong> {report_data.get('report_id', 'N/A')}</p>
        
        <h2>Executive Summary</h2>
        <p>{report_data.get('executive_summary', 'No executive summary provided.')}</p>
        
        <h2>Risk Summary</h2>
        <div class="risk-summary">
            <div class="risk-card critical">
                <div class="risk-count">{sum(1 for f in findings if f.get('severity') == 'Critical')}</div>
                <div>Critical</div>
            </div>
            <div class="risk-card high">
                <div class="risk-count">{sum(1 for f in findings if f.get('severity') == 'High')}</div>
                <div>High</div>
            </div>
            <div class="risk-card medium">
                <div class="risk-count">{sum(1 for f in findings if f.get('severity') == 'Medium')}</div>
                <div>Medium</div>
            </div>
            <div class="risk-card low">
                <div class="risk-count">{sum(1 for f in findings if f.get('severity') == 'Low')}</div>
                <div>Low</div>
            </div>
            <div class="risk-card info">
                <div class="risk-count">{sum(1 for f in findings if f.get('severity') == 'Info')}</div>
                <div>Info</div>
            </div>
        </div>
        
        <h2>Methodology</h2>
        <p>{report_data.get('methodology', 'Standard penetration testing methodology was followed.')}</p>
        
        <h2>Detailed Findings</h2>
        {findings_html}
        
        <h2>Conclusion</h2>
        <p>{report_data.get('conclusion', 'Assessment complete.')}</p>
        
        <footer>
            <p>Generated by KaliAgent v4 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p><strong>CONFIDENTIAL</strong> - For authorized recipients only</p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_json(self, report_data: Dict, filename: str = None) -> str:
        """Generate JSON report (for data exchange)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pentest_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add metadata
        report_data['generated_at'] = datetime.now().isoformat()
        report_data['generator'] = 'KaliAgent v4 Report Generator'
        report_data['version'] = '1.0'
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return filepath
    
    def generate_all(self, report_data: Dict, base_filename: str = None) -> Dict[str, str]:
        """Generate all report formats"""
        return {
            'pdf': self.generate_pdf(report_data, f"{base_filename}.pdf" if base_filename else None),
            'html': self.generate_html(report_data, f"{base_filename}.html" if base_filename else None),
            'json': self.generate_json(report_data, f"{base_filename}.json" if base_filename else None)
        }


# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    
    sample_report = {
        'client': 'Internal Security Assessment',
        'date': '2026-04-24',
        'report_id': 'KA-V4-2026-001',
        'executive_summary': 'This penetration test identified 5 security vulnerabilities across the target network. Critical findings include outdated web server software and weak authentication mechanisms. Immediate remediation is recommended for high-risk findings.',
        'methodology': 'OSSTMM-compliant penetration testing methodology was followed, including reconnaissance, scanning, exploitation, and post-exploitation phases.',
        'findings': [
            {
                'title': 'Outdated Apache Web Server',
                'severity': 'High',
                'cvss': 7.5,
                'description': 'The target system is running Apache 2.4.18, which contains multiple known vulnerabilities including CVE-2016-2161 (session fixation).',
                'evidence': 'Nmap scan confirmed Apache/2.4.18 on port 80 and 443',
                'remediation': 'Upgrade Apache to the latest stable version (2.4.58 or newer) and apply all security patches.'
            },
            {
                'title': 'SQL Injection in Login Form',
                'severity': 'Critical',
                'cvss': 9.8,
                'description': 'The authentication endpoint is vulnerable to SQL injection, allowing complete bypass of authentication.',
                'evidence': "Payload: admin'-- successfully bypassed login",
                'remediation': 'Implement parameterized queries and input validation for all user-supplied data.'
            }
        ],
        'conclusion': 'The assessment revealed significant security gaps that require immediate attention. Priority should be given to patching critical and high-severity vulnerabilities.'
    }
    
    print("📄 Generating reports...")
    files = generator.generate_all(sample_report, "kaliagent_v4_demo")
    print(f"✅ PDF: {files['pdf']}")
    print(f"✅ HTML: {files['html']}")
    print(f"✅ JSON: {files['json']}")
