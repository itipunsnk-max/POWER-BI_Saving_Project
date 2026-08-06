# Independent Data Quality Audit — Power BI Maintenance Saving

**Audit date:** 7 August 2026 (Asia/Bangkok)

**Dataset:** `service_tracking_cleaned-Rev.1.xlsx`

**Workbook fingerprint (SHA-256):** `baf33afabb99c9aa901a399650a9b46e1c01c8ebb51b3fd6164f8d28bee40d96`

**Decision:** **BLOCK official Saving KPI / SHARE descriptive views only with caveats**

รายงานนี้เป็นการตรวจอิสระจาก workbook และเอกสารเดิมใน repository โดยใช้เฉพาะผลรวม อัตรา และ metadata ไม่บันทึกตัวอย่างแถว, Service ID, Asset ID, ชื่อบุคคล, ชื่อสถานี, ชื่อ Vendor หรือข้อความแจ้งซ่อมลงในรายงาน ผล profile รายคอลัมน์แบบ aggregate อยู่ที่ `analysis/profile-summary.json`

## 1. Executive decision

| Use case | Readiness | เหตุผลหลัก |
|---|---|---|
| Finance-approved Saving / Cost Reduction % | **BLOCKED** | ไม่มี accounting transaction grain, Commitment, Accrual, currency/VAT status, reversal, Finance control total และ period lock |
| Baseline 2025 และเป้าลด 20% | **BLOCKED** | พบ baseline 3 ค่าและยังไม่มี reconciliation/sign-off |
| Work-order volume และ Actual cost overview | **CONDITIONAL** | Service ID ผ่าน uniqueness และยอดรวมภายใน workbook reconcile แต่จำนวนเงินยังไม่ trace ถึง Finance |
| Symptom Pareto / Root cause / Self Maintenance | **BLOCKED** | Unknown symptom cost ปี 2025 = 40.31%; ไม่มี RootCauseCode/ResolutionCode ที่ตรง semantic contract |
| Repeat repair / Bad actor asset | **BLOCKED** | Asset coverage เพียง 10.72%; 93.18% ของมูลค่าไม่มี Asset |
| SLA / cycle-time analytics | **CONDITIONAL** | วันที่บางส่วนเป็น text แบบ month-first และ closed records จำนวนมากไม่มี intermediate timestamps |
| Publish source artifacts to public GitHub | **BLOCKED** | พบ source binary 2 ไฟล์ถูก track อยู่แล้ว แม้ `.gitignore` จะกัน extension เหล่านั้น |

ภายใต้ logic ใน `powerbi/measures.dax` ค่า completeness proxy จะถูกจำกัดด้วย Asset coverage ที่ **10.72%** ซึ่งต่ำกว่า gate 95% และควรทำให้ `Target Status` เป็น `BLOCKED - DATA QUALITY` ไม่ควรแสดง Saving KPI

## 2. Dataset, sheets และ grain

- Workbook มี 2 sheets:
  - `Clean_Data`: 1,586 data rows × 52 columns; ไม่มี formula, hidden row/column, comment หรือ hyperlink
  - `Cost_Summary`: 85 data rows × 5 columns; เป็นค่าคงที่ ไม่มี formula
- Grain ที่สังเกตได้ของ `Clean_Data` คือ **1 row per SERVICE_ID / service order**
  - `SERVICE_ID`: populated 100%, unique 1,586/1,586
  - exact duplicate rows: 0
  - `PMORDER`: populated 100%, unique 1,586/1,586
- Grain นี้ตรงกับ `FactServiceOrder` แต่ **ไม่ตรงกับ** `FactCostTransaction` ที่ data contract กำหนดเป็น 1 row ต่อ SAP accounting document line
- `Cost_Summary` reconcile กับ `Clean_Data` ภายในไฟล์: total count/sum/average/max ต่างกัน 0 และ aggregate group rows ที่ตรวจ 78 แถวต่างกันไม่เกิน 0.01 ทั้งหมด อย่างไรก็ตามนี่เป็น **self-reconciliation จาก source เดียวกัน** และไม่ใช่หลักฐานว่าเท่ากับ SAP/Finance

## 3. Critical findings

### C1 — ไม่สามารถคำนวณ Cost Exposure หรือ Finance-approved Saving ได้

