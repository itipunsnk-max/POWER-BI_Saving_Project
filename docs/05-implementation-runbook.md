# Implementation Runbook

## Batch 0 - Governance และความปลอดภัย (สัปดาห์ 1)

Owner: Sponsor, Finance, Maintenance, HSE, BI owner

- ยืนยันนิยาม PM/CM และขอบเขตค่าใช้จ่าย
- ยืนยัน Baseline 2025 และ Exclusion
- ตั้ง DEV/TEST/PROD workspace
- แต่งตั้ง Data owner, KPI owner, Release owner
- อนุมัติขอบเขต Self Maintenance

Exit criteria:

- Baseline sign-off
- KPI dictionary sign-off
- Safety boundary sign-off

## Batch 1 - Data foundation (สัปดาห์ 1-3)

- สร้าง Work type, Symptom, Resolution master
- แยก FactServiceOrder / FactCost / FactCommitment
- ทำ SAP reconciliation
- สร้าง Data Quality page
- เพิ่ม Refresh audit

Exit criteria:

- Unknown cost ≤ 5%
- Asset/SAP match ≥ 98%
- Finance variance ≤ 1%

## Batch 2 - Executive MVP (สัปดาห์ 3-5)

- Saving Control Tower
- PM/CM Portfolio
- Symptom Pareto
- Budget/Commitment/Forecast
- Repair history drill-through

Exit criteria:

- ตัวเลขทุกหน้าตรงกันภายใต้ Filter เดียวกัน
- KPI มี Definition tooltip
- UAT ผ่าน 10 test cases

## Batch 3 - Operational pilot (สัปดาห์ 5-8)

Pilot อาการ:

- แม่ปั๊ม/มิเตอร์
- มอเตอร์/สายพาน
- สายยาง
- มือจ่าย
- การแสดงผล

กิจกรรม:

- Triage form
- Repeat repair alert
- Vendor/warranty check
- Self Maintenance L0/L1
- Saving ledger

Exit criteria:

- ≥ 80% ticket ใช้ Symptom code
- ≥ 90% pilot ticket มี Asset No.
- Saving evidence ครบ 100%
- Safety incident = 0

## Batch 4 - Scale (สัปดาห์ 9-12)

- Vendor scorecard
- PM/legal bundling
- Repair-vs-replace
- Inventory reuse
- Sankey และ mobile layout
- Alerts/Power Automate

Exit criteria:

- Monthly saving run-rate ≥ 209,833 บาทตาม Working baseline
- Guardrails ผ่าน
- Finance approved ledger

## Weekly operating rhythm

### Daily

- Refresh/Data quality check
- Critical red flag ticket
- Overdue SLA

### Weekly

- Top cost symptoms
- Repeat repair list
- Saving action owner/due date
- Unknown coding queue

### Monthly

- Finance reconciliation and lock
- Saving approval
- Forecast at completion
- Vendor performance
- PM/legal compliance

## UAT test cases

1. Filter PM แล้ว Total ทุก Visual ตรงกัน
2. Filter CM แล้ว Unknown ไม่หายไป
3. Comparable period ใช้วันสิ้นสุดเดียวกัน
4. Partial month แสดง warning
5. Actual + Commitment + Accrual reconcile
6. Duplicate Service ID ไม่เพิ่มยอด
7. Drill-through แสดง Service/Asset เดียวถูกต้อง
8. Self Maintenance reopen ทำให้ Saving ถูก reverse
9. Legal overdue เป็นสีแดงและไม่ถูกซ่อน
10. RLS ของ AM เห็นเฉพาะ Scope ที่อนุมัติ

