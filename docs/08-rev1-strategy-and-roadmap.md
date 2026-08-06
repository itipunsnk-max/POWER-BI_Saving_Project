# Rev.1 Strategy & Delivery Roadmap

เอกสารนี้อัปเดตจาก `service_tracking_cleaned-Rev.1.xlsx` และสถานะ PBIX/Repository
ณ วันที่ 7 สิงหาคม 2026 เป้าหมายคือเปลี่ยนรายงานจาก “สรุปยอดย้อนหลัง” ให้เป็น
ระบบตัดสินใจที่พิสูจน์ผลประหยัดได้ คุมความเสี่ยงได้ และส่งต่อให้ทีม Power BI
ดำเนินการจริงได้เป็นเฟส

## 1. Executive decision

สิ่งที่ข้อมูลยืนยันได้ในขณะนี้:

- `Clean_Data` มี 1,586 งาน, 52 ฟิลด์ และ Service ID ไม่ซ้ำ
- ยอดปี 2025 ใน Excel Rev.1 เท่ากับ 15,331,857.14 บาท
- ช่วงเทียบเท่ากัน Jan-Jun 2025 เท่ากับ 7,770,078.59 บาท และ Jan-Jun 2026
  เท่ากับ 4,386,281.25 บาท ลดเชิงคำนวณ 3,383,797.34 บาท หรือ 43.55%
- SLA met รวมเท่ากับ 61.70% ของงานที่ประเมิน SLA ได้ และ H1/2026 เท่ากับ 65.10%
- งานสองระบบหลัก — ตู้จ่ายน้ำมันและถังน้ำมันใต้ดิน — รวม 90.72% ของต้นทุน
  ทั้งหมด จึงเป็นจุดเริ่ม pilot ที่มี leverage สูง

สิ่งที่ยังห้ามประกาศเป็นผลสำเร็จ:

- 43.55% เป็น `Actual-only analytical reduction` ไม่ใช่ Finance-approved saving
- ไม่มี Commitment, Accrual, Finance control total และ Saving ledger ใน workbook
- Baseline เดิม 15,359,352.14 บาทต่างจาก Excel Rev.1 จำนวน 27,495 บาท และ
  Working baseline PM/CM เดิม 12,590,005.44 บาทต่างจาก Rev.1 ถึง 2,741,851.70 บาท
- อาการที่ว่างหรือ “อื่น ๆ” ครอบคลุมต้นทุน 7,809,063.79 บาท หรือ 39.34%
- Asset coverage มีเพียง 10.72% จึงยังคำนวณ Repeat Repair, MTBF และ
  Repair-vs-Replace อย่างน่าเชื่อถือไม่ได้

คำแนะนำต่อกรรมการ:

> อนุมัติ `Controlled Pilot` 12 สัปดาห์ โดยให้ Data Quality, Finance reconciliation
> และ Safety guardrail เป็นเงื่อนไขปล่อย KPI ไม่ใช่งานเอกสารภายหลัง

## 2. Engineering logic: จากยอดลดลงสู่ผลประหยัดที่พิสูจน์ได้

### 2.1 Cost exposure ก่อน saving

ใช้สมการหลัก:

`Cost Exposure = Actual + Open Commitment + Accrual - Reversal`

และใช้:

`Finance-approved Net Saving = Counterfactual - Cost Exposure - Implementation Cost`

ห้ามใช้ `ยอดปีนี้ต่ำกว่าปีก่อน` เป็น Saving โดยอัตโนมัติ เพราะอาจเกิดจาก invoice
ล่าช้า, ปริมาณงานลด, scope เปลี่ยน, PM เลื่อน, งานยังไม่ปิด หรือข้อมูลยังไม่ครบ

### 2.2 Decomposition สำหรับช่วง Jan-Jun

การเปลี่ยนจาก 7.770 ล้านบาทเป็น 4.386 ล้านบาทแยกได้เป็น:

| Driver | ผลต่อค่าใช้จ่าย | วิธีตีความ |
|---|---:|---|
| จำนวนงานลดลง | -745,076 บาท | งานลดจาก 511 เป็น 462 งาน |
| PM/CM mix | +30,905 บาท | สัดส่วนงานเปลี่ยนและเพิ่มต้นทุนเล็กน้อยเมื่อคุมราคาเดิม |
| Cost/job + severity/scope/price + missing exposure | -2,669,626 บาท | ต้องแตกต่อด้วยข้อมูล Part, Vendor, severity, Commitment และ Accrual |
| **ผลรวม** | **-3,383,797 บาท** | ตรงกับส่วนต่างช่วงเทียบเท่า |

ส่วนสุดท้ายเป็น “กล่องรวม” ไม่ใช่ผลการต่อรองราคาล้วน จึงต้องมี Finance bridge และ
scope normalization ก่อนนำไป claim

### 2.3 KPI tree ที่แนะนำ

Primary outcomes:

1. `Finance-approved Net Saving` — KPI ผลสำเร็จทางการเงิน
2. `Comparable Cost Exposure Reduction %` — leading indicator ที่รวมภาระผูกพัน
3. `Critical/Statutory Compliance %` — guardrail ที่ต้องไม่ลดลง

Diagnostic drivers:

- Work order volume, cost/job และ price variance ต่อ comparable job
- Repeat 30/60/90 วัน, First-time fix และ reopen
- SLA met, downtime และ overdue
- Self/remote resolution, avoided dispatch และ escalation compliance
- Warranty recovery, duplicate billing และ invoice rejection

Data trust guardrails:

- Service ID uniqueness = 100%
- PM/CM coverage ≥ 98%
- Meaningful symptom coverage ≥ 95%
- Asset match ≥ 98%
- Vendor/SAP match ≥ 98%
- Finance reconciliation variance ≤ 1%
- Source freshness ตาม SLA ที่ตกลงร่วมกัน

## 3. แผนดำเนินงาน 5 เฟส

### Phase 0 — Decision lock (สัปดาห์ 1)

เป้าหมาย: ปิดนิยามก่อนเขียน Dashboard production

ดำเนินการ:

1. Finance ระบุรายการที่รวม/ไม่รวมใน Baseline 2025 และเหตุผลของ baseline
   12.590M, 15.359M และ 15.332M
2. Maintenance owner ยืนยัน grain ว่า 1 Service ID คือหนึ่งงานจริง และ PMORDER
   ไม่ได้รวมหลาย invoice line
3. Data owner กำหนด `LatestCompleteDate`, timezone Asia/Bangkok และกฎ period lock
4. HSE/Legal อนุมัติขอบเขต L0/L1/L2/L3 ของ Self Maintenance
5. Sponsor แต่งตั้ง KPI owner, Data owner, Finance approver และ Release owner

Exit criteria:

- Baseline dictionary และ exclusion list ลงนาม
- KPI dictionary v1 ลงนาม
- Finance bridge template และ Saving ledger ได้ owner
- ไม่มี KPI “Saving” ที่แสดงค่าเมื่อ gate ยัง blocked

### Phase 1 — Data quality recovery (สัปดาห์ 1-3)

เป้าหมาย: ทำให้ข้อมูลอธิบายสาเหตุและ trace กลับได้

ดำเนินการตามลำดับ:

1. บังคับเลือก Symptom code ก่อน dispatch และห้ามใช้ “อื่น ๆ” โดยไม่มี review queue
2. บังคับ Asset ID ก่อน technical close สำหรับอุปกรณ์ที่มีทะเบียน
3. ทำ Vendor master และ mapping code สำหรับ 136 แถวที่ยังไม่มี Vendor code
4. แก้ date-sequence exception 4 จุดและเพิ่ม automated test
5. แยก free text ออกจาก code; เก็บ text เป็นหลักฐานแต่ไม่ใช้เป็น primary grouping
6. เพิ่ม `SourceUpdatedAt`, `ExtractedAt`, `IsPeriodComplete`, `IsFinanceLocked`
7. สร้าง reconciliation table ระหว่าง Service, SAP actual, Commitment, Accrual

