# แผนลดต้นทุน 20%

## 1. Target

ใช้ Baseline PM/CM 2025 จำนวน 12,590,005.44 บาทเป็น Working baseline
ชั่วคราว:

- Saving target = 2,518,001.09 บาท
- Monthly saving run-rate = 209,833.42 บาท
- Cost ceiling = 10,072,004.35 บาท

**หมายเหตุ:** ต้องยืนยันกับ Finance ก่อน Lock เพราะ Dashboard อีกหน้ามี Baseline
15,359,352.14 บาท

## 2. Target allocation แบบบริหาร

นี่คือการแบ่งเป้าหมาย ไม่ใช่ผลประหยัดที่เกิดขึ้นแล้ว

| Lever | Target (บาท) | สัดส่วน | วิธีพิสูจน์ |
|---|---:|---:|---|
| Preventable CM / Repeat failure | 950,000 | 37.7% | เทียบ repeat rate และ avoided recurrence |
| PM & legal test bundling | 450,000 | 17.9% | Route/bundle saving เทียบราคาเดิม |
| Vendor/parts price control | 500,000 | 19.9% | Price variance และ negotiated rate |
| Repair-vs-replace / asset reuse | 400,000 | 15.9% | Lifecycle NPV และ approved replacement |
| Billing/duplicate/data control | 218,001 | 8.7% | Credit note, rejected duplicate, warranty |
| **รวม** | **2,518,001** | **100%** | Finance validation |

## 3. อาการที่ควรทำก่อน

จากข้อมูลปี 2025 กลุ่มค่าใช้จ่ายสูง 5 อันดับแรก:

| กลุ่มอาการ | ค่าใช้จ่ายประมาณ (บาท) | แนวทาง |
|---|---:|---|
| ตู้จ่าย - แม่ปั๊ม/มิเตอร์ | 2,200,854 | RCA, condition check, repair-vs-replace |
| ตู้จ่าย - มอเตอร์/สายพาน | 1,755,784 | PM standard, repeat failure, parts standard |
| ตู้จ่าย - สายยาง | 1,461,017 | External inspection, replacement criteria |
| ตู้จ่าย - มือจ่าย | 1,197,887 | Triage, warranty, failure code |
| ตู้จ่าย - การแสดงผล | 900,958 | Remote triage, approved reset, parts reuse |
| **รวม** | **7,516,501** | 48.94% ของ Service baseline |

กลุ่ม `0/ไม่ระบุ` ต้องเป็น Workstream แยก เพราะอาจซ่อนโอกาสมากกว่าอาการที่
จัดประเภทแล้ว ห้ามนำ Unknown ไปนับเป็น Saving

## 4. วิธีลดต้นทุนอื่น

### Demand avoidance

- Mandatory triage ก่อน dispatch
- เช็กประวัติ 90 วันและ Warranty ก่อนเปิด PO
- Merge ticket ซ้ำของ Asset เดียวกัน
- Severity/SLA ตามผลกระทบ ไม่ใช้ Urgent ทุกงาน

### Reliability

- Bad actor list รายเดือน
- RCA เมื่อซ่อมซ้ำ 2 ครั้งใน 90 วัน
- Repair-vs-replace เมื่อค่า repair 12 เดือนเกิน threshold ที่อนุมัติ
- Standard failure code และ parts used

### Commercial

- Rate card แยก labor/travel/part
- Benchmark ราคา job เดียวกันข้าม Vendor
- Warranty recovery
- Bundle งานตามพื้นที่/รอบ PM
- Consignment/critical spare สำหรับอะไหล่ใช้บ่อย

### Process

- Three-way match: Service order / PO / Invoice
- Duplicate invoice and duplicate service check
- Close code บังคับก่อนจ่ายเงิน
- Finance lock รายเดือน

## 5. Saving ledger

ผลประหยัดต้องบันทึกเป็น Ledger ไม่คำนวณจากยอดลดลงเพียงอย่างเดียว

ฟิลด์ขั้นต่ำ:

- Saving ID, Lever, Owner, Service/Asset reference
- Baseline method, Baseline amount
- Counterfactual amount
- Actual amount
- Gross saving, implementation cost, net saving
- Evidence URL
- Finance status: Draft / Reviewed / Approved / Rejected
- Approval date and approver role

Guardrails:

- งานทดสอบตามกฎหมายครบ 100%
- Safety incident = 0
- Reopen after self maintenance ≤ 5%
- Emergency downtime ไม่เพิ่ม
- Customer complaint rate ไม่เพิ่ม

