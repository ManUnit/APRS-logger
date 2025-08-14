

# APRS-IS RAW Packet Logger

สคริปต์ Python สำหรับเชื่อมต่อ APRS-IS และบันทึกแพ็กเก็ตดิบ (RAW) พร้อมระบบกรองข้อมูล, บันทึกลงไฟล์รายวัน, และการเชื่อมต่อใหม่อัตโนมัติ

## คุณสมบัติ

- **เชื่อมต่อ APRS-IS** ผ่านโฮสต์/พอร์ตที่กำหนด
- **กรองข้อมูล** ด้วย APRS filter (ระบุ callsign หรือพิกัด + รัศมี)
- **บันทึกข้อมูล RAW** แยกไฟล์ตามวันที่ (`aprs_raw_YYYYMMDD.log`)
- **แสดงผลแบบเรียลไทม์** บนคอนโซล
- **รองรับ Windows และ Linux**
- **ระบบ reconnect อัตโนมัติ** พร้อม backoff แบบเพิ่มเวลา

## การติดตั้ง

ต้องใช้ Python 3.9 ขึ้นไป

```bash
git clone https://github.com/USERNAME/REPO.git
cd REPO
