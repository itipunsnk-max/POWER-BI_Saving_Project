# Executive Dashboard Storytelling & UX Review

วันที่ทบทวน: 7 สิงหาคม 2026

บทบาท: Executive dashboard UX / storytelling reviewer

สถานะเอกสาร: Design direction — **ไม่ใช่การรับรองตัวเลข Saving ทางการเงิน**

## 1. ขอบเขตและหลักคุ้มครองข้อมูล

ทบทวน `README.md`, `index.html`, `styles.css`, เอกสาร `docs/01` ถึง `docs/06`,
data contract/DAX ที่เกี่ยวข้อง และ workbook `service_tracking_cleaned-Rev.1.xlsx`
แบบ read-only

หลักฐานจาก Excel ในเอกสารนี้ใช้เฉพาะ schema และ aggregate:

- ไม่แสดง Service ID, Site, Vendor, Technician, Asset หรือข้อความรายละเอียดรายงานรายแถว
- ไม่แสดงตัวอย่าง raw record
- กลุ่มย่อยที่มีจำนวนน้อยกว่า 5 รายการไม่ใช้เป็นหลักฐานเชิงเล่าเรื่อง
- ตัวเลขทางการเงินทั้งหมดต้องถือเป็น `Observed aggregate` จนกว่า Finance จะ reconcile และ lock
- Mockup สาธารณะควรใช้ข้อมูล aggregate ที่ sanitize แล้วหรือ synthetic data เท่านั้น

## 2. Executive verdict

แนวคิดเดิมแข็งแรงกว่ารายงานลดต้นทุนทั่วไป เพราะยอมรับตรง ๆ ว่า “ยอดลดลง”
ยังไม่เท่ากับ “Saving ที่พิสูจน์แล้ว” และมี safety/legal guardrail อยู่ในแกนงาน
อย่างไรก็ดี หน้าเว็บปัจจุบันยังเล่าแบบ brochure และรายการสิ่งที่จะสร้าง มากกว่า
การพากรรมการผ่านการตัดสินใจหนึ่งชุดแบบจบวงจร

ข้อเสนอแกนเรื่องใหม่:

> **Trust → Focus → Engineer → Act → Validate**
>
> เชื่อข้อมูลให้ได้ก่อน → โฟกัสความสูญเสียที่มีนัยสำคัญ → ใช้ตรรกะวิศวกรรมเลือกวิธีแก้ →
> มอบหมายและติดตาม → รับรู้เป็น Saving เฉพาะส่วนที่มีหลักฐานและผ่าน Finance

ประโยคเปิดที่แนะนำ:

> “วันนี้เรายังไม่ขอประกาศว่าลดได้ 20% เราขอแสดงให้เห็นว่าเงินรั่วอยู่ที่ไหน
> เหตุขัดข้องแบบใดควรแก้ก่อน ใครต้องทำอะไร และ Saving ส่วนใดพิสูจน์ได้แล้ว”

นี่เป็นจุดต่างที่น่าจดจำ: โครงการไม่ใช่ “dashboard สวย” แต่เป็น
**closed-loop engineering and financial control system**

## 3. Evidence map จาก workbook — aggregate เท่านั้น

### 3.1 ภาพรวมแหล่งข้อมูล

| หลักฐาน | Aggregate ที่ตรวจได้ | ความหมายต่อ UX/Story |
|---|---:|---|
| `Clean_Data` | 1,586 รายการ, 52 ฟิลด์ | เพียงพอสำหรับ prototype ระดับ portfolio แต่ยังไม่ใช่ saving ledger |
| ช่วง `SERVICE_DATE` | 25 ธ.ค. 2024–29 มิ.ย. 2026 | ต้องแสดง `Latest available service date`; มี 1 แถวปี 2024 ที่ควรตรวจ scope |
| Service ID | ครบ 100%, ไม่พบ ID ซ้ำ | เป็น positive trust signal ที่แสดงได้ |
| Amount | มีค่าตัวเลขครบ 100% | ใช้ทำ cost concentration ได้ แต่ยังไม่ยืนยันว่าเป็น Actual + Commitment + Accrual |
| Asset | ครบ 10.72% (170/1,586 แถว) | ยังไม่ควรประกาศ Bad Actor, Repeat by Asset หรือ Repair-vs-Replace เป็น production KPI |
| Problem detail | ครบ 86.70% | กลุ่ม missing ยังมีผลกระทบสูง ต้องมี Unknown queue |
| Site master | 35 Site IDs ผูกกับหลายชื่อ | ต้อง standardize master ก่อนใช้ ranking/location accountability |
| Timestamp sequence | พบ anomaly เล็กน้อย | ควรมี lifecycle validation ไม่ควรซ่อนเป็นค่าเฉลี่ย |

### 3.2 สัญญาณธุรกิจและวิศวกรรมที่ใช้เล่าเรื่องได้

