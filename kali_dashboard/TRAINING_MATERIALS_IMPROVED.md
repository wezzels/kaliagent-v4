# KaliAgent Training Materials

Complete training curriculum with interactive diagrams and certification paths.

---

## Table of Contents

1. [Training Overview](#training-overview)
2. [Certification Path](#certification-path)
3. [Beginner Track](#beginner-track)
4. [Intermediate Track](#intermediate-track)
5. [Advanced Track](#advanced-track)
6. [Admin Track](#admin-track)
7. [Hands-On Labs](#hands-on-labs)
8. [Assessment Exams](#assessment-exams)
9. [Training Schedule](#training-schedule)
10. [Instructor Guide](#instructor-guide)
11. [Certification Program](#certification-program)

---

## Training Overview

### Learning Objectives

By the end of this training, participants will be able to:

✅ Install and configure KaliAgent  
✅ Execute security assessment playbooks  
✅ Interpret and report findings  
✅ Configure safety controls  
✅ Integrate with existing tools  
✅ Troubleshoot common issues  
✅ Administer KaliAgent deployments  

### Target Audience

```mermaid
graph TD
    A[Security Professional] --> B{Choose Your Path}
    
    B -->|Analyst| C[Beginner Track<br/>4 hours]
    B -->|Pen Tester| D[Intermediate Track<br/>8 hours]
    B -->|Consultant| E[Advanced Track<br/>16 hours]
    B -->|Admin| F[Admin Track<br/>4 hours]
    B -->|Manager| G[Overview Track<br/>2 hours]
    
    C --> H[KCS Certified]
    D --> I[KCP Certified]
    E --> J[KCE Certified]
    F --> K[KCA Certified]
    G --> L[Informed Decision Maker]
```

### Role-Based Training Paths

| Role | Track | Duration | Certification | Prerequisites |
|------|-------|----------|---------------|---------------|
| 🔰 **Security Analyst** | Beginner | 4 hours | KCS | Basic Linux, networking |
| 🔐 **Penetration Tester** | Intermediate | 8 hours | KCP | 1+ year experience |
| 🎯 **Security Consultant** | Advanced | 16 hours | KCE | 3+ years pentesting |
| ⚙️ **System Administrator** | Admin | 4 hours | KCA | Linux admin, Docker |
| 👔 **Security Manager** | Overview | 2 hours | N/A | Management role |

---

## Certification Path

### Certification Hierarchy

```mermaid
graph TB
    A[Start Training] --> B{Select Track}
    
    B --> C[Beginner Track]
    B --> D[Intermediate Track]
    B --> E[Advanced Track]
    B --> F[Admin Track]
    
    C --> G[Complete 7 Modules]
    D --> H[Complete 6 Modules]
    E --> I[Complete 8 Modules]
    F --> J[Complete 6 Modules]
    
    G --> K[Pass Exam 80%+]
    H --> L[Pass Exam 85%+]
    I --> M[Pass Exam 90%+]
    J --> N[Complete Labs]
    
    K --> O[🏆 KCS Certified<br/>2 years]
    L --> P[🏆 KCP Certified<br/>2 years]
    M --> Q[🏆 KCE Certified<br/>2 years]
    N --> R[🏆 KCA Certified<br/>2 years]
    
    O --> S{Recertify?}
    P --> S
    Q --> S
    R --> S
    
    S -->|Yes| T[4 hours CE or Exam]
    S -->|No| U[Certification Expires]
    
    T --> V[Renewed 2 years]
```

### Certification Levels

| Level | Code | Name | Requirements | Validity |
|-------|------|------|--------------|----------|
| 🥉 **Level 1** | KCS | KaliAgent Certified Specialist | Beginner track + 80% exam | 2 years |
| 🥈 **Level 2** | KCP | KaliAgent Certified Professional | Intermediate + 85% exam + KCS | 2 years |
| 🥇 **Level 3** | KCE | KaliAgent Certified Expert | Advanced + 90% exam + KCP | 2 years |
| ⚙️ **Specialist** | KCA | KaliAgent Certified Admin | Admin track + labs | 2 years |

### Recertification Requirements

```mermaid
graph LR
    A[Certification Expiring] --> B{Choose Option}
    B --> C[Complete 4h CE]
    B --> D[Pass Recert Exam]
    C --> E[Submit CE Credits]
    D --> F[Pass Exam 80%+]
    E --> G[Renewed 2 years]
    F --> G
    G --> H[Continue Cycle]
```

**Continuing Education (CE) Options:**

| Activity | CE Hours | Max per Cycle |
|----------|----------|---------------|
| **Advanced Webinars** | 2 hours | 4 hours |
| **Case Studies** | 1 hour | 2 hours |
| **Community Contribution** | 1 hour | 2 hours |
| **Recertification Exam** | 4 hours | Unlimited |

---

## Beginner Track

### Module 1: Introduction to KaliAgent (30 min)

#### Learning Objectives

After this module, you will be able to:
- Explain what KaliAgent does
- Identify key features
- Recognize appropriate use cases
- Understand safety considerations

#### What is KaliAgent?

**Definition:** KaliAgent is a professional security automation platform that orchestrates 52 Kali Linux tools with safety controls and professional reporting.

**Key Capabilities:**

```mermaid
graph LR
    A[KaliAgent Platform] --> B[52 Kali Tools]
    A --> C[5 Automated Playbooks]
    A --> D[Web Dashboard]
    A --> E[PDF Reports]
    A --> F[Safety Controls]
    
    B --> G[Nmap, SQLMap, etc.]
    C --> H[Recon, Web Audit, etc.]
    D --> I[React UI, Real-time]
    E --> J[Executive Summaries]
    F --> K[Whitelist, Auth, Audit]
```

#### Knowledge Check

**Question 1:** How many Kali Linux tools does KaliAgent integrate?

- A) 25
- B) 52 ✅
- C) 100
- D) 10

**Question 2:** Which is NOT a playbook type?

- A) Reconnaissance
- B) Web Audit
- C) Social Media Audit ✅
- D) Password Cracking

---

### Module 2: Installation & Setup (45 min)

#### Learning Objectives

After this module, you will be able to:
- Install KaliAgent dependencies
- Configure the platform
- Verify installation
- Troubleshoot common issues

#### Installation Flowchart

```mermaid
graph TD
    A[Start Installation] --> B{OS Check}
    B -->|Kali Linux| C[Tools Pre-installed]
    B -->|Ubuntu| D[Install Kali Tools]
    B -->|Other| E[Not Supported]
    
    C --> F[Clone Repository]
    D --> F
    
    F --> G[Install Python Deps]
    G --> H[Install Node Deps]
    H --> I[Run Tests]
    I --> J{Tests Pass?}
    J -->|Yes| K[✅ Installation Complete]
    J -->|No| L[❌ Check Errors]
    L --> M[Fix Issues]
    M --> I
```

#### Hands-On Lab

**Step 1: Clone Repository**
```bash
git clone https://github.com/wezzels/agentic-ai.git
cd agentic-ai/kali_dashboard
```

**Step 2: Install Python Dependencies**
```bash
pip3 install -r requirements.txt
```

**Step 3: Install Frontend**
```bash
cd frontend
npm install
```

**Step 4: Start Services**
```bash
# Terminal 1 - Backend
cd ..
python3 server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Step 5: Verify Installation**
```bash
curl http://localhost:8001/api/health
# Expected: {"status": "healthy"}
```

---

### Module 3: Dashboard Navigation (30 min)

#### Dashboard Pages

```mermaid
graph TB
    A[Main Dashboard] --> B[Engagements]
    A --> C[Playbooks]
    A --> D[Tools]
    A --> E[Settings]
    A --> F[Live Monitor]
    
    B --> B1[Create New]
    B --> B2[View Existing]
    B --> B3[Track Progress]
    
    C --> C1[Browse Playbooks]
    C --> C2[Execute Workflow]
    C --> C3[View History]
    
    D --> D1[Search Tools]
    D --> D2[View Details]
    D --> D3[Check Auth Level]
    
    E --> E1[Safety Settings]
    E --> E2[Authorization]
    E --> E3[Audit Logs]
    
    F --> F1[Real-time Output]
    F --> F2[Progress Bars]
    F --> F3[Stop/Pause]
```

#### Navigation Exercise

Navigate to each page and document:
1. Page URL
2. 3 key elements
3. 1 action performed

---

### Module 4: Running Your First Playbook (60 min)

#### Playbook Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Dashboard
    participant API
    participant KaliAgent
    participant Tools
    
    User->>Dashboard: Navigate to Playbooks
    Dashboard->>User: Show available playbooks
    User->>Dashboard: Select Reconnaissance
    Dashboard->>User: Show configuration form
    User->>Dashboard: Enter target: scanme.nmap.org
    Dashboard->>API: POST /api/playbooks/execute
    API->>KaliAgent: Validate target
    KaliAgent->>KaliAgent: Check whitelist
    KaliAgent->>KaliAgent: Check blacklist
    KaliAgent->>KaliAgent: Verify auth level
    KaliAgent->>Tools: Execute Nmap
    KaliAgent->>Tools: Execute Amass
    KaliAgent->>Tools: Execute theHarvester
    Tools-->>KaliAgent: Return results
    KaliAgent->>API: Store findings
    API-->>Dashboard: Execution complete
    Dashboard->>User: Show results
```

---

## Assessment Exams

### Exam Structure

```mermaid
graph LR
    A[Exam Start] --> B[Section 1: MC Questions]
    B --> C[Section 2: Practical Lab]
    C --> D[Auto-Grading]
    D --> E{Score >= Pass?}
    E -->|Yes| F[🎉 Pass - Certificate]
    E -->|No| G[❌ Fail - Retake]
    G --> H[Study Weak Areas]
    H --> A
```

### Exam Details

| Track | Questions | Practical | Passing Score | Time Limit |
|-------|-----------|-----------|---------------|------------|
| **Beginner** | 20 MC | 1 lab | 80% | 60 min |
| **Intermediate** | 15 MC | 2 labs | 85% | 90 min |
| **Advanced** | 10 MC | 3 labs | 90% | 120 min |
| **Admin** | 15 MC | 2 labs | 85% | 90 min |

---

## Training Schedule

### Week 1: Beginner Track

```mermaid
gantt
    title Beginner Track Schedule
    dateFormat  YYYY-MM-DD
    axisFormat  %a
    
    section Day 1
    Module 1: Introduction     :m1, 2026-04-20, 30m
    Module 2: Installation     :m2, after m1, 45m
    
    section Day 2
    Module 3: Dashboard        :m3, 2026-04-21, 30m
    Module 4: First Playbook   :m4, after m3, 60m
    
    section Day 3
    Module 5: Findings         :m5, 2026-04-22, 45m
    Module 6: Reports          :m6, after m5, 30m
    
    section Day 4
    Module 7: Safety           :m7, 2026-04-23, 30m
    Exam                       :exam, after m7, 60m
```

---

## Instructor Guide

### Preparation Checklist

```mermaid
graph TD
    A[Start Prep] --> B[Set Up Environment]
    B --> C[Test All Labs]
    C --> D[Prepare Materials]
    D --> E[Test AV Equipment]
    E --> F[Print Workbooks]
    F --> G[Prepare Certificates]
    G --> H{Ready?}
    H -->|Yes| I[✅ Start Training]
    H -->|No| B
```

---

## Certification Program

### Benefits by Level

| Benefit | KCS | KCP | KCE | KCA |
|---------|-----|-----|-----|-----|
| **Digital Badge** | ✅ | ✅ | ✅ | ✅ |
| **Certificate PDF** | ✅ | ✅ | ✅ | ✅ |
| **Community Access** | ✅ | ✅ | ✅ | ✅ |
| **Priority Support** | ❌ | ✅ | ✅ | ✅ |
| **Expert Directory** | ❌ | ❌ | ✅ | ❌ |
| **Beta Features** | ❌ | ❌ | ✅ | ✅ |
| **Instructor Status** | ❌ | ❌ | ✅ | ❌ |

---

*Last Updated: April 18, 2026*  
*Version: 2.0.0 (Improved with Mermaid diagrams)*
