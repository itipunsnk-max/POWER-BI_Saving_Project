# Power BI Blueprint

## 1. เป้าหมายของผลิตภัณฑ์

Power BI ต้องตอบคำถามให้ได้ตามลำดับ:

1. ตอนนี้ประหยัดได้จริงเท่าไรเมื่อรวมภาระผูกพัน?
2. Gap จากเป้าหมาย 20% อยู่ที่ไหน?
3. อาการ/Asset/พื้นที่/Vendor ใดเป็นโอกาสที่ลงมือได้?
4. งานใดแก้ด้วย Self Maintenance ได้อย่างปลอดภัย?
5. ใครต้องทำอะไร ภายในเมื่อไร และผลหลังทำเป็นอย่างไร?

## 2. Semantic model เป้าหมาย

ใช้ Star schema และหลีกเลี่ยงการเชื่อม Fact-to-Fact โดยตรง

### Fact tables

- `FactServiceOrder` - 1 แถวต่อ Service ID
- `FactCostTransaction` - 1 แถวต่อ SAP document / invoice line
- `FactCommitment` - PO/PR/งานค้างวางบิล
- `FactMaintenanceAction` - กิจกรรม Triage/Self/Vendor และผลลัพธ์
- `FactPMCompliance` - 1 แถวต่อ Asset × PM requirement × due date
- `FactInventoryMovement` - อะไหล่/Asset reuse
- `FactSavingLedger` - Saving ที่ผ่านการอนุมัติ

### Dimensions

- `DimDate`, `DimAsset`, `DimLocation`, `DimAM`
- `DimWorkType` = PM / CM
- `DimSymptom`, `DimRootCause`, `DimResolution`
- `DimVendor`, `DimCostStatus`, `DimSavingLever`
- `DimSeverity`, `DimLegalRequirement`

ทุก Fact ต้องมี Date key, Location key, Asset key เมื่อใช้ได้ และ Source system
identifier สำหรับ Trace back

## 3. หน้า Dashboard Production

### Page 1 - Saving Control Tower

Hero cards:

- Baseline 2025
- Actual + Commitment + Accrual YTD
- Comparable saving %
- Saving validated by Finance
- Gap to 20% target
- Data completeness

Visual:

- Monthly run-rate: Baseline comparable vs Exposure vs Target
- Waterfall: Baseline → Avoided → Price saving → Scope change → Current exposure
- Action table: Lever, owner, due date, expected/validated saving, status

### Page 2 - PM/CM Portfolio

- Stacked column: cost and job count by month, split PM/CM
- Small multiples: cost/job, repeat rate, downtime by PM/CM
- Matrix: Business group × PM/CM × cost × saving gap
- Tooltip: definition, source, last refresh, completeness

### Page 3 - Symptom Pareto

- Pareto bar + cumulative line by standardized symptom
- Decomposition tree: PM/CM → Asset → Symptom → Root cause → Vendor
- Unknown/0 callout with value and coverage trend
- Drill-through to work order history

### Page 4 - Repair Path Sankey

Flow:

`PM/CM → Asset category → Symptom → Resolution → Outcome`

Use Sankey only after:

- Symptom and resolution coverage ≥ 95%
- Categories are mutually exclusive
- Node count is limited to Top N + Other
- Custom visual is approved by IT/security

Sankey is explanatory; it does not create real-time behavior. Data freshness comes
from the model and refresh architecture.

### Page 5 - Repeat Repair / Bad Actor

- Asset ranking by 90/180/365-day cost
- Repeat within 30/60/90 days
- MTBF, cost/asset value, lifetime repair cost
- Repair-vs-replace flag
- Scatter: repair cost ratio vs repeat count, bubble = downtime

### Page 6 - Self Maintenance

- Funnel: reported → triaged → self eligible → resolved → avoided dispatch
- First-time fix rate
- Avoided dispatch cost (validated)
- Escalation and reopen rate guardrails
- Table of symptoms awaiting infographic/SOP

### Page 7 - Vendor & Warranty

- Cost, SLA, repeat repair, first-time fix by Vendor
- Warranty recovery and invoice rejection
- Price variance for comparable job/part
- Vendor concentration and overdue invoices

### Page 8 - PM & Legal Compliance

- Due/overdue/complete by month and asset
- Legal due dates and evidence completeness
- Bundling opportunity by geography/month
- Guardrail: 100% statutory compliance

### Page 9 - Budget & Forecast

- Budget/Actual/Commitment/Accrual/Available
- Forecast at completion
- Target line and scenario selector
- Bridge to Finance totals

### Page 10 - Data Quality

- Source freshness
- Row count trend
- Duplicate Service IDs
- Unknown PM/CM, symptom, asset and location
- SAP match rate
- Reconciliation variance
- Period lock status

## 4. Refresh architecture

### Recommended default: Near-real-time

งานซ่อมไม่จำเป็นต้องลงทุน Real-Time Intelligence ถ้าการตัดสินใจเป็นรายวัน
แนะนำ Refresh ทุก 30-60 นาทีสำหรับ Service intake และ 2-4 ครั้ง/วันสำหรับ SAP
โดยแสดงเวลาอัปเดตแต่ละ Source แยกกัน

### เมื่อ SLA ต้องต่ำกว่า 5 นาที

ใช้ Microsoft Fabric Real-Time Intelligence:

`Power Apps/Form/Service event → Eventstream → Eventhouse/KQL → Power BI`

แต่ SAP actual/Finance ยังต้องเป็น batch และต้องไม่รวมตัวเลขสดที่ยังไม่ผ่าน
การตรวจสอบเข้ากับ Finance validated saving

ไม่แนะนำเริ่มโครงการใหม่ด้วย Power BI streaming semantic model แบบเดิม เพราะ
Microsoft ระบุว่าการสร้างใหม่จะสิ้นสุด 31 ตุลาคม 2027 และแนะนำ Fabric
Real-Time Intelligence แทน

## 5. Visual standards

- ใช้ภาษาไทยเป็นหลัก และชื่อฟิลด์เชิงเทคนิคไว้ใน Tooltip
- ใช้สี: Actual = Navy, Target = Cyan, Exposure = Orange, Risk = Red
- หลีกเลี่ยง Pie/Donut เมื่อมีมากกว่า 5 กลุ่ม
- Bar chart เริ่มที่ศูนย์
- ทุก KPI แสดงหน่วย, ช่วงเวลา,สถานะ Complete/Partial และ Last refresh
- ไม่มีชื่อหน้า `Page 1/2/3` หรือ `Duplicate`
- Bookmark `Reset to approved view` ต้องทดสอบทุกหน้า
- Mobile layout สำหรับผู้บริหารและ AM