| Signal | Observed aggregate | วิธีเล่าอย่างไม่เกินหลักฐาน |
|---|---:|---|
| Corrective work | 89.09% ของรายการ และ 88.52% ของมูลค่า | “Portfolio ถูกครอบด้วยงานแก้เสีย” ไม่ใช่ “PM ไม่มีประสิทธิภาพ” |
| Cost concentration | 10% รายการมูลค่าสูงสุดคิดเป็น 43.58% ของมูลค่า | แสดงว่าการจัดลำดับเป้าหมายมี leverage สูง |
| ตู้จ่ายน้ำมัน | 79.57% ของรายการ, 60.78% ของมูลค่า | เป็น high-frequency workstream สำหรับ standardization/triage |
| ถังน้ำมันใต้ดิน | 14.12% ของรายการ, 29.94% ของมูลค่า | เป็น lower-frequency, higher-cost/risk workstream; ให้ HSE/technical route นำ |
| Problem detail missing | 24.19% ของมูลค่า | Unknown เป็น workstream จริง ไม่ใช่เศษข้อมูล |
| ค่า “อื่น ๆ” | 15.15% ของมูลค่า | Missing + Other รวม 39.34%; Pareto ปัจจุบันยังไม่ actionable พอ |
| SLA `Missed` | 34.99% ของทุกแถว | ใช้เป็น signal เพื่อสอบสวน โดยต้องแสดง missing 8.58% และนิยาม denominator |

ยอด `จำนวนยอดเงิน` รวมตาม `SERVICE_DATE` ปี 2025 ใน workbook เท่ากับ
15,331,857.14 บาท ขณะที่เอกสารเดิมอ้าง Service baseline 15,359,352.14 บาท
ต่างกัน 27,495.00 บาท หรือประมาณ 0.18% ของยอดเอกสารเดิม แม้ต่ำกว่า gate 1%
แต่เป็นหลักฐานว่าหน้า Executive ต้องแสดง `Baseline version`, source และ lock date
เสมอ ส่วน Working baseline PM/CM 12,590,005.44 บาทยังเป็นคนละชุดนิยามและต้อง
reconcile ก่อนใช้ตัดสินเป้าหมาย 20%

### 3.3 สิ่งที่ workbook ยังพิสูจน์ไม่ได้

- Finance-approved net saving
- Actual + Open Commitment + Accrual แบบไม่ซ้ำกัน
- Counterfactual และ implementation cost ของแต่ละ saving event
- Repeat repair ที่เชื่อถือได้ในระดับ Asset เพราะ Asset coverage ต่ำ
- First-time fix, reopen, avoided dispatch และ self-maintenance funnel
- Warranty recovery และ repair-vs-replace economics
- Statutory compliance จาก fact ที่มี due date/evidence ครบ

เมื่อ field/fact ยังไม่มี ให้ UI แสดง `ยังไม่มีข้อมูลตาม data contract` ไม่ใช้เลขศูนย์
เพราะศูนย์สื่อว่ามีการวัดแล้วและผลเท่ากับศูนย์

## 4. Review ของของเดิม

### 4.1 จุดแข็งที่ควรรักษา

- `README.md` วาง Data Quality Gate, baseline mismatch และ Finance lock อย่างตรงไปตรงมา
- Blueprint เชื่อม executive KPI ไปยัง Pareto, bad actor, self maintenance และ action owner
- มี data contract, DAX ตั้งต้น, saving ledger concept และ UAT cases
- Self Maintenance มี L0–L3 และ red flags ที่ไม่ยอมให้ Saving อยู่เหนือ safety/legal
- `index.html` มี hero message จำง่าย, responsive structure, semantic section, alt text และ nav label
- Visual identity navy/cyan ให้บุคลิก technical/modern เหมาะกับ control tower

### 4.2 ช่องว่างที่ลดพลังการนำเสนอ

1. **เป้าหมายกับผลลัพธ์อยู่ใกล้กันเกินไป** — ตัวเลข 20%, 2.518M และ allocation
   อาจถูกตีความว่าเป็น Saving ที่เกิดแล้ว ต้องติดป้าย `Target allocation` ชัดเจน
2. **10 หน้าเป็น product backlog ไม่ใช่ pitch flow** — กรรมการไม่ควรจำชื่อหน้า
   แต่ควรจำ decision loop หนึ่งเส้น
3. **Data Quality อยู่ปลายทาง** — ในการนำเสนอควรอยู่เป็น confidence strip ทุกหน้า
   และมี Trust Center สำหรับตรวจลึก
4. **ไม่มี evidence-state grammar** — Observed, Target, Hypothesis, Draft และ Approved
   ต้องแยกด้วยคำ สี รูปทรง และ tooltip
5. **หน้าเว็บยังไม่มี interaction model** — เป็น landing page ที่อ่านได้ดี แต่ยังไม่สาธิต
   filter → diagnose → assign → verify
6. **หลักฐานล่าสุดเปลี่ยนแล้ว** — workbook ใหม่มี coverage/aggregate ต่างจากเอกสารบางจุด
   จึงต้อง version source และไม่ hard-code claim เก่าใน mockup
7. **Asset coverage ต่ำ** — หน้า Bad Actor ที่ดู “เทพ” แต่ใช้ Asset เพียงประมาณหนึ่งในสิบของงาน
   จะทำลายความเชื่อถือมากกว่าสร้างความประทับใจ

## 5. Evidence-state grammar

ทุก KPI, chart annotation และ action ควรมีสถานะหนึ่งเดียว:

| State | ความหมาย | การแสดงผล |
|---|---|---|
| `Observed` | รวมจาก source ตาม filter ปัจจุบัน | ป้าย `Observed`; แสดง source date |
| `Derived` | คำนวณจาก observed fields ด้วยสูตรที่นิยามแล้ว | ป้าย `Calculated`; tooltip มีสูตร/denominator |
| `Target` | เป้าหมายที่ผู้บริหารกำหนด | เส้น/กรอบ target และคำว่า `Target`; ห้ามใช้คำว่า achieved |
| `Hypothesis` | โอกาสหรือ expected saving ที่ยังไม่พิสูจน์ | เส้นประ/พื้นโปร่ง; owner + assumption |
| `Draft evidence` | มีหลักฐานบางส่วนแต่ Finance ยังไม่อนุมัติ | แสดงแยกจาก approved ห้ามรวมใน hero saving |
| `Finance-approved` | ผ่าน evidence, reconciliation และ finance lock | olive/dark mark + check icon + approval month |
| `Blocked` | ไม่ผ่าน DQ, finance หรือ safety gate | ป้าย BLOCKED + เหตุผล + next action |

Default ของหน้า Executive ต้องเป็น `Finance-approved`; ผู้ใช้เปิด layer Draft/Hypothesis
เพิ่มได้ แต่ UI ต้องไม่รวม layer เหล่านั้นในตัวเลข headline โดยเงียบ ๆ

## 6. Information architecture ที่แนะนำ

ลด navigation สำหรับ pitch และ executive use เหลือ 5 หน้าหลัก พร้อม drill-through:

```text
01 DECIDE — Executive Control Tower
   ├─ Can we claim the target?
   ├─ What decision is required today?
   └─ What is blocked and why?

02 FOCUS — Opportunity & Reliability
   ├─ Where is cost/failure concentrated?
   ├─ High-frequency vs high-consequence workstreams
   └─ Unknown coding queue

03 ACT — Engineering Action Portfolio
   ├─ Intervention, owner, due date
   ├─ Expected vs validated impact
   └─ Evidence and next review

04 PROTECT — Safety, SLA & Legal Guardrails
   ├─ Red flags / statutory route
   ├─ SLA and reopen guardrails
   └─ Self-maintenance eligibility when fact becomes available

05 TRUST — Data Quality & Reconciliation
   ├─ Baseline/source/lock
   ├─ Coverage, mappings, lifecycle validity
   └─ Issue queue and gate owner

Hidden drill-through
   ├─ Sanitized service/asset history for authorized Power BI users
   ├─ Vendor/price detail under RLS
   └─ Metric definition and evidence lineage
```

หน้า PM/CM, Vendor, PM/Legal และ Budget เดิมยังอยู่ได้ใน Production แต่ควรเป็น
diagnostic tabs/drill-through ภายใต้ 5 คำถามข้างต้น ไม่ใช่ 10 รายการที่มีน้ำหนักเท่ากัน
บนเส้นทางนำเสนอ

## 7. 5–7 minute pitch flow

เป้าหมายเวลา: 6 นาที 30 วินาที เหลือ buffer สำหรับคำถาม

| เวลา | หน้าจอ/การกระทำ | สิ่งที่พูด | หลักฐานหรือการตัดสินใจ |
|---|---|---|---|
| 0:00–0:35 | Cover → Decision banner | “เราไม่ได้สร้าง dashboard เพื่อบอกว่ายอดลด แต่สร้างระบบที่พิสูจน์ได้ว่าอะไรประหยัดจริง” | วาง credibility ก่อน wow |
| 0:35–1:20 | Page 01: Evidence gate | “วันนี้ยังประกาศ 20% ไม่ได้ เพราะ baseline ยังมีหลายนิยามและ cost exposure ยังไม่ครบ” | ขออนุมัติ baseline owner/lock rule |
| 1:20–2:15 | Page 02: Concentration | “Corrective ครอง 88.52% ของมูลค่า และ 10% งานบนสุดกิน 43.58%” | ชี้ว่าการจัดลำดับมี leverage |
| 2:15–3:20 | Page 02: Engineering matrix | “ตู้จ่ายเป็น high-frequency; ถังเป็น high-cost/high-consequence จึงไม่ใช้มาตรการเดียวกัน” | เลือก standardization/triage เทียบกับ HSE/technical route |
| 3:20–4:30 | Page 03: Action portfolio | คลิกกลุ่มหนึ่ง → เปิด action drawer ที่มี owner, due, expected impact, evidence | เปลี่ยน insight เป็นงานรับผิดชอบ |
| 4:30–5:25 | Page 04: Guardrails | “ประหยัดไม่ถือว่าสำเร็จถ้า legal compliance, safety, reopen หรือ emergency downtime แย่ลง” | ยืนยัน no-compromise constraints |
| 5:25–6:05 | Page 05: Trust/ledger | “ระบบ bank Saving เฉพาะรายการที่มี counterfactual, actual, cost และ Finance approval” | แยก Draft/Approved/Reversed |
| 6:05–6:30 | กลับ Page 01 | “สิ่งที่ขอวันนี้คือ lock baseline, ปิด asset/symptom gaps และ pilot 2 workstreams” | จบด้วย decision ask 3 ข้อ |

หากมีเวลาเพียง 5 นาที ตัดรายละเอียด Page 04 เหลือ guardrail strip และเปิด Page 05
เฉพาะ reconciliation bridge; ห้ามตัดคำอธิบายเรื่อง provisional/approved

## 8. Page wireframes

### Page 01 — Executive Control Tower / “ตัดสินใจอะไรวันนี้”

