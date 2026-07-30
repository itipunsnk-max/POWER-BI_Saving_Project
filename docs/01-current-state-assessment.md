# ผลตรวจระบบปัจจุบัน

วันที่ตรวจ: 30 กรกฎาคม 2026  
แหล่งข้อมูล: Project Summary, PDF สรุปงบ/ค่าใช้จ่าย, PBIX และ Power BI Service

## สรุปผล

ระบบมีองค์ประกอบสำคัญแล้ว ได้แก่ Service Tracking, Asset, AM, Vendor, Budget,
IW39, ME2K, PM order และตารางงานค้าง แต่ยังเป็นชุดหน้ารายงานที่สร้างตามโจทย์
ย่อยมากกว่าจะเป็นผลิตภัณฑ์บริหาร Saving แบบครบวงจร

ผลประเมิน: **Share with caveats / ต้องแก้ก่อนประกาศ Saving**

## สิ่งที่มีอยู่แล้ว

- Semantic model มีอย่างน้อย 22 ตาราง
- รายงานมี 12 หน้า โดย 10 หน้าแสดงต่อผู้ใช้ และ 2 หน้าซ่อน
- มีแนวโน้มค่าใช้จ่าย 2025-2026, Root cause, Cost by AM, Vendor overdue,
  Budget/Actual และ KPI Cost Reduction
- มี Drill-down ตามปี/ไตรมาส/เดือน และรายละเอียดอาการ
- มีการเชื่อม Report ID กับ Semantic Model ID บน Power BI Service

## ประเด็นสำคัญที่พบ

### 1. Baseline ไม่เป็น Source of Truth เดียว

| รายการ | Baseline 2025 (บาท) | Saving 20% (บาท) | Target cost (บาท) |
|---|---:|---:|---:|
| PM/CM classification | 12,590,005.44 | 2,518,001.09 | 10,072,004.35 |
| Service Tracking dashboard | 15,359,352.14 | 3,071,870.43 | 12,287,481.71 |
| ส่วนต่าง | 2,769,346.70 | 553,869.34 | 2,215,477.36 |

ส่วนต่าง Baseline เท่ากับ 18.03% ของยอด Dashboard จึงมีนัยสำคัญพอที่จะเปลี่ยน
ผลตัดสินว่าโครงการบรรลุ 20% หรือไม่

ต้องสร้าง Reconciliation bridge:

`Service Tracking → Billed → SAP actual → Commitment → Accrual → Exclusion`

### 2. KPI ลด 50.04% ยังไม่ควรใช้เป็นผลสำเร็จ

หน้าปัจจุบันเปรียบเทียบ Actual 2025 Same Period 7.80 ล้านบาท กับ Actual 2026
Comparable 3.90 ล้านบาท จึงได้ Reduction 50.04% แต่ยังมีความเสี่ยงจาก:

- Power BI Service แสดง Data updated 22 กรกฎาคม 2026
- ไฟล์ทำงานใหม่กว่ามียอด 2026 ไม่ตรงกับ Service
- งานค้างวางบิลและ Commitment แยกอยู่คนละตาราง
- 2026 เป็นปีที่ยังไม่ปิดบัญชี
- ไม่มี Period complete / Finance lock indicator บน KPI

ควรเปลี่ยน KPI หลักเป็น `Cost Exposure = Actual + Commitment + Accrual`
และแสดง Actual-only เป็นข้อมูลประกอบ

### 3. Unknown/0 มีมูลค่าสูง

ข้อมูลปี 2025 พบกลุ่มอาการไม่ระบุ/รหัส 0 มูลค่าสูง โดยเฉพาะงานถังใต้ดินและ
ตู้จ่ายน้ำมัน กลุ่มนี้ทำให้ Root cause และ Self Maintenance targeting ไม่น่าเชื่อถือ

Data Quality Gate ที่ต้องมี:

- Work type coverage ≥ 98%
- Symptom coverage ≥ 95%
- Asset match rate ≥ 98%
- SAP order match rate ≥ 98%
- Unknown cost share ≤ 5%
- Duplicate service ID = 0
- Finance reconciliation variance ≤ 1%

### 4. โครงสร้างรายงานซ้ำและชื่อหน้าไม่พร้อม Production

พบหน้า `Page 1`, `Page 2`, `Page 3`, `Duplicate of...` และชื่อ
`Rootcasue Analyst` ซึ่งควรเปลี่ยนให้สื่อวัตถุประสงค์ รวมหน้า 2025/2026 ที่ซ้ำกัน
และซ่อนหน้าทดลองจากผู้ใช้ Production

### 5. My workspace ไม่เหมาะเป็น Production

ควรแยก Workspace เป็น DEV / TEST / PROD กำหนด Owner, Viewer, Release owner,
Gateway owner และ Refresh owner ชัดเจน พร้อม Deployment pipeline เมื่อ License
รองรับ

## หลักฐานตัวเลขที่ใช้กำหนดโอกาส

ปี 2025 จาก Service Tracking:

- ตู้จ่ายน้ำมันรวมประมาณ 11.67 ล้านบาทในข้อมูลรวม 2025-2026 ที่หน้า Cost by AM
- กลุ่มอาการค่าใช้จ่ายสูงของปี 2025 ได้แก่ แม่ปั๊ม/มิเตอร์, มอเตอร์/สายพาน,
  สายยาง, มือจ่าย และการแสดงผล
- 5 กลุ่มข้างต้นรวมประมาณ 7.52 ล้านบาท หรือ 48.94% ของ Service baseline
  15.36 ล้านบาท
- PM/CM classification ระบุ CM ประมาณ 8.97 ล้านบาท (71.21%) และ PM
  ประมาณ 3.62 ล้านบาท (28.79%)

ตัวเลขสองชุดมาจากคนละมุมมองและต้อง Reconcile ก่อนใช้คำนวณผลประหยัดจริง