- **Severity / confidence:** Critical / High
- **Evidence:** Workbook มีจำนวนเงินรวมอยู่ที่ service-order grain เพียงฟิลด์เดียว แต่ไม่มี AccountingDocumentID, LineID, PostingDate, CostElement, AmountExVAT flag, Currency, CostStatus, IsReversal, Commitment, Accrual, FinanceControl, SourceUpdatedAt, Finance lock หรือ Saving ledger
- **Impact:** Actual-only YTD สามารถดูต่ำผิดจริงจาก late invoice, open PO/PR, accrual และ reversal ทำให้ Cost Reduction % สูงเกินจริงและเปลี่ยนผลตัดสินเป้า 20%
- **Likely cause:** Service Tracking export ถูกใช้แทน finance fact model
- **Required fix:** สร้าง facts แยกตาม `powerbi/data-contract.md`; KPI หลักต้องใช้ `Actual + Open Commitment + Accrual`, ปิดงวดด้วย Finance lock และแสดง Actual-only เป็นข้อมูลประกอบ
- **Automated gate:** ห้ามแสดง Saving เมื่อ Finance reconciliation variance >1%, period ยังไม่ complete หรือ source component ใดไม่มี freshness timestamp

### C2 — Baseline 2025 ไม่เป็น Source of Truth เดียว

- **Severity / confidence:** Critical / High
- **Evidence (aggregate only):**

| Source | 2025 rows/jobs | Baseline (THB) | 20% target (THB) |
|---|---:|---:|---:|
| PDF PM/CM working baseline | 994 | 12,590,005.44 | 2,518,001.09 |
| Existing dashboard documentation | 1,124 | 15,359,352.14 | 3,071,870.43 |
| Rev.1 workbook | 1,123 | 15,331,857.14 | 3,066,371.43 |

- Rev.1 สูงกว่า PDF 2,741,851.70 บาท หรือ 21.78% ของ PDF baseline และมีงานมากกว่า 129 งาน
- Rev.1 ต่ำกว่า dashboard 27,495.00 บาทและน้อยกว่า 1 งาน
- เป้า 20% ของ Rev.1 ต่างจาก PDF 548,370.34 บาท
- **Impact:** เปลี่ยนทั้ง denominator, saving target และสถานะ on/off target
- **Required fix:** ทำ row-count/amount bridge แบบ `source → billed → SAP actual → commitment → accrual → exclusion → finance lock`; เก็บ baseline version, inclusion rule, owner และ sign-off date
- **Automated gate:** baseline hash/version ต้องตรงกันทุก report page และห้ามแก้ locked baseline โดยไม่มี audit record

### C3 — Source binaries ยังถูก track ใน Git ทั้งที่ repository ระบุว่าเป็น public documentation

- **Severity / confidence:** Critical / High
- **Evidence:** `.gitignore` ครอบคลุม `*.docx`, `*.pdf`, `*.xlsx`, `*.pbix` แต่ `git ls-files` ยังพบ source binary ที่ tracked แล้ว 2 ไฟล์ (DOCX 1, PDF 1) เพราะ `.gitignore` ไม่ยกเลิกไฟล์ที่ถูก track ก่อนหน้า ขณะที่ XLSX และ PBIX ปัจจุบันถูก ignore และไม่ tracked
- **Impact:** Operational/financial source material อาจอยู่ทั้งใน current tree และ Git history; การลบเฉพาะ working tree ไม่ได้ลบประวัติ
- **Required fix:** ให้ repository owner และ Information Security หยุด publish ชั่วคราว, ตรวจ access/history, นำ binary ออกจาก index, ประเมิน history rewrite และทำ DLP scan ก่อนเปิด public อีกครั้ง
- **Automated gate:** CI ต้อง fail หาก `git ls-files` พบ raw extension หรือ DLP scan พบ identifier/personal pattern

## 4. High findings

### H1 — Asset linkage ไม่เพียงพอสำหรับ repeat repair และ reliability engineering

- Asset populated 170/1,586 = **10.72%**; missing 1,416 rows = 89.28%
- มูลค่าที่ไม่มี Asset = **18,500,136.99 บาท หรือ 93.18%** ของทั้งหมด
- ปี 2025 coverage = 9.26%; ปี 2026 = 14.29%
- **Impact:** Repeat 30/90D, bad actor, MTBF, lifecycle cost, repair-vs-replace และ self-maintenance safety targeting ไม่ trustworthy
- **Fix:** สร้าง Asset master/crosswalk ระหว่าง Service Tracking–CAMS–SAP; แยก `asset_not_applicable` ออกจาก `asset_unknown`; reject close สำหรับงานที่ asset ต้องมีแต่ยัง map ไม่ได้
- **Gate:** applicable Asset match ≥98%; orphan = 0; one business asset maps to one active AssetKey

### H2 — Unknown symptom cost สูงกว่าขีดจำกัดอย่างมาก