```text
┌ Baseline v__ │ Latest complete __ │ Finance lock __ │ Data confidence: BLOCKED ┐
├───────────────────────────────────────────────────────────────────────────────┤
│ DECISION BANNER: ยังไม่พร้อมประกาศ 20% — 3 blockers / 3 decisions required  │
├──────────────┬──────────────┬──────────────┬──────────────┬───────────────────┤
│ Approved Net │ Cost Exposure│ Gap to Target│ Guardrails   │ Evidence coverage │
│ Saving       │ vs Comparable│ Provisional  │ 0 breach / ? │ reason + owner    │
├─────────────────────────────────────────────┬─────────────────────────────────┤
│ Monthly Exposure vs Baseline/Target         │ Reconciliation waterfall        │
│ [8–12+ periods, locked period marker]       │ Service→Actual→Commit→Accrual   │
├─────────────────────────────────────────────┴─────────────────────────────────┤
│ TOP ACTIONS: issue / owner / due / expected / approved / next review          │
└───────────────────────────────────────────────────────────────────────────────┘
```

Hero card ที่ยังไม่มี fact ให้แสดง `Not yet measured` พร้อม link ไป data contract
ไม่แสดง `฿0` และไม่ใช้สีเขียวทั้งหน้าเพียงเพราะ Actual ต่ำกว่าปีก่อน

### Page 02 — Opportunity & Reliability / “แก้อะไรก่อน”

```text
┌ Corrective value 88.52% │ Top 10% jobs = 43.58% value │ Asset coverage 10.72% ┐
├─────────────────────────────────────────┬─────────────────────────────────────┤
│ Frequency × Cost × Consequence matrix   │ Cost Pareto by standardized symptom│
│ High freq: dispenser standardization    │ Unknown/Other always visible       │
│ High consequence: tank/HSE route        │ cumulative line + exact denominator│
├─────────────────────────────────────────┴─────────────────────────────────────┤
│ ENGINEERING DECISION RULE: route / RCA / standardize / repair-replace / code │
└───────────────────────────────────────────────────────────────────────────────┘
```

เมื่อ Asset coverage ยังต่ำ ให้ใช้ grain `Problem type × Problem detail × period`
ก่อน ห้ามใช้ Asset bubble chart เป็น hero visual

### Page 03 — Engineering Action Portfolio / “ใครทำอะไร เมื่อไร”

```text
┌ Expected impact │ Draft evidence │ Approved saving │ Reversed │ Overdue actions ┐
├──────────────────────────────────────┬────────────────────────────────────────┤
│ Saving by lever: target/draft/approved│ 4-week action burn-up / due-date risk │
├──────────────────────────────────────┴────────────────────────────────────────┤
│ ACTION TABLE: priority / intervention / owner / due / confidence / evidence   │
│ click row → drawer: problem, engineering rule, before/after, guardrail, proof │
└───────────────────────────────────────────────────────────────────────────────┘
```

Action table เป็น visual หลักได้ เพราะหน้ามีจุดประสงค์เพื่อ lookup และ follow-up
ไม่ควรแปลงทุกอย่างเป็นกราฟ

### Page 04 — Safety, SLA & Legal Guardrails / “ประหยัดโดยไม่สร้างความเสี่ยง”

```text
┌ Safety incident │ Statutory compliance │ Emergency downtime │ Reopen 30D │ SLA ┐
├─────────────────────────────────────────┬─────────────────────────────────────┤
│ Guardrail trend + breach annotations    │ Work routing: L0 / L1 / L2 / L3     │
├─────────────────────────────────────────┴─────────────────────────────────────┤
│ RED FLAGS / breached cases / owner / containment / due date                  │
└───────────────────────────────────────────────────────────────────────────────┘
```

Self-maintenance funnel แสดงเมื่อมี `FactMaintenanceAction` ครบ ordered stages
เท่านั้น ระหว่างนี้ให้ mockup กล่อง contract/empty state แทน funnel ปลอม

### Page 05 — Trust Center / “ตัวเลขเชื่อได้แค่ไหน”