Exit criteria:

- Meaningful symptom coverage ≥ 95%
- Asset match ≥ 90% ใน pilot และแผนขึ้น ≥ 98% ก่อน scale
- Vendor/SAP match ≥ 98%
- Duplicate Service ID = 0 และ date sequence violation = 0
- Finance variance ≤ 1% สำหรับเดือนที่ lock แล้ว

### Phase 2 — Semantic model & Executive MVP (สัปดาห์ 3-5)

เป้าหมาย: ให้ผู้บริหารเห็นสถานะ เงิน และคันโยกใน 60 วินาที

ส่งมอบ Power BI 5 หน้าแรก:

1. `Executive Saving Control Tower`
2. `Cost & Work Mix`
3. `Engineering Cost Drivers`
4. `Data Trust & Reconciliation`
5. `Action Register`

กติกา model:

- Star schema; ห้าม join fact-to-fact โดยตรง
- แยก Service Order, Cost Transaction, Commitment, Accrual และ Saving Ledger
- ทุก measure ใช้ DimDate เดียวและ cutoff เดียว
- tooltip ทุก KPI ระบุสูตร, หน่วย, filter, completeness และ refresh
- Official saving คืนค่า blank เมื่อ Finance/DQ gate ไม่ผ่าน

Exit criteria:

- Cards, charts และ detail table reconcile ภายใต้ filter เดียวกัน
- UAT 10 test cases ผ่าน
- Mobile layout และ bookmark `Reset to approved view` ผ่านการทดสอบ
- Performance Analyzer: หน้า Executive พร้อมใช้งานในเวลาที่ทีมกำหนด

### Phase 3 — Engineering pilot (สัปดาห์ 5-8)

ขอบเขต pilot:

- ตู้จ่ายน้ำมัน: แม่ปั๊ม/มิเตอร์, มอเตอร์/สายพาน, สายยาง, มือจ่าย, การแสดงผล
- ถังน้ำมัน: เริ่มจาก triage/data capture; งานเสี่ยงและ statutory ต้อง escalate

คันโยก:

1. Mandatory triage + ภาพ/รหัสอาการก่อน dispatch
2. ตรวจ Warranty และงานซ้ำ 90 วันก่อนเปิด PO
3. RCA เมื่อ Asset เดิมซ้ำ 2 ครั้งใน 90 วัน
4. Rate card แยก labor/travel/parts และเปรียบเทียบ comparable scope
5. Pilot Self Maintenance เฉพาะ L0/L1 ที่มี SOP และ guardrail
6. Saving ledger ทุก action พร้อม counterfactual และ evidence URL

Exit criteria:

- Pilot ticket มี Asset ID ≥ 90% และมี Symptom code ≥ 95%
- Saving evidence completeness = 100%
- Reopen 30 วันและ Safety incident ไม่แย่กว่า guardrail
- Finance อนุมัติ/ปฏิเสธ saving ได้เป็นรายรายการ

### Phase 4 — Scale & automation (สัปดาห์ 9-12)

ดำเนินการ:

- Vendor scorecard, warranty recovery และ price variance
- Repeat Repair/Bad Actor, MTBF และ Repair-vs-Replace NPV
- PM/legal calendar และ geographic bundling
- Power Automate alert สำหรับ SLA, repeat, missing code และ action due
- Deployment pipeline DEV → TEST → PROD และ release checklist
- Incremental refresh; ใช้ near-real-time เฉพาะ source ที่มี SLA ต้องการจริง

Exit criteria:

- Monthly Finance-approved saving มี trend และ forecast
- Data quality gate ผ่านต่อเนื่อง 2 รอบ lock
- Guardrails ผ่านและมี owner แก้ exception
- Production workspace, RLS, refresh owner และ rollback process พร้อม

## 4. Dashboard architecture ปลายทาง

