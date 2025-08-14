#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APRS-IS RAW packet logger (line-accurate, banner filtered)
- Prints every non-comment line to console
- Saves daily logs to aprs_raw_YYYYMMDD.log
- Auto-reconnects with backoff

Tested on Windows (Python 3.9+) and Linux.
"""

import socket
import time
import os
from datetime import datetime, timezone, timedelta

# =========================
# CONFIG
# =========================
HOST = "rotate.aprs2.net"   # หรือเลือก T2 เฉพาะก็ได้ เช่น "euro.aprs2.net"
PORT = 14580
CALLSIGN = "CALLSIGN-SSID"          # <- เปลี่ยนเป็น callsign ของคุณ (ไม่ต้องใส่ -SSID)
PASSCODE = "PASSWD"              # รับอย่างเดียวใช้ -1
VERS = "APRS Logger 1.0"    # ชื่อโปรแกรมตามใจ
# ตัวอย่างฟิลเตอร์ (เลือกหนึ่งอย่าง หรือแก้ได้เอง):
# FILTER = "p/HS1AB-10"                                  # เฉพาะสถานีนี้
# FILTER = "b/HS1AB-10/E24AD-1"                         # หลายสถานี
FILTER = "r/14.036077/100.725963/1000"                      # รัศมี 1000 กม. รอบพิกัด

# ถ้าต้องการแสดงบรรทัดที่ขึ้นต้นด้วย "#", ให้ตั้งเป็น True
SHOW_SERVER_COMMENTS = False

# โซนเวลาเพื่อแสตมป์ (เอเชีย/กรุงเทพฯ = UTC+7)
TZ = timezone(timedelta(hours=7))

# =========================
# IMPLEMENTATION
# =========================

def now_str():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

def log_path_for_today():
    return datetime.now(TZ).strftime("aprs_raw_%Y%m%d.log")

def send_login(sock: socket.socket):
    login_line = f"user {CALLSIGN} pass {PASSCODE} vers {VERS} filter {FILTER}\n"
    sock.sendall(login_line.encode("utf-8"))

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect((HOST, PORT))
    s.settimeout(None)  # หลังล็อกอินปล่อยให้บล็อกตามปกติ
    return s

def stream():
    backoff = 2
    max_backoff = 60
    buffer = b""
    current_log = None
    current_log_name = None

    while True:
        try:
            print(f"[{now_str()}] Connecting to {HOST}:{PORT} ...")
            s = connect()
            print(f"[{now_str()}] Connected. Sending login/filter ...")
            send_login(s)
            print(f"[{now_str()}] Login sent: user {CALLSIGN} pass {PASSCODE} vers {VERS} filter {FILTER}")

            # reset buffer and backoff after successful connect
            buffer = b""
            backoff = 2

            # open today log
            target = log_path_for_today()
            if current_log_name != target:
                if current_log:
                    current_log.close()
                current_log_name = target
                current_log = open(current_log_name, "a", encoding="utf-8", newline="\n")
                print(f"[{now_str()}] Logging to {current_log_name}")

            while True:
                data = s.recv(4096)
                if not data:
                    raise ConnectionError("Server closed connection")

                buffer += data
                # split by newline — keep last partial line in buffer
                *lines, buffer = buffer.split(b"\n")

                for raw in lines:
                    line = raw.decode("utf-8", errors="ignore").rstrip("\r")
                    # rotate file by date change
                    target = log_path_for_today()
                    if current_log_name != target:
                        if current_log:
                            current_log.close()
                        current_log_name = target
                        current_log = open(current_log_name, "a", encoding="utf-8", newline="\n")
                        print(f"[{now_str()}] Switched log to {current_log_name}")

                    if line.startswith("#"):
                        # server banner / comments
                        if SHOW_SERVER_COMMENTS:
                            print(line)
                        # ไม่บันทึกลงไฟล์ raw
                        continue

                    # Print every non-comment line (RAW APRS)
                    print(line)
                    current_log.write(line + "\n")
                    current_log.flush()

        except (socket.timeout, ConnectionError, OSError) as e:
            print(f"[{now_str()}] Connection error: {e}. Reconnecting in {backoff}s ...")
            try:
                if current_log:
                    current_log.flush()
            except Exception:
                pass
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
            continue
        except KeyboardInterrupt:
            print(f"\n[{now_str()}] Interrupted by user.")
            break
        finally:
            try:
                if current_log:
                    current_log.flush()
            except Exception:
                pass

if __name__ == "__main__":
    # สรุปคอนฟิกให้เห็นชัด ๆ
    print("==== APRS-IS RAW LOGGER ====")
    print(f" Server   : {HOST}:{PORT}")
    print(f" Callsign : {CALLSIGN}")
    print(f" Filter   : {FILTER}")
    print(f" Comments : {'SHOW' if SHOW_SERVER_COMMENTS else 'HIDE'} (lines starting with #)")
    print(" Press Ctrl+C to stop.\n")
    stream()
