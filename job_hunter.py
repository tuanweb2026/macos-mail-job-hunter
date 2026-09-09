#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Hunter - Tự động quét email tuyển dụng từ Mail.app trên macOS
Dựa theo 3 hồ sơ năng lực (CV):
1. IT Manager / Infrastructure Head
2. IT Project Manager / Regional Operations
3. Cyber Security & Tech Risk Manager (CISA)
"""

import sys
import os
import subprocess
import email
from email import policy
from html.parser import HTMLParser
import re
from datetime import datetime

# Cấu hình
ACCOUNT_NAME = "Google"
MAX_EMAILS_TO_CHECK = 400
REPORT_DIR = os.path.expanduser("~/.gemini/antigravity/scratch/job_hunter/reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# Từ khóa định danh email tuyển dụng
JOB_ALERT_SENDERS = [
    "indeed", "linkedin", "vietnamworks", "itviec", "topcv", "jobalert", "talentnetwork"
]

JOB_KEYWORDS = [
    "it manager", "infrastructure", "trưởng phòng", "trưởng bộ phận", "project manager",
    "technical project", "cyber security", "security lead", "risk manager", "cisa",
    "network manager", "head of it", "it director", "system admin", "devops",
    "cloud manager", "governance", "bcp", "drp"
]

# Các hồ sơ khớp chuyên môn
PROFILES = {
    "IT_MANAGER": {
        "name": "CV 1 & 2: IT Manager / Infrastructure Head",
        "keywords": ["it manager", "infrastructure", "trưởng phòng công nghệ", "trưởng bộ phận hạ tầng", "hạ tầng it", "operations", "network", "system", "head of it"],
        "weight": 1.0
    },
    "PROJECT_MANAGER": {
        "name": "CV 2: IT Project Manager / Regional Operations",
        "keywords": ["project manager", "technical project manager", "program manager", "regional", "scrum", "it project"],
        "weight": 0.95
    },
    "SECURITY_RISK": {
        "name": "CV 3: Cyber Security & Technology Risk Manager",
        "keywords": ["cyber security", "security lead", "risk", "cisa", "iso 27001", "compliance", "audit", "bcp", "drp", "incident response"],
        "weight": 1.0
    }
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_a = False
        self.curr_href = ""
        self.curr_text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_a = True
            self.curr_href = dict(attrs).get("href", "")
            self.curr_text = []

    def handle_data(self, data):
        if self.in_a:
            self.curr_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            text = " ".join("".join(self.curr_text).split())
            if text and self.curr_href and self.curr_href.startswith("http"):
                self.links.append((text, self.curr_href))
            self.in_a = False
            self.curr_href = ""
            self.curr_text = []

def notify_macos(title, message):
    """Bắn thông báo và chuông macOS"""
    script = f'''display notification "{message}" with title "{title}" sound name "Glass"'''
    subprocess.run(["osascript", "-e", script], capture_output=True)

def fetch_recent_emails():
    """Lấy danh sách tóm tắt các email gần đây từ Mail.app"""
    print(f"[*] Đang kết nối ứng dụng Mail (Tài khoản: {ACCOUNT_NAME})...")
    osa_script = f'''
    tell application "Mail"
        set mbox to mailbox "INBOX" of account "{ACCOUNT_NAME}"
        set res to {{}}
        repeat with i from 1 to {MAX_EMAILS_TO_CHECK}
            try
                set m to message i of mbox
                set d to (date received of m)
                set s to (subject of m)
                set snd to (sender of m)
                set end of res to (i as string) & "<;>" & (d as string) & "<;>" & snd & "<;>" & s
            on error
                exit repeat
            end try
        end repeat
        set AppleScript's text item delimiters to ASCII character 10
        return res as string
    end tell
    '''
    res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Lỗi kết nối Mail.app: {res.stderr}")
        return []
    
    lines = res.stdout.strip().splitlines()
    print(f"[+] Đã đọc {len(lines)} email gần nhất từ Mail.app.")
    return lines

def fetch_email_source(msg_idx):
    """Lấy nội dung chi tiết dạng MIME của một email theo chỉ mục"""
    osa_script = f'''
    tell application "Mail"
        set mbox to mailbox "INBOX" of account "{ACCOUNT_NAME}"
        set m to message {msg_idx} of mbox
        return (source of m)
    end tell
    '''
    res = subprocess.run(["osascript", "-e", osa_script], capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else ""

def parse_mime_links(raw_eml):
    """Trích xuất danh sách liên kết từ MIME"""
    msg = email.message_from_string(raw_eml, policy=policy.default)
    html_part = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_part = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                break
    else:
        html_part = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")

    if not html_part:
        return []

    parser = LinkParser()
    try:
        parser.feed(html_part)
    except Exception:
        pass
    return parser.links

def evaluate_match(subject, text_content):
    """Đánh giá độ khớp với các nhóm CV"""
    combined = (subject + " " + text_content).lower()
    matched_profiles = []
    
    for code, pdata in PROFILES.items():
        score = sum(1 for kw in pdata["keywords"] if kw in combined)
        if score > 0:
            matched_profiles.append((pdata["name"], score))
            
    matched_profiles.sort(key=lambda x: x[1], reverse=True)
    return matched_profiles

def main():
    print("=" * 60)
    print("🚀 BẮT ĐẦU TỰ ĐỘNG QUÉT VIỆC LÀM PHÙ HỢP CV TỪ GMAIL")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    lines = fetch_recent_emails()
    if not lines:
        print("[!] Không tìm thấy dữ liệu từ Mail.")
        sys.exit(1)

    matched_jobs = []

    for line in lines:
        parts = line.strip().split("<;>")
        if len(parts) < 4:
            continue
        idx, date_str, sender, subject = parts[0], parts[1], parts[2], parts[3]
        
        sender_lower = sender.lower()
        sub_lower = subject.lower()

        is_job_sender = any(s in sender_lower for s in JOB_ALERT_SENDERS)
        is_job_title = any(kw in sub_lower for kw in JOB_KEYWORDS)

        if is_job_sender and is_job_title:
            matches = evaluate_match(subject, "")
            if matches:
                print(f"[*] Đang xử lý email khớp: [{idx}] {subject[:60]}...")
                raw = fetch_email_source(idx)
                links = parse_mime_links(raw)
                
                job_links = []
                for t, u in links:
                    t_lower = t.lower()
                    if any(w in t_lower for w in ["manager", "lead", "head", "specialist", "engineer", "admin", "xem", "apply", "chi tiết"]):
                        if not any(ign in t_lower for ign in ["privacy", "unsubscribe", "help", "terms", "chính sách"]):
                            job_links.append({"title": t, "url": u})

                matched_jobs.append({
                    "id": idx,
                    "date": date_str,
                    "sender": sender,
                    "subject": subject,
                    "profiles": [m[0] for m in matches],
                    "links": job_links[:6]
                })

    print(f"\n[+] Tổng cộng tìm thấy {len(matched_jobs)} email tuyển dụng khớp hồ sơ.")

    report_file = os.path.join(REPORT_DIR, f"job_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    latest_file = os.path.join(REPORT_DIR, "latest_report.html")

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Việc Làm Phù Hợp CV</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f8fafc; color: #1e293b; padding: 30px; margin: 0; }}
    .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
    h1 {{ color: #0f172a; margin-top: 0; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-right: 6px; background: #e0f2fe; color: #0369a1; }}
    .job-card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 16px; transition: border 0.2s; }}
    .job-card:hover {{ border-color: #3b82f6; }}
    .job-title {{ font-size: 18px; font-weight: 600; color: #1e3a8a; margin-bottom: 6px; }}
    .meta {{ font-size: 13px; color: #64748b; margin-bottom: 12px; }}
    ul.links {{ list-style-type: none; padding-left: 0; margin-top: 10px; }}
    ul.links li {{ margin-bottom: 6px; }}
    ul.links a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
    ul.links a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="container">
    <h1>🎯 Danh Sách Việc Làm Khớp CV Hôm Nay</h1>
    <p>Thời gian quét: <strong>{datetime.now().strftime('%d/%m/%Y %H:%M')}</strong> | Tìm thấy: <strong>{len(matched_jobs)}</strong> thông báo phù hợp.</p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
"""

    for job in matched_jobs:
        html += f"""
    <div class="job-card">
        <div class="job-title">{job['subject']}</div>
        <div class="meta">📅 {job['date']} &nbsp;|&nbsp; ✉️ {job['sender']}</div>
        <div>
"""
        for prof in job['profiles']:
            html += f"""<span class="badge">{prof}</span>"""
        html += """</div><ul class="links">"""
        
        if job['links']:
            for l in job['links']:
                html += f"""<li>👉 <a href="{l['url']}" target="_blank">{l['title']}</a></li>"""
        else:
            html += """<li><em>(Xem nội dung đầy đủ trực tiếp trên ứng dụng Mail)</em></li>"""
            
        html += """</ul></div>"""

    html += """
</div>
</body>
</html>
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(html)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Báo cáo đã được lưu tại: {latest_file}")

    # Bắn alert hệ thống
    notify_msg = f"Đã tìm thấy {len(matched_jobs)} việc làm phù hợp với CV của bạn!"
    notify_macos("🎯 Antigravity Job Hunter", notify_msg)

    # Tự động mở báo cáo trên trình duyệt
    subprocess.run(["open", latest_file])

if __name__ == "__main__":
    main()