| Page | คำถามที่ต้องตอบ | Visual หลัก | Action |
|---|---|---|---|
| Executive Control Tower | ประหยัดจริงหรือยัง และเชื่อได้แค่ไหน | KPI strip, comparable run-rate, target/status | เปิด action ที่กระทบ gap สูงสุด |
| Cost & Work Mix | เงินเปลี่ยนเพราะ volume, mix หรือ rate | grouped bars, decomposition waterfall | เลือก work type/period เพื่อเจาะต่อ |
| Engineering Drivers | ระบบ/อาการใดกินเงินและเกิดซ้ำ | Pareto, ranked bars, later asset scatter | เปิด RCA / repair-vs-replace |
| SLA & Reliability | งานใดกระทบ downtime/ลูกค้า | SLA bars, repeat trend, overdue table | assign owner และ due date |
| Self Maintenance | งานใดทำเองได้อย่างปลอดภัย | stage bars/funnel + guardrails | เปิด SOP หรือ escalate |
| Vendor & Warranty | ใครแพง/ซ้ำ/ช้าเมื่อเทียบ scope เดียวกัน | normalized scorecard | negotiate / claim warranty |
| PM & Legal | งานบังคับครบและ bundle ได้หรือไม่ | calendar/heatmap | schedule/route bundle |
| Budget & Exposure | Actual + commitment + accrual อยู่ตรงไหน | bridge and forecast | correct commitment/accrual |
| Data Trust | ตัวเลขหน้าไหนยังไม่ควรเชื่อ | gate scorecard + reconciliation | เปิด exception queue |
| Repair History | หลักฐานระดับงานคืออะไร | drill-through table | audit/close action |

## 5. สิ่งที่ต้องเพิ่มจาก Excel Rev.1

Priority 0 — ต้องมีก่อน claim saving:

- Cost transaction line, document/invoice ID, posting date และ reversal
- Commitment/PO/PR, Accrual และ Finance control total
- Finance lock, SourceUpdatedAt และ extract timestamp
- Saving ID, counterfactual, actual, implementation cost และ approval status

Priority 1 — ต้องมีก่อน reliability analytics:

- Asset master key และ asset category hierarchy
- Root Cause code, Resolution code และ Parts used
- Action/outcome/reopen timestamps
- Warranty and comparable job scope

Priority 2 — สำหรับ optimization:

- Asset criticality, replacement value และ downtime cost
- Travel/labor/parts split
- Latitude/longitude หรือ route zone ที่ผ่าน governance
- SOP version และ Self Maintenance evidence

## 6. วิธีนำเสนอกรรมการ 5-7 นาที

1. เปิดด้วยเงิน: “H1 ลดเชิงคำนวณ 43.55% แต่เรายังไม่ claim จนกว่า exposure และ
   Finance gate จะผ่าน”
2. แสดงความน่าเชื่อถือ: 2 จาก 8 gates ผ่าน, 1 blocked และ 5 fail
3. แสดงคันโยก: 90.72% ของต้นทุนอยู่ในสองระบบหลัก
4. แสดงตรรกะ: volume อธิบายเพียง 0.745M; ส่วนใหญ่ยังอยู่ใน cost/job + scope
5. เสนอ pilot: 12 สัปดาห์ มี owner, exit criteria และ safety guardrail
6. ปิดด้วยคำขออนุมัติ: baseline owner, data capture rule และ pilot resources

ประโยคสำคัญบนเวที:

> Dashboard นี้ไม่ได้ทำให้ตัวเลขสวยขึ้น แต่ทำให้ทุกบาทมีที่มา ทุก saving มีหลักฐาน
> และทุก action มี owner

## 7. หลักฐานและไฟล์ที่ใช้ต่อ

- Aggregate profile: `analysis/data-profile.json`
- Public mockup data: `data/dashboard-data.json`
- Rebuild script: `tools/build_analytics_assets.py`
- Validation gate: `tools/validate_analytics_assets.py`
- Power BI model/DAX: ดูไฟล์ใน `powerbi/`
- Interactive mockup: `index.html`

ไฟล์ Excel/PBIX/PDF/DOCX เป็น source ส่วนตัวและถูก `.gitignore`; ห้ามนำขึ้น
Public repository หรือฝังใน Vercel deployment