```text
┌ Source freshness │ Baseline version │ Finance lock │ Reconcile variance │ DQ gate ┐
├────────────────────────────────────────┬────────────────────────────────────────┤
│ Completeness heatmap by field × period │ Baseline/reconciliation bridge          │
├────────────────────────────────────────┴────────────────────────────────────────┤
│ ISSUE QUEUE: Asset missing / Unknown / site mapping / timestamp / owner / SLA    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

หน้า Trust ไม่ใช่หน้าสำหรับทีม BI เท่านั้น ผู้บริหารต้องเห็น blocker, impact และ owner
โดยไม่ต้องอ่านชื่อ field ทางเทคนิคจนกว่าจะ hover/click

## 9. Chart contracts

| ID | Analytical question / takeaway | Contract | Data gate และ honest fallback | Interaction/QA |
|---|---|---|---|---|
| C01 | Exposure เคลื่อนเข้าใกล้เพดาน 20% หรือไม่ | `line`; เดือน × Baseline comparable, Cost Exposure, Target; อย่างน้อย 8–12 จุด; locked period เป็น marker | ต้องมี Actual+Commitment+Accrual และ LatestCompleteDate; ถ้ามีไม่ถึง 8 จุดใช้ grouped bar/KPI | hover แสดงหน่วย, period state, source; เส้นใช้ style/marker ต่างกัน ไม่พึ่งสี |
| C02 | ยอด Service ไปจบที่ Finance total อย่างไร | `waterfall`; Service → exclusions → Actual → Commitment → Accrual → Finance control | Driver ต้องบวกกันได้จริง; หากยัง map ไม่ครบใช้ reconciliation table และ BLOCKED banner | exact labels, signed values, focused scale cue; Start/End neutral |
| C03 | กลุ่มใดสร้างมูลค่าสูงสุดและ coverage พอหรือยัง | sorted horizontal Pareto bar + cumulative line; standardized Problem detail; Top N + Other + Unknown | Unknown/Other ต้องไม่ถูกกรองทิ้ง; ถ้า taxonomy ยังไม่ sign-off ใช้ Problem type level | click bar cross-filter C04/action list; bar เริ่มศูนย์; denominator ชัด |
| C04 | ควรใช้ intervention แบบใดกับแต่ละ workstream | `scatter` ที่ grain เดียว: standardized symptom-period; x=frequency, y=cost/job หรือ exposure, size=total cost, style=consequence class | ต้องมีอย่างน้อย 12 กลุ่มที่เทียบกันได้; ถ้าน้อยหรือ definition ไม่พร้อมใช้ 2×2 matrix/ranked bars | label เฉพาะ outlier; tooltip มี n, amount, severity basis, data confidence |
| C05 | Opportunity กระจุกตัวมากเพียงใด | Pareto/concentration curve หรือ ranked bars; annotation “Top 10% jobs = 43.58% value” | ใช้ Amount observed เท่านั้นและติดป้ายไม่ใช่ Saving | filter period/work type; exact n และ total ใน subtitle |
| C06 | Lever ใดมี target, expected และ approved เท่าไร | grouped horizontal bar หรือ bullet chart ต่อ lever; Target, Hypothesis, Finance-approved แยก mark | ห้าม stack รวม target+expected+approved เพราะสถานะไม่ additive | click lever เปิด action portfolio; approved ใช้ solid, hypothesis ใช้ open/dashed |
| C07 | Saving เดินผ่าน evidence stage หรือค้างที่ใด | stage bars: Draft → Reviewed → Approved และ Reversed แยก; ใช้ funnel เฉพาะเมื่อเป็น cohort เดียวตามลำดับ | ต้องมี FactSavingLedger; ถ้ายังไม่มีใช้ empty state/data contract | filter by approval month/lever; ไม่รวม Reversed ใน Net Saving |
| C08 | SLA miss อยู่ที่ scope ใดและน่าเชื่อแค่ไหน | horizontal bars ตาม workstream/period; Met, Missed, Missing แยก | ยืนยัน SLA clock/eligibility; current signal 34.99% missed ใช้เพื่อ investigate ไม่ใช่ blame vendor | display denominator และ missing; ไม่ใช้ gauge/red-only |
| C09 | Field ใดทำให้ decision ถูก block | heatmap `field × period/workstream` ด้วย completeness/validity; issue count ข้างเคียง | target threshold ต้องมี owner; Asset coverage 10.72% แสดงตรง ๆ | click cell เปิด sanitized issue queue; มีตัวเลข/สัญลักษณ์แทนสี |
| C10 | Guardrail เสียหลัง intervention หรือไม่ | highlighted line/dot by locked period; Safety, compliance, reopen, emergency downtime แยก panel | ห้ามรวมต่างหน่วยบนแกนเดียว; fact ไม่พร้อมให้ N/A | breach annotation + owner; zero-event metricต้องแสดง coverage ด้วย |

Chart title ใช้ชื่ออธิบายสิ่งที่ plot เช่น “Monthly cost exposure vs target”
ส่วนข้อสรุปใช้ subtitle/callout ที่ผูกกับ evidence state ไม่ใช้ headline เชิงชัยชนะ
หากยังไม่มีหลักฐาน

## 10. Color system และ accessibility

### 10.1 สิ่งที่ตรวจพบใน CSS เดิม

โครง responsive และตัวอักษรหลักอ่านง่าย แต่สี accent บางคู่ไม่ผ่าน WCAG AA
สำหรับข้อความปกติ:

| คู่สีเดิม | Contrast โดยประมาณ | ข้อสรุป |
|---|---:|---|
| Cyan `#16C5FF` บนขาว | 2.01:1 | ไม่ผ่านทั้งข้อความปกติและ graphical object สำคัญ |
| Cyan `#16C5FF` บน Navy `#071B3F` | 8.46:1 | ผ่าน ใช้เป็น accent บนพื้นมืดได้ |
| Eyebrow `#1689BF` บนขาว | 3.91:1 | ไม่ผ่านข้อความ 12px |
| Warning text `#C45120` บน `#FFF8F3` | 4.39:1 | ต่ำกว่า 4.5:1 เล็กน้อย |
| Timeline text `#117BB2` บน `#F2F6FB` | 4.30:1 | ต่ำกว่า 4.5:1 |
| Risk red `#D9342B` บน `#FFF4F3` | 4.35:1 | ต่ำกว่า 4.5:1 |

### 10.2 Palette ที่แนะนำ

| Role | Color | Contrast บนขาว | การใช้ |
|---|---|---:|---|
| Ink / Actual | `#0B1F3A` | 16.52:1 | Actual, headline, axes |
| Target / controlled accent | `#007A9E` | 4.91:1 | Target line/text บนพื้นขาว |
| Exposure / warning | `#A54600` | 6.04:1 | Commitment/Accrual, warning |
| Risk / breach | `#B42318` | 6.57:1 | Safety/legal breach พร้อม icon/label |
| Finance-approved | `#3F6212` | 7.08:1 | Approved only; ไม่ใช้แทนคำว่า “ดี” ทุกกรณี |
| Neutral / Draft | `#475467` | 7.69:1 | Draft, missing, secondary labels |
| Brand cyan | `#16C5FF` | ผ่านบน navy | ใช้บน dark hero, decorative accent ที่ไม่ใช่ข้อมูลสำคัญบนขาว |