- Proxy unknown = `PROB_DETAIL_DESC` ว่างหรือ “อื่น ๆ”
- ทั้งไฟล์: 418 rows (26.36%), **7,809,063.79 บาท (39.33%)**
- ปี 2025: 319/1,123 rows (28.41%), **6,179,788.49 บาท (40.31%)**
- ปี 2026: 98/462 rows (21.21%), **1,494,268.50 บาท (34.07%)**
- **Impact:** Pareto, root-cause prioritization และ allocation ของ saving lever มี selection bias; Unknown ห้ามถูกนับเป็น saving
- **Fix:** ใช้ controlled `SymptomCode`, mapping queue, mandatory code ก่อน dispatch และแยก `UNKNOWN_PENDING_REVIEW`
- **Gate:** symptom coverage ≥95% และ unknown cost share ≤5%

### H3 — Taxonomy ไม่ตรงความหมายที่ data contract ต้องใช้

- ไม่มี `RootCauseCode` และ `ResolutionCode`
- `PROB_RESOLVE_DESC` มีลักษณะเป็น asset/component taxonomy มากกว่าการแก้ไขจริง จึงไม่ควรนำไปใช้เป็น Resolution โดยตรง
- Severity มี 11 labels ที่เป็น SLA windows/other classes ไม่ใช่ approved `Critical/Urgent/Routine`
- Project summary กล่าวถึง CM/PM/BM แต่ workbook มี PM/CM เท่านั้นและไม่มี mapping provenance ของ BM
- Province มี 128 normalized nonblank labels ซึ่งเกิน domain จังหวัดไทย 77 จังหวัดอย่างมาก; ไม่มี reference master ให้พิสูจน์ validity
- **Impact:** Drill path `Work type → Asset → Symptom → Root cause → Resolution` จะสื่อความหมายผิด และการรวมหมวดอาจเปลี่ยนตาม spelling/source
- **Fix:** แยก DimAssetCategory, DimComponent, DimSymptom, DimRootCause, DimResolution, DimSeverity และ DimLocation; version mapping table พร้อม unmapped exception queue; BM ต้อง map เป็น PM/CM ด้วยกฎที่ตรวจสอบย้อนกลับได้หรือแสดง exception

### H4 — กลุ่ม structural null 136 แถวกระทบ 15.35% ของมูลค่า

- 136 rows ขาดพร้อมกันใน 12 fields เช่น vendor code, status code, severity code, SAP order type และ assignment audit fields
- มูลค่า cohort = **3,046,805.90 บาท (15.35%)**; ในปี 2025 = 120 rows / 2,591,921.20 บาท
- **Impact:** บ่งชี้ mixed source/schema หรือ partial backfill; segment นี้อาจหลุดจาก slicer/join และทำให้ KPI ต่ำกว่าจริง
- **Fix:** เพิ่ม SourceSystem/SourceRecordType, แยก ingestion rule ตาม source, quarantine schema-incomplete rows และรายงาน coverage เป็นราย source/month

### H5 — Date storage ผสม type และมี locale ambiguity

- `WORKINPROGRESS`: datetime 933 + text 120; `RESOLVED_DATE`: datetime 1,224 + text 212
- ใน text dates มี day/month-ambiguous values 50 และ 77 rows ตามลำดับ
- เมื่อ parse แบบ month-first ตามรูปแบบที่สังเกต: future = 0, WIP-before-assigned = 0, resolved-before-service = 0
- หาก Power BI/เครื่องผู้ใช้ parse day-first: เกิด future WIP 23 rows, future resolved 31 rows และ sequence errors เพิ่มขึ้นมาก
- หลังใช้ month-first อย่างชัดเจนยังพบ assigned-before-service 2/1,451 และ close-before-resolved 2/1,436
- closed rows 1,585 แต่ขาด resolved timestamp 149 และ assigned timestamp 135
- **Impact:** SLA, cycle time, comparable-period cutoff และ late-arrival logic อาจผิดตาม locale
- **Fix:** upstream ส่ง ISO 8601 พร้อม timezone; Power Query ต้อง cast text dates ด้วย explicit `en-US` (ระหว่างแก้ต้นทาง) แล้วแปลงเป็น Asia/Bangkok; invalid/sequence error ต้อง quarantine

### H6 — มี PII/confidential-data leakage risk ใน operational fields

