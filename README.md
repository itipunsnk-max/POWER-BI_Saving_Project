# POWER BI Saving Project

โครงการลดต้นทุนงานซ่อมบำรุงและงานทดสอบตามกฎหมายของสถานีบริการ โดยใช้
Power BI เป็นศูนย์กลางการตัดสินใจ ตั้งแต่การคัดกรองอาการ การวิเคราะห์สาเหตุ
การควบคุมงบประมาณ ไปจนถึงการติดตามผลประหยัดเทียบฐานปี 2025

> สถานะ ณ 30 กรกฎาคม 2026: ระบบปัจจุบันมีข้อมูลใช้งานจริงแล้ว แต่ต้องปิด
> Data Quality Gate และยืนยัน Baseline ก่อนประกาศว่าบรรลุเป้าหมาย 20%

## Executive summary

- เป้าหมายโครงการ: ลด OPEX งานซ่อม/ทดสอบอย่างน้อย 20% เทียบปี 2025
- Baseline งาน PM/CM ในเอกสาร: 12,590,005.44 บาท  
  เป้าหมายประหยัด: 2,518,001.09 บาท  
  เพดานต้นทุนหลังลด 20%: 10,072,004.35 บาท
- Baseline ที่ Dashboard ใช้อยู่: 15,359,352.14 บาท  
  เป้าหมายประหยัด: 3,071,870.43 บาท  
  เพดานต้นทุน: 12,287,481.71 บาท
- ส่วนต่างของ Baseline สองชุด: 2,769,346.70 บาท หรือ 18.03%
- Power BI Service ที่ตรวจพบยังแสดงข้อมูลอัปเดต 22 กรกฎาคม 2026 ขณะที่
  ไฟล์ทำงานในเครื่องมีตัวเลขใหม่กว่า จึงต้องควบคุม Late invoice /
  Commitment / Accrual ก่อนใช้ Cost Reduction % เป็นผลสำเร็จอย่างเป็นทางการ

## สิ่งที่ Repository นี้จัดเตรียม

- [ผลตรวจระบบปัจจุบัน](docs/01-current-state-assessment.md)
- [Power BI dashboard blueprint](docs/02-power-bi-blueprint.md)
- [แผนลดต้นทุน 20%](docs/03-cost-reduction-plan.md)
- [Self Maintenance และขอบเขตความปลอดภัย](docs/04-self-maintenance.md)
- [Runbook ดำเนินงานแบบ Batch](docs/05-implementation-runbook.md)
- [ชุด DAX เริ่มต้น](powerbi/measures.dax)
- [Data contract สำหรับ Power BI](powerbi/data-contract.md)
- [Infographic backlog](docs/06-infographic-backlog.md)
- [Project site](index.html)

## Dashboard ที่ควรมีใน Production

1. Executive Saving Control Tower
2. PM/CM Cost & Volume
3. Pareto Symptom / Root Cause
4. Repeat Repair & Bad Actor Asset
5. Self Maintenance Funnel
6. Vendor / SLA / Warranty
7. PM & Legal Compliance
8. Budget, Commitment & Forecast
9. Data Quality & Reconciliation
10. Repair History Drill-through

Sankey ใช้เป็นหน้าอธิบายเส้นทาง
`PM/CM → Asset → Symptom → Resolution → Outcome` แต่ไม่ใช้แทน KPI หลัก
และความเป็น Real-time ต้องมาจาก Semantic Model/แหล่งข้อมูล ไม่ใช่ชนิด Visual

## Quick start

1. ยืนยันนิยาม Baseline และรายการที่รวม/ไม่รวมกับ Finance และเจ้าของข้อมูล
2. เพิ่มฟิลด์ตาม [Data contract](powerbi/data-contract.md)
3. สร้าง Measures จาก [measures.dax](powerbi/measures.dax)
4. ทำหน้า `Data Quality & Reconciliation` ก่อนหน้า Executive
5. Pilot 4 สัปดาห์กับอาการตู้จ่ายน้ำมันที่มีค่าใช้จ่ายสูง
6. Review ผลทุกสัปดาห์ และปิดผลประหยัดรายเดือนหลัง Finance lock

## Data protection

Repository นี้ตั้งใจให้เป็น Public documentation จึงไม่รวม PBIX, เอกสารต้นฉบับ,
ไฟล์รายงานการเงิน หรือข้อมูลส่วนบุคคล ไฟล์ต้นฉบับต้องเก็บใน SharePoint/Teams
ที่กำหนดสิทธิ์ และใช้ GitHub เก็บเฉพาะโค้ด นิยาม KPI และคู่มือที่ผ่านการ
Sanitize แล้ว

## แหล่งอ้างอิงหลัก

- [Power BI incremental refresh and real-time data](https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview)
- [Power BI real-time streaming retirement guidance](https://learn.microsoft.com/en-us/power-bi/connect-data/service-real-time-streaming)
- [Power BI content lifecycle management](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-content-lifecycle-management-deploy)
- [กฎหมายและประกาศ กรมธุรกิจพลังงาน](https://elaw.doeb.go.th/)