กฎการใช้:

- ใช้ `single-root preferred` สำหรับกราฟ single-series และไม่สร้าง legend ซ้ำกับ axis
- ใช้ไม่เกิน 2 non-neutral roots สำหรับ Actual vs Target หรือ positive/negative delta
- แยก series ด้วย line style, marker, fill, label และ order ไม่ใช้สีอย่างเดียว
- ไม่ใช้ red/green เป็นคู่ผ่าน/ไม่ผ่านโดยลำพัง; เพิ่มคำ `BLOCKED`, `APPROVED`, icon และ pattern
- ขนาดข้อความทั่วไปอย่างน้อย 14px, tooltip/metadata อย่างน้อย 12px พร้อม contrast ผ่าน
- touch target อย่างน้อย 44×44px, focus ring ชัด, keyboard order ตรงกับ visual order
- รองรับ `prefers-reduced-motion`; transition ไม่เกิน 200ms และไม่มี parallax ที่รบกวน pitch
- ทดสอบที่ 1366×768, 1920×1080, tablet และ mobile; ห้ามบังคับให้กรรมการ scroll ก่อนเห็น decision banner

## 11. Mockup interaction contract

### 11.1 Global controls

1. `Period`: default = Latest complete/finance-locked period
2. `Scope`: All approved scope; รายละเอียดพื้นที่ใช้เฉพาะใน Power BI ที่มี RLS
3. `Work type`: All / Corrective / Preventive
4. `Evidence layer`: Approved (default) / +Draft / +Hypothesis
5. `Reset to approved view`: คืนค่าทุก filter และ bookmark

ทุกหน้าต้องแสดง filter context เป็นข้อความอ่านได้ และมี `Clear filter` ที่ keyboard
เข้าถึงได้ ห้ามซ่อน active cross-filter ไว้เฉพาะด้วยสีของกราฟ

### 11.2 Guided presentation mode สำหรับกรรมการ

- ปุ่ม `Start 6-minute story` เปิด step 1–6 พร้อม progress และปุ่ม Next/Back
- แต่ละ step เปลี่ยนเฉพาะ bookmark/filter ที่บันทึกไว้ ไม่สุ่ม animation
- มี speaker cue สั้นหนึ่งบรรทัด และ `Evidence` link สำหรับผู้ถามลึก
- ปุ่ม `Exit story` กลับ approved default โดยไม่ค้าง cross-filter
- Public/Vercel mockup แสดง banner `Sanitized aggregate prototype — not a live financial system`

### 11.3 Diagnostic interactions

- คลิก Pareto group → highlight matrix, action list และ guardrail ของ scope เดียวกัน
- คลิก `Unknown/Other` → เปิด data remediation queue ไม่พาไปหา Saving
- คลิก action → drawer มี problem statement, engineering rule, owner, due date,
  expected/approved value, evidence status และ next review
- Hover/Focus KPI → tooltip มี definition, numerator, denominator, date range,
  source, freshness, finance lock และ exclusions
- Compare mode ใช้ same-period/same-scope เท่านั้น และมี visible comparison label
- Drill-through detail มีเฉพาะผู้ใช้ที่ได้รับสิทธิ์; public mockup แสดง aggregate placeholder

### 11.4 Empty/error states

- `Not measured`: fact ยังไม่มีตาม data contract
- `Blocked`: มีข้อมูลแต่ไม่ผ่าน gate พร้อมเหตุผล/owner
- `No activity`: วัดแล้วและไม่มี event จริง
- `Refresh delayed`: source เกิน SLA; คงค่า last-known พร้อม timestamp และ warning
- `Filter yields small group`: suppress detail และบอกเหตุผลด้าน privacy

สถานะเหล่านี้ต้องไม่ถูกแสดงเป็น `0` เหมือนกันทั้งหมด

## 12. Engineering decision logic และ action loop

### 12.1 Safety-first routing

```text
Safety / statutory red flag?
  ├─ Yes → Stop / contain / L2-L3 qualified route; cost optimization is secondary
  └─ No
      ├─ High frequency + standard symptom → standard work / triage / PM redesign
      ├─ High repeat + known asset → RCA / bad-actor / repair-vs-replace
      ├─ High unit cost + vendor/part comparability → commercial benchmark / warranty
      ├─ Geographic/time clustering → bundle PM/legal route
      └─ Unknown or low-confidence data → coding remediation; no saving claim
```

หากต้องการใช้ FMEA/RPN ให้กำหนด Severity, Occurrence และ Detectability scale
ร่วมกับ HSE/Engineering ก่อน ห้ามสร้าง score สวย ๆ จาก field ที่ยังไม่มีนิยาม

สำหรับ expected financial opportunity ใช้แนวคิด:

`Expected net opportunity = Exposure × Preventability × Evidence confidence − Implementation cost`

โดย `Preventability` และ `Evidence confidence` เป็น hypothesis ที่ต้องแสดง assumption,
owner และ sensitivity; ไม่ใช่ Finance-approved Saving