- มี direct identifier fields ได้แก่ technician name และ user-updated audit fields
- `CALL_DETAIL` เป็น free text high-cardinality (1,491 distinct/1,555 populated) และ pattern scan พบ phone-like 28 rows, Thai-name-title-like 15 rows และ valid-checksum 13-digit-like 3 rows; เป็น pattern detection ไม่ใช่การยืนยันตัวบุคคล
- Asset field พบ 13-digit-like pattern 3 rows ซึ่งอาจเป็น Asset ID หรือ personal identifier ต้อง classify กับ data owner
- Workbook metadata มี creator/last-modified-by populated
- **Impact:** drill-through/export/public Git อาจเปิดเผยข้อมูลส่วนบุคคลหรือ operational identifiers
- **Fix:** exclude free text/person fields จาก public model; ใช้ pseudonymous TechnicianKey, RLS/OLS, restricted detail workspace, metadata scrub และ DLP scan; เก็บ raw ใน approved SharePoint/Teams เท่านั้น

## 5. Medium findings และ positive controls

### Medium

- `SITE_ID` มี mixed physical type (string 1,546; integer 40) และ 35 Site IDs map ไปมากกว่า 1 Site name; ต้องใช้ DimLocation master และ effective-date mapping
- `GROUP_ID → GROUP_NAME` มี mapping ไม่เป็น 1:1 ใน comparable rows; ต้องตรวจ SCD/organizational change
- 1 record มี `SERVICE_DATE` ในปี 2024 และ `MM` ไม่ตรงเดือนของ SERVICE_DATE 1 record; ต้องกำหนด inclusion rule ไม่ให้ปน baseline 2025
- Latest service date คือ 29 June 2026 และ latest close date 6 July 2026 ขณะที่ audit วันที่ 7 August 2026; เนื่องจากไม่มี `SourceUpdatedAt`/Finance lock จึงรับรอง freshness ไม่ได้ อาจเป็น month-end cutoff ที่ตั้งใจหรือข้อมูลขาดช่วง
- Cost เป็น numeric 100%, positive ทั้งหมด, median 6,750.00 บาท, max 325,245.20 บาท; top 5% ของแถวคิดเป็น 30.94% ของมูลค่า ต้องใช้ price/rate-card master ตรวจ outlier แทน hard-coded threshold
- ไม่พบ negative/reversal rows; นี่ไม่ใช่หลักฐานว่าไม่มี reversal แต่บ่งชี้ว่า dataset ไม่รองรับ credit note/reversal accounting
- `PMORDER` และ `ตรวจสอบ PMORDER` ตรงกัน 100% แต่ทั้งสอง field มีค่าซ้ำกันแบบ mirror จึงไม่ถือเป็น independent SAP validation จนกว่าจะยืนยัน lineage

### Positive controls

- `SERVICE_ID` required/unique ผ่าน 100%; exact duplicate rows = 0
- `PMACTTYPES` populated 100% และมีเพียง PM/CM
- `จำนวนยอดเงิน` cast เป็น numeric ได้ 100%; ไม่มี null/zero/negative
- `Cost_Summary` reconcile กับ `Clean_Data` ภายใน snapshot ปัจจุบัน
- ไม่มี external links, formula, comments หรือ hyperlinks ใน workbook
- XLSX/PBIX ถูก ignore และไม่ tracked ใน Git ณ เวลาตรวจ

## 6. Data-contract gap summary

| Contract area | Workbook support | Assessment |
|---|---|---|
| FactServiceOrder key/date/work type | SERVICE_ID, SERVICE_DATE, PMACTTYPES มี | Partial; key ดี แต่ semantic fields ขาด |
| Asset/location/vendor dimensions | Site/vendor มีบางส่วน; Asset 10.72% | Fail for reliability use cases |
| Symptom/root cause/resolution | label บางส่วน; ไม่มี approved codes/root cause | Fail |
| Severity/maintenance level/reopen/repeat | severity เดิมไม่ตรง master; ที่เหลือไม่มี | Fail |
| FactCostTransaction | มี service-level amount อย่างเดียว | Fail |
| Commitment / Accrual | ไม่มี | Fail |
| Saving ledger / finance approval | ไม่มี | Fail |
| Freshness / source lineage / period lock | ไม่มี | Fail |
| Privacy-safe publication layer | ยังมี person/free-text fields และ tracked binaries | Fail |

## 7. Recommended remediation phases

### Phase 0 — Contain privacy and freeze claims (0–2 business days)

1. หยุด publish official Saving และ raw-detail export
2. ให้ Repo owner/InfoSec ตรวจ tracked DOCX/PDF และ Git history; ทำ DLP scan ก่อนเปิด public
3. Lock workbook fingerprint นี้เป็น audit snapshot; ห้ามแทนที่ไฟล์โดยไม่เปลี่ยน version/hash
4. ติดป้าย dashboard ปัจจุบันว่า `Actual-only / Unreconciled / Through latest complete period`

**Exit:** raw extensions tracked = 0, history exposure decision documented, Saving visual blocked by gate

