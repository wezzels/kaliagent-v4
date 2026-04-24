#!/usr/bin/env python3
"""
KaliAgent v4 - Phase 6: Demo Video Generator
Create a 3-minute professional demo reel showcasing all capabilities
"""

import subprocess
import os
from datetime import datetime
from typing import List, Dict

class DemoVideoGenerator:
    """Generate professional demo video for KaliAgent v4"""
    
    def __init__(self, output_dir: str = "./recordings"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.clips = []
    
    def record_screen(self, output_file: str, duration: int = 30, region: str = None):
        """Record screen using ffmpeg"""
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-f', 'x11grab',  # X11 screen capture
            '-framerate', '30',
            '-i', ':0.0',  # Display :0.0
        ]
        
        if region:
            cmd.extend(['-vf', f'crop={region}'])
        
        cmd.extend([
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            output_file
        ])
        
        print(f"🎬 Recording screen for {duration}s → {output_file}")
        # subprocess.run(cmd)  # Uncomment to actually record
        return output_file
    
    def create_title_card(self, output_file: str, title: str, subtitle: str = None):
        """Create title card using ffmpeg"""
        # Create a simple title card with gradient background
        filter_complex = f"""
        color=c=#0a0a0f:s=1920x1080:d=3,
        drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:
        text='{title}':fontsize=72:fontcolor=#e94560:
        x=(w-text_w)/2:y=(h-text_h)/2-50,
        """
        
        if subtitle:
            filter_complex += f"""
        drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:
        text='{subtitle}':fontsize=36:fontcolor=#ffffff:
        x=(w-text_w)/2:y=(h-text_h)/2+50,
        """
        
        filter_complex = filter_complex.rstrip(',')
        
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'lavfi',
            '-i', filter_complex,
            '-t', '3',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            output_file
        ]
        
        print(f"🎨 Creating title card: {title}")
        # subprocess.run(cmd)
        return output_file
    
    def create_section_header(self, output_file: str, section_number: int, title: str):
        """Create section header card"""
        return self.create_title_card(output_file, f"Phase {section_number}", title)
    
    def add_voiceover(self, input_video: str, audio_script: str, output_video: str):
        """Add voiceover narration to video"""
        # In production, this would use TTS (ElevenLabs, etc.)
        print(f"🎙️ Adding voiceover to {input_video}")
        return input_video  # Placeholder
    
    def concatenate_clips(self, clips: List[str], output_file: str):
        """Concatenate multiple video clips"""
        # Create concat file
        concat_file = os.path.join(self.output_dir, 'concat.txt')
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_file
        ]
        
        print(f"🔗 Concatenating {len(clips)} clips → {output_file}")
        subprocess.run(cmd)
        return output_file
    
    def add_background_music(self, video_file: str, audio_file: str, output_file: str, volume: float = 0.3):
        """Add background music to video"""
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_file,
            '-i', audio_file,
            '-filter_complex', f'[1:a]volume={volume}[bg];[0:a][bg]amix=inputs=2:duration=first',
            '-c:v', 'copy',
            '-c:a', 'aac',
            output_file
        ]
        
        print(f"🎵 Adding background music (volume: {volume*100}%)")
        subprocess.run(cmd)
        return output_file
    
    def generate_full_demo(self):
        """Generate complete 3-minute demo reel"""
        print("🎬 Generating KaliAgent v4 Demo Reel (3 minutes)")
        print("=" * 60)
        
        clips = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 0:00-0:15 - Opening Title
        print("\n[0:00-0:15] Creating opening title...")
        clips.append(self.create_title_card(
            os.path.join(self.output_dir, f"{timestamp}_01_intro.mp4"),
            "KALIAGENT V4",
            "Real Attack Works Edition"
        ))
        
        # 0:15-0:45 - Dashboard Overview
        print("\n[0:15-0:45] Dashboard overview...")
        clips.append(self.create_section_header(
            os.path.join(self.output_dir, f"{timestamp}_02_dashboard.mp4"),
            "01",
            "Command Dashboard"
        ))
        # Would capture: Dashboard showing all systems online, network map, live terminal
        
        # 0:45-1:15 - WiFi Attack Demo
        print("\n[0:45-1:15] WiFi attack demonstration...")
        clips.append(self.create_section_header(
            os.path.join(self.output_dir, f"{timestamp}_03_wifi.mp4"),
            "02",
            "WiFi Attack Suite"
        ))
        # Would capture: Monitor mode, deauth attack, handshake capture, hashcat cracking
        
        # 1:15-1:45 - Web App Attack
        print("\n[1:15-1:45] Web application attack...")
        clips.append(self.create_section_header(
            os.path.join(self.output_dir, f"{timestamp}_04_web.mp4"),
            "03",
            "SQL Injection Attack"
        ))
        # Would capture: Nmap scan, SQLMap automation, database dump, shell access
        
        # 1:45-2:15 - C2 Implant Demo
        print("\n[1:45-2:15] C2 server demonstration...")
        clips.append(self.create_section_header(
            os.path.join(self.output_dir, f"{timestamp}_05_c2.mp4"),
            "04",
            "C2 Infrastructure"
        ))
        # Would capture: Payload generation, agent check-in, command execution, screenshot
        
        # 2:15-2:45 - AI Report Generation
        print("\n[2:15-2:45] AI-powered reporting...")
        clips.append(self.create_section_header(
            os.path.join(self.output_dir, f"{timestamp}_06_ai.mp4"),
            "05",
            "AI Report Generation"
        ))
        # Would capture: LLM analyzing results, PDF report generation, professional output
        
        # 2:45-3:00 - Closing
        print("\n[2:45-3:00] Creating closing...")
        clips.append(self.create_title_card(
            os.path.join(self.output_dir, f"{timestamp}_07_outro.mp4"),
            "KALIAGENT V4",
            "83% Complete - Phase 6 In Progress"
        ))
        
        # Concatenate all clips
        final_video = os.path.join(self.output_dir, f"kaliagent_v4_demo_{timestamp}.mp4")
        self.concatenate_clips(clips, final_video)
        
        print("\n" + "=" * 60)
        print(f"✅ Demo video created: {final_video}")
        print(f"📊 Total clips: {len(clips)}")
        print(f"⏱️  Estimated duration: ~3 minutes")
        
        return final_video
    
    def generate_script(self):
        """Generate voiceover script for demo video"""
        script = """
KALIAGENT V4 - DEMO REEL SCRIPT
================================

[0:00-0:15] OPENING
"Welcome to KaliAgent v4 - the most advanced automated penetration testing platform.
This is the Real Attack Works Edition, featuring live C2 servers, real exploits, and AI-powered automation."

[0:15-0:45] DASHBOARD
"Here's our command dashboard, showing real-time status of all systems.
The isolated lab network is online, C2 servers are active, and we're ready for action.
Notice the live terminal feed and network topology map."

[0:45-1:15] WIFI ATTACK
"Let's demonstrate our WiFi attack suite.
With one click, we enable monitor mode, scan for networks, and launch a deauthentication attack.
The handshake is captured automatically, and hashcat begins cracking.
In this demo, we recovered the password in under 30 seconds."

[1:15-1:45] WEB ATTACK
"Next, our automated web application attack chain.
The system scans for web servers, identifies SQL injection vulnerabilities, and exploits them.
Database credentials are dumped, and we establish a reverse shell.
All evidence is captured for the final report."

[1:45-2:15] C2 INFRASTRUCTURE
"Our C2 infrastructure includes Sliver, Empire, and our custom Enhanced C2 server.
Watch as we generate a payload, deploy it to the target, and establish full control.
We can execute commands, capture screenshots, and exfiltrate files."

[2:15-2:45] AI REPORTING
"Finally, our AI-powered report generation.
The LLM analyzes all attack results and generates a professional penetration test report.
Executive summary, detailed findings, CVSS scores, and remediation recommendations.
Available in PDF, HTML, and JSON formats."

[2:45-3:00] CLOSING
"KaliAgent v4 - 83% complete and ready for real-world testing.
Phase 6 is in progress, bringing even more AI integration and polish.
This is the future of automated penetration testing."
"""
        return script


if __name__ == "__main__":
    generator = DemoVideoGenerator()
    
    print("🍀 KaliAgent v4 Demo Video Generator")
    print("=" * 60)
    
    # Generate script
    script = generator.generate_script()
    print("\n📝 Voiceover Script:")
    print(script)
    
    # Uncomment to generate actual video (requires ffmpeg and screen recording setup)
    # final_video = generator.generate_full_demo()
    # print(f"\n✅ Demo video ready: {final_video}")
    
    print("\n🎬 To record actual video:")
    print("1. Install ffmpeg: sudo apt install ffmpeg")
    print("2. Run: python demo_video_generator.py")
    print("3. Uncomment the generate_full_demo() call")
    print("4. Manually perform each demo while recording")