### 12.2 Closed action loop

```text
OBSERVE → PRIORITIZE → DECIDE → ASSIGN → VERIFY → BANK → LEARN
   ↑                                                       │
   └──────── update standard / SOP / master / threshold ───┘
```

ขั้นต่ำของ action record:

- Problem/workstream และ evidence snapshot
- Engineering decision rule และ intervention
- Owner, due date, status, next review
- Expected gross saving, implementation cost, expected net saving
- Before/after denominator และ comparable period
- Safety/legal/SLA/reopen guardrails
- Evidence URL และ Finance state
- Reversal rule หากเกิด reopen, late invoice หรือ invalid counterfactual

Operating rhythm:

- Daily: refresh/DQ, safety red flag, overdue critical action
- Weekly: top opportunity, repeat/RCA, unknown queue, owner/due review
- Monthly: finance reconciliation, saving approval/reversal, forecast, standard update

## 13. Risk wording — พูดอย่างทรงพลังโดยไม่เกินหลักฐาน

| หลีกเลี่ยง | ใช้แทน | ต้องมีเพื่อเลื่อนไปเป็น claim ที่แรงขึ้น |
|---|---|---|
| “ลดได้ 50.04% แล้ว” | “Actual-only comparable cost ต่ำกว่าเดิม 50.04%; provisional pending commitment, accrual และ finance lock” | Exposure ครบ, period complete, baseline sign-off |
| “ประหยัดได้ 2.518 ล้านบาท” | “เป้าหมาย/target allocation 2.518 ล้านบาทตาม working baseline” | Finance-approved ledger รวมถึง implementation cost |
| “Top 5 นี้จะสร้าง Saving 7.52M” | “Top 5 เดิมมี cost concentration สูง จึงเป็น candidate สำหรับ pilot; potential ยังต้องพิสูจน์” | Standard taxonomy, preventability, counterfactual |
| “Bad actor asset” | “Asset-level analysis ยัง blocked เพราะ Asset coverage 10.72%” | Asset match ตาม threshold ที่อนุมัติและ repeat logic |
| “Self maintenance ลดค่า dispatch” | “งาน L0/L1 ที่เข้าเกณฑ์ SOP อาจลด dispatch; รับรู้เมื่อไม่ reopen และผ่าน guardrail” | FactMaintenanceAction, approved SOP, standard/actual cost |
| “Real-time dashboard” | “Source A refreshed ทุก X นาที; SAP/Finance เป็น batch และแสดงเวลาของแต่ละ source” | Refresh audit และ measured SLA |
| “Vendor A ทำผลงานแย่” | “Scope นี้มี SLA miss signal ภายใต้นิยาม/coverage ปัจจุบัน ต้องตรวจ mix และ denominator” | Eligible SLA clock, severity mix, sample size |
| “ข้อมูลครบ” | “Service ID และ amount ครบ; Asset/problem/lifecycle coverage ยังต่างกันตาม field” | Field-level DQ scorecard |
| “Unknown ไม่มีผล” | “Missing/Other มี 39.34% ของมูลค่ารวมใน problem detail และเป็น priority data workstream” | Coding owner, queue SLA, approved master |

## 14. Judging criteria และ proof ที่ควรเตรียม

เสนอ rubric 100 คะแนนเพื่อซ้อมก่อนนำเสนอ:

| เกณฑ์ | น้ำหนัก | กรรมการควรเห็น | Acceptance evidence |
|---|---:|---|---|
| Evidence integrity | 20 | Target/Draft/Approved แยก, baseline version, finance lock | Reconciliation bridge, KPI dictionary, no silent filter |
| Decision usefulness | 20 | รู้ภายใน 30 วินาทีว่าต้องตัดสินใจอะไร | Decision banner + top 3 actions/owners |
| Engineering depth | 20 | Intervention ต่างกันตาม frequency/cost/consequence | Decision matrix, RCA/FMEA rule, repair-vs-replace gate |
| Business impact | 15 | Opportunity concentration และ path to validated saving | Cost Pareto + saving ledger + implementation cost |
| Actionability/adoption | 10 | Insight เปลี่ยนเป็น owner/due/evidence | Action drawer, weekly/monthly loop |
| Safety/legal/control | 5 | Saving ไม่ override safety/statutory | L0–L3 routing, guardrail breach behavior |
| UX/accessibility | 5 | อ่านเร็ว, keyboard/mobile, color-safe | Contrast test, responsive/presentation-mode QA |
| Scalability/governance | 5 | DEV/TEST/PROD, RLS, source lineage | Release/UAT/data-owner evidence |

Red-team questions ที่ต้องตอบได้:

1. ถ้า invoice มาช้า Saving ย้อนกลับอย่างไร?
2. ทำไม baseline สองชุดต่างกัน และชุดไหนเป็น official?
3. จะรู้ได้อย่างไรว่าต้นทุนลดเพราะ intervention ไม่ใช่ volume/scope ลด?
4. ถ้า Asset coverage ต่ำ จะเชื่อ repeat repair ได้อย่างไร?
5. Self Maintenance ใครอนุมัติ และหยุดที่เส้นใด?
6. ทำไมถังน้ำมันใต้ดินไม่ใช้แนวทางเดียวกับตู้จ่าย?
7. ตัวเลขใดเป็น target, observed, hypothesis และ Finance-approved?
8. ผู้บริหารต้องตัดสินใจอะไรจากหน้าจอนี้ภายในวันนี้?