### Phase 1 — Finance baseline and exposure model (2–5 business days)

1. Finance ลงนาม inclusion/exclusion และ baseline 2025 เพียงค่าเดียว
2. สร้าง FactCostTransaction, FactCommitment, FactAccrual และ FinanceControl ตาม data contract
3. ทำ reconciliation bridge รายเดือนและแยก VAT/currency/reversal ให้ชัด
4. เพิ่ม LatestCompleteDate, SourceUpdatedAt และ FinanceLockDate

**Exit:** reconciliation variance ≤1%, baseline version signed, Actual + Commitment + Accrual ครบ

### Phase 2 — Engineering master data (1–2 weeks)

1. สร้าง Asset/Site crosswalk และ effective-dated dimensions
2. สร้าง controlled symptom/root-cause/resolution/severity masters
3. ทำ mapping queue สำหรับ Unknown และ BM exceptions
4. แก้ source dates เป็น ISO 8601; quarantine chronology errors

**Exit:** Asset match ≥98%, unknown cost ≤5%, location mapping 1:1 ณ effective date, date rule errors = 0

### Phase 3 — Saving evidence and production QA (1–2 weeks)

1. สร้าง FactSavingLedger พร้อม counterfactual, implementation cost, evidence และ Finance status
2. Reverse saving เมื่อ reopen/invalidated; ห้าม infer saving จากยอดลดลงอย่างเดียว
3. UAT filter totals, partial month, duplicate prevention, repeat logic, legal/safety guardrails และ RLS/OLS
4. เปิด Executive Saving page หลังผ่าน all gates เท่านั้น

**Exit:** Finance-approved ledger, evidence 100%, safety/legal guardrails ผ่าน, all KPI tests green

## 8. Minimum automated tests

| Test | Threshold |
|---|---:|
| ServiceID not null / duplicate | 100% / 0 |
| AccountingDocumentID + LineID uniqueness | 100% / 0 duplicate |
| Work type accepted values | PM/CM only; BM exception = 0 unresolved |
| Applicable Asset match | ≥98% |
| Symptom coverage / unknown cost | ≥95% / ≤5% |
| Location business key mapping | 1 active match per effective date |
| Date parse and chronology | 100% parse; future/sequence errors = 0 |
| Closed record required timestamps | 100% ตาม approved lifecycle rule |
| Currency/VAT/status/reversal | explicit and accepted values 100% |
| Finance reconciliation variance | ≤1% |
| Source freshness | ภายใน SLA ที่ owner ลงนาม; แสดงแยกแต่ละ source |
| Public-repo raw extension/DLP scan | 0 tracked raw files; 0 unresolved findings |
| Saving evidence and approval | 100% สำหรับยอดที่แสดงเป็น Finance Approved |

## 9. Assumptions and open questions

- ถือว่า `SERVICE_DATE` เป็น reported/open date และ `CLOSE_DATE` เป็น completion date จนกว่า data owner จะยืนยัน
- ถือว่า text timestamps ใช้ month-first เพราะให้ chronology สอดคล้องที่สุด; ต้องยืนยันจาก source system ไม่ควรอาศัย inference ใน production
- `จำนวนยอดเงิน` ถูก audit เป็น amount ที่ workbook ใช้ แต่ยังไม่ยืนยันว่าเป็น THB excluding VAT, billed, actual หรือ estimate
- Unknown symptom ใช้ proxy “ว่าง/อื่น ๆ”; production ต้องใช้ `SymptomCode` และ `IsUnknown`
- ไม่ได้รับ SAP/Finance control extract, commitment, accrual, invoice status, master data หรือ approved KPI dictionary จึงยังตรวจ referential integrity และ external reconciliation ไม่ได้
- ต้องให้ Finance ตอบว่า 129 งาน/2.742 ล้านบาทที่ต่างจาก PDF baseline รวม/ไม่รวมด้วยกฎใด และรายการ 27,495 บาทที่ต่างจาก dashboard ถูกย้ายปี ตัดออก หรือแก้ไขเพราะเหตุใด

## 10. Auditor conclusion

ไฟล์ Rev.1 มีฐาน service-order ที่สะอาดด้าน primary key และ internal aggregation แต่ยังเป็น **operational snapshot ไม่ใช่ auditable saving model** จุดแข็งนี้เพียงพอสำหรับเริ่มสร้าง descriptive data-quality page แต่ไม่เพียงพอสำหรับประกาศ Cost Reduction, Repeat Repair, Self Maintenance saving หรือ Finance-approved saving จนกว่าจะปิด Critical/High findings และผ่าน gates ข้างต้น