## 15. Mockup และ dashboard QA contract

### Pitch-ready

- เปิดแล้วเห็น decision banner, evidence state และ latest complete date โดยไม่ scroll
- Guided story จบใน 5–7 นาทีและ Reset ได้เสมอ
- ทุกตัวเลขใน mockup ใช้ sanitized aggregate/synthetic data และมี label
- ไม่มีชื่อ Site/Vendor/Technician/Service/Asset ใน public build
- ค่า Target ไม่ถูกนับรวมกับ Approved
- Unknown/Other ไม่หายเมื่อ filter
- สี/ข้อความผ่าน contrast และใช้ keyboard ได้
- Responsive ที่ 1366×768 และ mobile โดย KPI ไม่ถูกตัด

### Production-ready

- Official baseline sign-off และ versioned exclusions
- Cost Exposure reconcile กับ Finance ภายใน threshold ที่อนุมัติ
- Saving ledger มี approval/reversal audit trail
- Asset/symptom/master coverage ผ่าน gate ก่อนเปิด asset-level claims
- UAT filter/reconciliation/RLS/partial-period/reopen ผ่าน
- Source refresh, Finance lock และ model version แสดงแยกกัน
- Performance: executive page usable ภายใน 3 วินาทีบน network องค์กรเป้าหมาย
- Accessibility: WCAG 2.1 AA สำหรับ text/non-text ที่สำคัญ

## 16. ลำดับดำเนินการที่แนะนำ

### Phase 0 — Evidence lock (1–3 วัน)

- ตั้ง official baseline owner/version และ reconcile 3 ตัวเลขที่ใช้อยู่
- ยืนยันนิยาม Amount ว่าเป็น actual หรือ exposure component ใด
- ใส่ evidence-state dictionary และ risk wording ใน KPI dictionary
- กำหนด public-data suppression policy

Exit: ทุก headline metric มี source, denominator, period, state และ owner

### Phase 1 — Executive story mockup (4–7 วัน)

- เปลี่ยน mockup เป็น 5-page IA และ guided 6-minute story
- ใช้ sanitized aggregate/synthetic dataset
- ทำ Decision banner, concentration, engineering matrix และ action drawer
- ปรับ palette/accessibility และ responsive QA

Exit: ผู้ทดสอบ 5 คนตอบได้ภายใน 30 วินาทีว่า status, blocker และ top action คืออะไร

### Phase 2 — Trusted Power BI MVP (2–3 สัปดาห์)

- สร้าง Cost Exposure/reconciliation และ Trust Center ก่อน headline Saving
- สร้าง standardized symptom/site master และ DQ queue
- เชื่อม action/saving ledger พร้อม approved/draft/reversal states
- UAT cross-filter, latest complete period, RLS และ export

Exit: finance varianceตาม threshold, metric reconcile ทุกหน้า และ approved saving trace ได้

### Phase 3 — Engineering pilot (4 สัปดาห์)

- Pilot สองเส้นทาง: ตู้จ่าย high-frequency กับถัง high-consequence
- ใช้ intervention และ guardrail ต่างกัน
- วัด before/after ด้วย comparable denominator และ implementation cost
- ปิด monthly Finance review แล้ว update SOP/standard

Exit: มีอย่างน้อยหนึ่ง closed-loop case ที่ trace จาก signal → action → evidence → approval/reversal ได้

## 17. Top recommendations

### P0 — ก่อนนำเสนอ claim

1. เปลี่ยน hero จาก “20% / 2.518M” เป็น `Decision + Evidence Gate`; เก็บ 20% เป็น Target
2. Reconcile workbook 2025, Service baseline และ PM/CM working baseline พร้อม version/lock date
3. แยก `Observed`, `Target`, `Hypothesis`, `Draft`, `Approved`, `Blocked` ในทุก visual
4. หยุด asset-level claim จน Asset coverage ผ่าน gate; เร่ง Asset master และ Unknown/Other queue

### P1 — เพื่อชนะใจกรรมการ

5. ใช้เรื่อง `Trust → Focus → Engineer → Act → Validate` และ pitch 6:30 นาที
6. เล่า engineering split ให้คม: ตู้จ่าย = high-frequency standardization;
   ถัง = high-cost/high-consequence HSE route
7. ทำ action drawer/ledger ให้เห็น owner, due, expected, approved, evidence และ reversal
8. แสดง cost concentration พร้อม guardrail ไม่โชว์กราฟจำนวนมากที่ไม่มี decision

### P2 — เพื่อยกระดับ UX

9. ลด 10 หน้าเป็น 5 executive questions + hidden drill-through
10. ปรับ cyan/orange/red บนพื้นขาวให้ผ่าน WCAG และไม่พึ่ง red/green
11. เพิ่ม guided presentation mode, Reset to approved view และ explicit empty/error states
12. ให้ public mockup ใช้ sanitized aggregate/synthetic data พร้อม prototype disclaimer

## 18. Closing line ที่แนะนำ

> “ความน่าเชื่อถือของโครงการนี้ไม่ได้อยู่ที่กราฟบอกว่าค่าใช้จ่ายลดลงเท่าไร
> แต่อยู่ที่เราชี้เหตุ เลือกวิธีแก้ มอบหมายงาน คุมความเสี่ยง และพิสูจน์ Saving
> ย้อนกลับถึงหลักฐานได้ทุกบาท”
