# Power BI Semantic Model Implementation Guide v2

## 1. ข้อสรุปสำหรับการลงมือทำ

แบบจำลอง v2 นี้ยึด `Clean_Data` ใน `service_tracking_cleaned-Rev.1.xlsx` เป็นแหล่งข้อมูลปฏิบัติการ ณ ปัจจุบัน และยึด grain หลักเป็น **1 แถวต่อ `SERVICE_ID`** ซึ่งตรวจแล้วว่า 1,586 แถวมี `SERVICE_ID` ไม่ซ้ำทั้งหมด

ข้อกำหนดสำคัญ:

- ใช้ `SERVICE_DATE` เป็น canonical date ของงานบริการ และสร้าง Year/Month ใหม่จากคอลัมน์นี้
- ไม่ใช้ `MM` เป็นตัวเชื่อมวันที่หรือเป็นฐานคำนวณ KPI เพราะพบ 1 แถวที่ `MM = 2025-04` แต่ `SERVICE_DATE` อยู่ใน `2026-04` ทำให้ยอดปี 2025 ต่างกัน 27,495.00 บาท
- ค่า `จำนวนยอดเงิน` เป็นเพียงยอดที่บันทึกอยู่ใน Service Tracking ระดับงานบริการ จึงตั้งชื่อว่า `RecordedCostTHB`; ห้ามเรียกว่า SAP Actual หรือ Finance Actual จนกว่าจะกระทบยอดกับบัญชี
- `Cost_Summary` เป็นตารางสรุปแบบ static ไม่มีสูตร ให้ใช้เฉพาะ QA/reconciliation และปิด Load; ห้ามเชื่อมเข้ากับ semantic model เพราะจะเกิดการนับซ้ำ
- KPI Saving ทางการต้องถูกปิดด้วย Publication Gate จนกว่า Baseline, Finance reconciliation, Asset/SAP match, Period lock และ Safety/Statutory guardrails จะผ่าน
- ไม่โหลด `TECHNICIAN_NAME`, `USER_UPDATED_*`, `CALL_DETAIL` หรือข้อความอิสระที่อาจมีข้อมูลส่วนบุคคลเข้าสู่โมเดลสำหรับผู้ใช้ทั่วไป

ไฟล์ DAX ที่สอดคล้องกับ contract นี้คือ `powerbi/measures-v2.dax`

## 2. แหล่งข้อมูลและหลักฐานที่ตรวจ

ตรวจจาก:

- `service_tracking_cleaned-Rev.1.xlsx`
- `docs/01-current-state-assessment.md` ถึง `docs/06-infographic-backlog.md`
- `powerbi/data-contract.md`
- `powerbi/measures.dax`

หมายเหตุเรื่อง path: repository ไม่มีโฟลเดอร์ `docs/powerbi`; จึงตีความคำสั่งว่าให้อ่านเอกสารเดิมใน `docs/` และ `powerbi/` โดยไม่แก้ไขไฟล์เดิม

### 2.1 Workbook profile ที่ใช้เป็น baseline ทดสอบ

| รายการ | ผลตรวจ |
|---|---:|
| `Clean_Data` | 1,586 data rows, 52 columns |
| Distinct `SERVICE_ID` | 1,586 |
| Distinct `PMORDER` | 1,586 |
| Exact duplicate rows | 0 |
| `SERVICE_DATE` range | 2024-12-25 ถึง 2026-06-29 |
| `CLOSE_DATE` range | 2025-01-04 ถึง 2026-07-06; missing 1 |
| Recorded amount, all rows | 19,853,145.19 |
| CM amount, all rows | 17,573,203.39 |
| PM amount, all rows | 2,279,941.80 |
| Asset value present | 170 / 1,586 = 10.72% |
| Site IDs with more than one site-name variant | 35 |
| Duration reconciliation exceptions (>1 minute) | 1 |
| Assigned timestamp before service timestamp | 2 |

ตัวเลขข้างต้นเป็น aggregate benchmark สำหรับ UAT เท่านั้น ไม่มีการคัดลอกข้อมูลรายบุคคลหรือข้อมูลระดับแถวลงเอกสารนี้

### 2.2 ความขัดแย้งของ Baseline ที่ต้องปิดก่อน Production

| วิธีตัดปี 2025 | จำนวนงาน | Recorded cost |
|---|---:|---:|
| ใช้ `SERVICE_DATE` ซึ่งเป็น canonical date | 1,123 | 15,331,857.14 |
| ใช้ `MM` จาก source | 1,124 | 15,359,352.14 |
| Working baseline PM/CM ในเอกสารเดิม | ไม่ได้ระบุ grain เดียวกัน | 12,590,005.44 |

สาเหตุของส่วนต่างระหว่างสองแถวแรกคือ 1 record ที่ source month กับ service month ข้ามปีและมีมูลค่า 27,495.00 บาท ดังนั้น v2 จะใช้ 15,331,857.14 เป็น **technical reconciliation benchmark** จาก `SERVICE_DATE` เท่านั้น ยังไม่ใช่ Approved Finance Baseline

### 2.3 ข้อค้นพบด้านชนิดข้อมูล

- `WORKINPROGRESS` มีทั้ง Excel DateTime และข้อความรูปแบบ US แต่ parse ได้ครบ 1,053 ค่าที่มีข้อมูล
- `RESOLVED_DATE` มีทั้ง Excel DateTime และข้อความรูปแบบ US แต่ parse ได้ครบ 1,436 ค่าที่มีข้อมูล
- `TECHNICIAN_TIME` และ `PTT_TECHNICIAN_TIME` มีทั้งตัวเลขและ numeric text; หลังแปลงแล้วตรงกันทั้งหมด 1,435 ค่า
- `PTT_CALLCENTER_TIME` เป็น text ทั้งหมด แต่แปลงเป็นตัวเลขได้ครบ 1,435 ค่า
- `RESOLUTION_TIME` เป็น SLA target หน่วยนาที; `TOTALTIME` เป็น actual elapsed time หน่วยนาที
- กฎ `SLA_STATUS = Met` เมื่อ `TOTALTIME <= RESOLUTION_TIME` ตรงกับ source ครบ 1,449 แถวที่ประเมินได้
- `SITE_ID` และ `PMORDER` มีชนิดข้อมูลผสม text/integer ต้องแปลงเป็น text ก่อนทำ key
- `TECHNICIAN_STATUS` กับ `PTT_TECHNICIAN_STATUS` ต่างกัน 43 แถว; 42 แถวเป็น `-` เทียบกับ blank และ 1 แถวเป็นความขัดแย้งจริง ให้ใช้คอลัมน์แรกเป็น reporting field และเก็บ flag เพื่อตรวจสอบ

## 3. Target grain และขอบเขต Fact

### 3.1 Fact ที่สร้างได้ทันทีจาก workbook

#### `FactServiceOrder`

Grain: **1 row per `SERVICE_ID`**

`SERVICE_ID` เป็น primary business key ที่ยืนยัน uniqueness แล้ว ส่วน `PMORDER` และ `SERVICE_NO` เป็น degenerate identifiers สำหรับ trace-back ไม่ใช่ dimension

`RecordedCostTHB` อยู่ใน Fact นี้ เพราะ source ให้เพียงหนึ่งยอดต่อ service/order และ `PMORDER` ไม่ซ้ำ ห้ามแยกยอดนี้เป็น `FactCostTransaction` เพราะไม่มี accounting document/line, posting date, cost element, reversal และ VAT basis ที่จำเป็นต่อ grain ทางบัญชี

### 3.2 Fact ที่ต้องเพิ่มจาก source อื่นใน Phase 2–3

| Fact | Target grain | แหล่งที่ต้องหา | ใช้ตอบ |
|---|---|---|---|
| `FactCostTransaction` | 1 row per SAP accounting document line | SAP actual/IW39/GL extract | Actual cost, reversal, posting period |
| `FactCommitment` | 1 row per open PO/PR/received-not-invoiced line per snapshot | ME2K/PO/PR | Open commitment |
| `FactAccrual` | 1 row per service/internal order per month-end accrual | Finance month-end | Accrued cost |
| `FinanceControl` | 1 row per finance control total per posting period/scope | Finance signed control | Reconciliation |
| `FactSavingLedger` | 1 row per approved saving event | Controlled saving form/list | Finance-approved net saving |
| `FactMaintenanceAction` | 1 row per triage/self/vendor action attempt | Triage/action form | Self-resolution, reopen, avoided dispatch |
| `FactPMCompliance` | 1 row per asset × requirement × due date | PM/legal master | PM and statutory compliance |

ห้ามเชื่อม Fact-to-Fact โดยตรง ใช้ dimensions ร่วมกันและคำนวณผ่าน measures

## 4. Power Query staging

### 4.1 Query layout

สร้าง query ตามลำดับนี้:

1. `pSourceFile` — Text parameter; local path ใช้เฉพาะ DEV
2. `fnToNullableText` — normalize text/blank
3. `fnToLocalDateTime` — parse Excel DateTime และ US text timestamp
4. `fnToNullableNumber` — parse numeric/numeric text
5. `src_ServiceTracking` — อ่าน `Clean_Data`; connection only
6. `stg_ServiceTracking` — select, sanitize, type, derive flags; connection only
7. `qa_CostSummary` — อ่าน `Cost_Summary`; connection only, Enable Load = Off
8. `qa_DuplicateServiceID`, `qa_InvalidDateSequence`, `qa_DurationVariance`, `qa_SourceMonthMismatch` — exception queries; connection only
9. Dimensions
10. `FactServiceOrder`
11. `RefreshAudit`

Production ให้เปลี่ยน source เป็น SharePoint/OneDrive connector ที่จัดสิทธิ์แล้ว ไม่ใช้ absolute path ของเครื่องผู้พัฒนา

### 4.2 Helper functions

```powerquery
// fnToNullableText
(value as any) as nullable text =>
let
    TextValue = if value = null then null else Text.Trim(Text.Clean(Text.From(value, "en-US"))),
    Result = if TextValue = null or TextValue = "" or TextValue = "-" then null else TextValue
in
    Result
```

```powerquery
// fnToLocalDateTime — source timestamps are local wall-clock time in Asia/Bangkok
(value as any) as nullable datetime =>
let
    Direct = try DateTime.From(value) otherwise null,
    Parsed =
        if Direct <> null then Direct
        else try DateTime.FromText(Text.From(value), [Culture = "en-US"]) otherwise null
in
    Parsed
```

```powerquery
// fnToNullableNumber
(value as any) as nullable number =>
let
    Direct = try Number.From(value) otherwise null,
    Parsed =
        if Direct <> null then Direct
        else try Number.FromText(Text.Replace(Text.Trim(Text.From(value)), ",", ""), "en-US") otherwise null
in
    Parsed
```

### 4.3 Source-to-target mapping ครบ 52 fields

| Source field | Target/action | Type/role |
|---|---|---|
| `SERVICE_ID` | `ServiceID` | Text, required business key |
| `SERVICE_NO` | `ServiceNo` | Text, hidden trace-back identifier |
| `MM` | `SourceYearMonth` | Text, QA only; do not load to model |
| `SITE_ID` | `SiteKey` | Normalized text |
| `SITE_NAME` | `SiteNameRaw` | Text; canonicalize in `DimSite` |
| `PMORDER` | `PMOrder` | Text, hidden trace-back identifier |
| `SERVICE_DATE` | `ServiceDateTime` | Local DateTime, required |
| `ASSIGNED_DATE` | `AssignedDateTime` | Local DateTime, nullable |
| `WORKINPROGRESS` | `WorkInProgressDateTime` | Local DateTime, nullable, mixed source type |
| `RESOLVED_DATE` | `ResolvedDateTime` | Local DateTime, nullable, mixed source type |
| `CLOSE_DATE` | `CloseDateTime` | Local DateTime, nullable |
| `RESOLUTION_TIME` | `SLATargetMinutes` | Decimal/whole minutes |
| `TOTALTIME` | `LeadTimeMinutes` | Decimal/whole minutes |
| `SLA_STATUS` | `SLAStatusRaw`, derive `IsSLAMet` | Text + Boolean |
| `TECHNICIAN_TIME` | `TechnicianTimeMinutes` | Decimal/whole minutes |
| `TECHNICIAN_STATUS` | `TechnicianSLAStatusRaw`, derive `IsTechnicianSLAMet` | Text + Boolean |
| `GROUP_ID` | `ServiceGroupIDRaw` | Text attribute; nullable |
| `GROUP_NAME` | `ServiceGroupKey`/name | Normalize text; complete in current file |
| `VENDOR_CODE` | `VendorCodeRaw` | Text attribute; nullable |
| `VENDOR_NAME` | `VendorKey`/name | Normalize text; complete in current file |
| `CALL_DETAIL` | Remove before Load | Free text; may contain personal/raw detail |
| `PROBLEM_TYPE_DESC` | `ProblemType` | `DimSymptom` hierarchy |
| `OBJECT_PART` | `ObjectPart` | `DimSymptom` hierarchy |
| `OBJECT_PART_ITEM` | `ObjectPartItem` | `DimSymptom` hierarchy |
| `PROB_DETAIL_DESC` | `ProblemDetail` | `DimSymptom` hierarchy |
| `DAMAGE` | `Damage` | `DimSymptom` hierarchy |
| `PROB_RESOLVE_DESC` | `Resolution` | `DimResolution` |
| `SERVICE_STATUS` | `ServiceStatusCodeRaw` | Source attribute/QA |
| `SERVICE_STATUS_DESC` | `ServiceStatusKey`/description | Model key; complete in current file |
| `SEVERITY_LEVEL` | `SeverityKey` | Text; `UNKNOWN` when unavailable |
| `SEVERITY_LEVEL_DESC` | `SeverityDescription` | Dimension attribute; map from code when unique |
| `PMACTTYPES` | `WorkTypeKey` | PM/CM, complete |
| `PMACTTYPES_DESC` | `WorkTypeDescription` | Dimension attribute |
| `SAP_PM_ORDER_TYPE` | `SAPOrderTypeKey` | Text; `UNKNOWN` when unavailable |
| `SAP_PM_ORDER_TYPE_DESC` | `SAPOrderTypeDescription` | Dimension attribute |
| `TECHNICIAN_NAME` | Remove before Load | Personal data |
| `PROVINCE_NAME` | `ProvinceNameRaw` | `DimSite` attribute; canonicalize |
| `PTT_TECHNICIAN_TIME` | QA then remove | Duplicate of `TECHNICIAN_TIME` after parsing |
| `PTT_TECHNICIAN_STATUS` | QA then remove | Compare with technician status; 43 differences |
| `PTT_CALLCENTER_TIME` | `CallCenterTimeMinutes` | Numeric parsed from text |
| `PARENT_GROUP_NAME` | `ParentServiceGroupName` | `DimServiceGroup` attribute |
| `USER_UPDATED_NEW` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_ASSIGNED` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_TO_TECHNICIAN` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_ON_THE_WAY` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_INPROGRESS` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_RESOLVED` | Remove before Load | Personal/user identifier |
| `USER_UPDATED_CLOSED` | Remove before Load | Personal/user identifier |
| `GRADE` | `SiteGradeRaw` | `DimSite` attribute |
| `เลข Asset (จริงหน้างาน,CAMS (รอเช็ค))` | `AssetKey` | Normalized text; `UNKNOWN` when blank |
| `ตรวจสอบ PMORDER` | QA then remove | Exact duplicate of normalized `PMORDER` in current file |
| `จำนวนยอดเงิน` | `RecordedCostTHB` | Decimal currency; VAT basis not yet verified |

### 4.4 Derived columns in `stg_ServiceTracking`

สร้างคอลัมน์ต่อไปนี้ใน Power Query เพื่อให้ DAX เบาและตรวจสอบได้:

| Column | Logic |
|---|---|
| `ServiceDate`, `AssignedDate`, `WorkInProgressDate`, `ResolvedDate`, `CloseDate` | `Date.From` ของ DateTime ที่ parse แล้ว |
| `ServiceDateKey` etc. | `YYYYMMDD` integer; null เมื่อวันที่ไม่มี |
| `DerivedYearMonth` | `Date.ToText([ServiceDate], "yyyy-MM")` |
| `IsSourceYearMonthConsistent` | `SourceYearMonth = DerivedYearMonth` |
| `ElapsedMinutesFromTimestamps` | `Duration.TotalMinutes(CloseDateTime - ServiceDateTime)` |
| `DurationVarianceMinutes` | `LeadTimeMinutes - ElapsedMinutesFromTimestamps` |
| `IsDurationConsistent` | absolute variance <= 1 minute |
| `IsDateSequenceValid` | milestone ที่มีค่าต้องไม่ก่อน `ServiceDateTime` และต้องเรียงตาม business rule |
| `IsSLAMet` | normalized `SLA_STATUS = "Met"`; null เมื่อไม่ประเมิน |
| `IsSLAConsistent` | source status ตรงกับ `LeadTimeMinutes <= SLATargetMinutes` |
| `IsTechnicianSLAMet` | normalized technician status |
| `IsClosed` | `SERVICE_STATUS_DESC = "Closed"` |
| `IsIssueClassified` | symptom hierarchy ไม่เป็น blank/unknown ทั้งชุด |
| `HasAssetReference` | normalized asset ไม่เป็น null |
| `IsAssetMatched` | nullable Boolean จาก Asset master; ต้องเป็น null จนกว่าจะมี master |
| `IsSAPOrderMatched` | nullable Boolean จาก SAP extract; ต้องเป็น null จนกว่าจะตรวจจริง |
| `IsRecordedCostValid` | amount ไม่เป็น nullและ >= 0 |

ตัวอย่าง core derivation:

```powerquery
let
    AddServiceDate = Table.AddColumn(PreviousStep, "ServiceDate", each Date.From([ServiceDateTime]), type date),
    AddDerivedMonth = Table.AddColumn(AddServiceDate, "DerivedYearMonth", each Date.ToText([ServiceDate], "yyyy-MM"), type text),
    AddElapsed = Table.AddColumn(
        AddDerivedMonth,
        "ElapsedMinutesFromTimestamps",
        each if [ServiceDateTime] = null or [CloseDateTime] = null
             then null
             else Duration.TotalMinutes([CloseDateTime] - [ServiceDateTime]),
        type number
    ),
    AddVariance = Table.AddColumn(
        AddElapsed,
        "DurationVarianceMinutes",
        each if [LeadTimeMinutes] = null or [ElapsedMinutesFromTimestamps] = null
             then null
             else [LeadTimeMinutes] - [ElapsedMinutesFromTimestamps],
        type number
    ),
    AddDurationFlag = Table.AddColumn(
        AddVariance,
        "IsDurationConsistent",
        each if [DurationVarianceMinutes] = null then null else Number.Abs([DurationVarianceMinutes]) <= 1,
        type logical
    ),
    AddSLAFlag = Table.AddColumn(
        AddDurationFlag,
        "IsSLAConsistent",
        each if [IsSLAMet] = null or [LeadTimeMinutes] = null or [SLATargetMinutes] = null
             then null
             else [IsSLAMet] = ([LeadTimeMinutes] <= [SLATargetMinutes]),
        type logical
    )
in
    AddSLAFlag
```

### 4.5 Duplicate policy

ห้ามใช้ `Table.Distinct` เพื่อลบ duplicate แบบเงียบ ๆ ให้สร้าง `qa_DuplicateServiceID` แล้ว fail refresh เมื่อพบ key ซ้ำ:

```powerquery
let
    Grouped = Table.Group(stg_ServiceTracking, {"ServiceID"}, {{"RowCount", each Table.RowCount(_), Int64.Type}}),
    Duplicates = Table.SelectRows(Grouped, each [ServiceID] = null or [RowCount] <> 1),
    Asserted = if Table.RowCount(Duplicates) > 0
               then error "FactServiceOrder grain violation: SERVICE_ID is blank or duplicated."
               else stg_ServiceTracking
in
    Asserted
```

## 5. Star schema

### 5.1 `FactServiceOrder` contract

| Column group | Columns |
|---|---|
| Business identifiers | `ServiceID`, `ServiceNo`, `PMOrder` |
| Foreign keys | `SiteKey`, `VendorKey`, `ServiceGroupKey`, `AssetKey`, `WorkTypeKey`, `SeverityKey`, `SAPOrderTypeKey`, `ServiceStatusKey`, `SymptomKey`, `ResolutionKey` |
| Date keys | `ServiceDateKey`, `AssignedDateKey`, `WorkInProgressDateKey`, `ResolvedDateKey`, `CloseDateKey` |
| Timestamps | `ServiceDateTime`, `AssignedDateTime`, `WorkInProgressDateTime`, `ResolvedDateTime`, `CloseDateTime` |
| Engineering measures | `SLATargetMinutes`, `LeadTimeMinutes`, `TechnicianTimeMinutes`, `CallCenterTimeMinutes`, `ElapsedMinutesFromTimestamps`, `DurationVarianceMinutes` |
| Financial proxy | `RecordedCostTHB` |
| Status flags | `IsSLAMet`, `IsTechnicianSLAMet`, `IsClosed` |
| Quality/match flags | `IsSourceYearMonthConsistent`, `IsDurationConsistent`, `IsDateSequenceValid`, `IsSLAConsistent`, `IsIssueClassified`, `HasAssetReference`, `IsAssetMatched`, `IsSAPOrderMatched`, `IsRecordedCostValid` |

ตั้ง `ServiceID`, `ServiceNo`, `PMOrder` และ raw status fields เป็น Hide in report view; ให้เปิดเฉพาะ drill-through ที่ได้รับอนุญาต

### 5.2 Dimensions

| Dimension | Key | Attributes/logic |
|---|---|---|
| `DimDate` | `DateKey` | Calendar attributes, official-period flags |
| `DimSite` | normalized `SiteKey` | Canonical site name, province, grade, ambiguity flags |
| `DimVendor` | normalized vendor name initially | Vendor code/name; replace with approved master key later |
| `DimServiceGroup` | normalized group name initially | Group ID/name/parent; preserve ambiguity flag |
| `DimAsset` | normalized `AssetKey` | Current source has only reference; enrich from Asset master |
| `DimWorkType` | `WorkTypeKey` | PM/CM and description |
| `DimSeverity` | `SeverityKey` | Source code, description, SLA target minutes |
| `DimSAPOrderType` | `SAPOrderTypeKey` | Order type and description |
| `DimServiceStatus` | normalized status description | Source code and description |
| `DimSymptom` | deterministic composite `SymptomKey` | Problem type → object part → item → problem detail → damage |
| `DimResolution` | normalized `ResolutionKey` | Resolution description |
| `ModelControl` | one row only | Baseline/target/cutoff/tolerances/approval statuses |
| `SecurityUserSite` | `UserUPN` + `SiteKey` | Disconnected RLS mapping; not visible to report users |

Current workbook has 104 distinct symptom combinations without free text และ 22 resolution states including unknown ซึ่งเหมาะกับ dimensions; ห้ามรวม `CALL_DETAIL` เพราะจะทำ cardinality เพิ่มเป็นเกือบระดับรายการและมีความเสี่ยงด้านข้อมูลส่วนบุคคล

### 5.3 Canonical site rule

`SITE_ID` ต้องเป็น key หลัก แต่พบ 35 keys ที่มีหลายชื่อ, 22 keys ที่มีหลายจังหวัด และ 5 keys ที่มีหลาย grade:

1. ถ้ามี approved Site master ให้ master เป็นผู้ชนะเสมอ
2. ก่อนมี master ให้เลือกค่าที่ nonblank ล่าสุดตาม `CloseDateTime`
3. เพิ่ม `SiteNameVariantCount`, `ProvinceVariantCount`, `GradeVariantCount`
4. ตั้ง `IsNameAmbiguous = SiteNameVariantCount > 1`
5. แสดง ambiguity ใน Data Quality page และห้ามใช้ชื่อ raw เป็น relationship key

### 5.4 Unknown member policy

แต่ละ dimension ต้องมี member `UNKNOWN` หนึ่งแถวเพื่อป้องกัน orphan facts ห้าม drop แถว fact เพราะ dimension attribute หาย และห้ามแปลง Unknown เป็นค่าปกติ

`AssetKey = UNKNOWN` หมายถึง “ยังไม่มี reference” ไม่ใช่ “ไม่ match master” ส่วน `IsAssetMatched = null` หมายถึงยังไม่ได้ประเมินกับ master

## 6. Relationships

กำหนดทุก relationship เป็น dimension `1` → fact `*`, single-direction filter และไม่ใช้ bidirectional ยกเว้นแบบจำลอง security ที่ผ่านการทดสอบแล้ว

| From | To | Active | Filter |
|---|---|---:|---|
| `DimDate[DateKey]` | `FactServiceOrder[ServiceDateKey]` | Yes | Single |
| `DimDate[DateKey]` | `FactServiceOrder[AssignedDateKey]` | No | Single |
| `DimDate[DateKey]` | `FactServiceOrder[WorkInProgressDateKey]` | No | Single |
| `DimDate[DateKey]` | `FactServiceOrder[ResolvedDateKey]` | No | Single |
| `DimDate[DateKey]` | `FactServiceOrder[CloseDateKey]` | No | Single |
| `DimSite[SiteKey]` | `FactServiceOrder[SiteKey]` | Yes | Single |
| `DimVendor[VendorKey]` | `FactServiceOrder[VendorKey]` | Yes | Single |
| `DimServiceGroup[ServiceGroupKey]` | `FactServiceOrder[ServiceGroupKey]` | Yes | Single |
| `DimAsset[AssetKey]` | `FactServiceOrder[AssetKey]` | Yes | Single |
| `DimWorkType[WorkTypeKey]` | `FactServiceOrder[WorkTypeKey]` | Yes | Single |
| `DimSeverity[SeverityKey]` | `FactServiceOrder[SeverityKey]` | Yes | Single |
| `DimSAPOrderType[SAPOrderTypeKey]` | `FactServiceOrder[SAPOrderTypeKey]` | Yes | Single |
| `DimServiceStatus[ServiceStatusKey]` | `FactServiceOrder[ServiceStatusKey]` | Yes | Single |
| `DimSymptom[SymptomKey]` | `FactServiceOrder[SymptomKey]` | Yes | Single |
| `DimResolution[ResolutionKey]` | `FactServiceOrder[ResolutionKey]` | Yes | Single |

Facts ใน Phase 2 ใช้ conformed dimensions เดียวกันตาม grain และ date role ของแต่ละ fact

## 7. Date strategy

### 7.1 Calendar

- สร้าง `DimDate` ตั้งแต่ต้นปีของวันที่ต่ำสุดถึงสิ้นปีของวันที่สูงสุดใน facts
- Mark as date table ด้วย `DimDate[Date]`
- ใช้ calendar year เป็นค่าเริ่มต้น; Fiscal year ต้องยืนยันกับ Finance ก่อนเพิ่ม
- เพิ่ม `DateKey`, `Date`, `Year`, `Quarter`, `MonthNumber`, `MonthNameTH`, `YearMonth`, `MonthStart`, `MonthEnd`, `IsWeekend`
- Sort `MonthNameTH` by `MonthNumber`, sort `YearMonth` by `MonthStart`

### 7.2 Date role

- Slicer หลักใช้ `ServiceDateKey`
- Measures ที่นับ closed/resolved/assigned ใช้ `USERELATIONSHIP`
- หากผู้ใช้ต้อง filter หลาย date roles พร้อมกัน ให้สร้าง role-playing dimensions (`DimCloseDate`, `DimResolvedDate`) ใน Phase 3 แทนการเปิด bidirectional

### 7.3 Timezone

timestamps ใน workbook เป็น local wall-clock time และไม่มี timezone offset ให้ตีความเป็น `Asia/Bangkok` โดยไม่แปลงซ้ำเป็น UTC ใน Fact

`RefreshAudit` ต้องเก็บทั้ง UTC และ local timestamp อย่างชัดเจน เช่น `RefreshFinishedAtUTC` และ `RefreshFinishedAtLocal`

### 7.4 Official period cutoff

ห้ามใช้ `TODAY()` หรือ max transaction date เป็น official cutoff โดยตรง

`ModelControl[OfficialThroughDate]` ต้องมาจากการ sign-off ของ Data owner/Finance และเป็น blank จนกว่าจะอนุมัติ DAX จะมี `Provisional Complete Date` สำหรับ DEV แต่ KPI ทางการใช้ `Official Complete Date` เท่านั้น

## 8. `ModelControl` one-row table

สร้างเป็น controlled SharePoint list/table หรือ Power Query table ชั่วคราวใน DEV:

| Column | Initial value | Rule |
|---|---|---|
| `BaselineYear` | 2025 | เปลี่ยนหลัง governance approval เท่านั้น |
| `ReductionTargetPct` | 0.20 | เป้าหมายโครงการ |
| `CoreClassificationThresholdPct` | 0.95 | Data gate |
| `AssetMatchThresholdPct` | 0.98 | ต้องมี Asset master ก่อนประเมิน |
| `SAPMatchThresholdPct` | 0.98 | ต้องมี SAP extract ก่อนประเมิน |
| `ReconciliationTolerancePct` | 0.01 | Finance gate |
| `BaselineApprovalStatus` | `PENDING` | `APPROVED` เมื่อ Finance sign-off |
| `OfficialThroughDate` | null | ใส่หลัง period complete/lock |
| `SafetyGuardrailStatus` | `PENDING` | `PASS` เมื่อ evidence ครบ |
| `StatutoryComplianceStatus` | `PENDING` | `PASS` เมื่อ legal KPI ครบ |

ห้ามให้ report viewer แก้ตารางนี้โดยตรง และต้องเก็บ change history

## 9. KPI tree

### 9.1 Objective

ลด OPEX งานซ่อมบำรุง/ทดสอบอย่างน้อย 20% เทียบ approved 2025 baseline โดยไม่ลดความปลอดภัยและการปฏิบัติตามกฎหมาย

### 9.2 Primary KPIs

1. `Exposure Reduction %` — เปรียบเทียบ Actual + Open Commitment + Accrual กับ baseline comparable period
2. `Finance Approved Net Saving` — Saving ledger ที่ Finance อนุมัติแล้ว
3. `Gap to Reduction Target` — ส่วนต่างจากเป้าหมาย 20%

ทั้งสาม KPI ยังผลิตอย่างเป็นทางการไม่ได้จาก workbook นี้เพียงไฟล์เดียว

### 9.3 Current-source proxy KPIs

- `Recorded Cost`
- `Recorded Cost Reduction Proxy %`
- `Work Order Count`
- `Average Recorded Cost per Work Order`
- `CM Cost Share %`
- `SLA Compliance %`
- `Average/P95 Lead Time Hours`

ทุกชื่อที่เป็น proxy ต้องมีคำว่า `Recorded` หรือ `Proxy` บน card/tooltip เพื่อไม่ให้ผู้ชมเข้าใจว่าเป็น Finance Actual

### 9.4 Drivers

| Primary KPI | Driver | Action enabled |
|---|---|---|
| Exposure reduction | CM volume, CM cost, cost/job | Demand avoidance, PM redesign |
| Exposure reduction | Symptom/asset/vendor Pareto | RCA, bad-actor, commercial action |
| Exposure reduction | Repeat 30/90D | Repair-vs-replace, warranty |
| Approved saving | Validated avoided dispatch | Safe self-maintenance |
| Approved saving | Price/rate variance | Negotiation, rate card |
| Gap to target | Monthly run-rate and forecast | Reallocate saving levers |

### 9.5 Guardrails

- Finance reconciliation variance <= 1%
- Core classification coverage >= 95%
- Asset match >= 98% after master evaluation
- SAP order match >= 98% after SAP evaluation
- Duplicate Service ID = 0
- Statutory compliance = 100%
- Safety incident = 0
- Reopen after self-maintenance <= 5%
- Official period and baseline approved

### 9.6 Availability matrix

| Metric family | Current workbook | Production status |
|---|---|---|
| Volume/recorded cost/work type | Available | Use after UAT |
| SLA/lead time | Available with quality flags | Use after resolving exceptions |
| Site/vendor/symptom dimensions | Available but need master cleanup | Provisional |
| Asset capture | Available (10.72%) | Not an Asset match KPI |
| SAP actual/commitment/accrual | Not available | Block official exposure |
| Finance-approved saving | Not available | Block official saving |
| Repeat repair | Insufficient asset coverage/master | Do not publish yet |
| Self-maintenance/reopen | Not available | Phase 3 |
| Statutory/safety | Not available | Must remain guardrail `PENDING` |

## 10. DAX implementation order

1. สร้าง tables/columns ตามชื่อในเอกสารนี้
2. สร้าง `ModelControl`
3. Import Phase 1 block จาก `measures-v2.dax`
4. ตั้ง Format string และ Display folder ตาม comment ในไฟล์
5. ตรวจ aggregate benchmarks
6. เพิ่ม Phase 2 facts และ active date relationships
7. Import Phase 2 block
8. เปิด `Official Saving KPI Display` เฉพาะเมื่อ `Publication Readiness Status = READY`

อย่าสร้าง calculated columns สำหรับ aggregations ที่ทำเป็น measure ได้ และห้ามใช้ implicit measures ใน visuals

## 11. RLS และการคุ้มครองข้อมูล

### 11.1 Scope ที่ทำได้จาก source ปัจจุบัน

Workbook ไม่มี AM/user-to-scope mapping ที่เชื่อถือได้ จึงยังทำ AM RLS จาก source นี้เพียงอย่างเดียวไม่ได้ ให้ใช้ external `SecurityUserSite` ที่มี:

- `UserUPN`
- `SiteKey`
- `ValidFrom`
- `ValidTo`
- `IsActive`
- `ApprovedByRole`

ถ้าสิทธิ์กำหนดเป็นกลุ่ม ให้ expand Group → Site upstream ก่อนโหลด security table

### 11.2 Recommended role

- `RLS_SiteViewer`: filter `DimSite` จาก disconnected `SecurityUserSite`
- `BI_Admin`: workspace role ที่ไม่ใช้ RLS; จำกัดจำนวนผู้ใช้
- `Finance_Reviewer`: ใช้ workspace/app audience และหากจำเป็นใช้ OLS ซ่อน transaction identifiers

RLS expression มีตัวอย่างแบบ comment ใน `measures-v2.dax`

### 11.3 Privacy controls

- Personal/user columns และ free text ถูกตัดใน staging ก่อน Load
- RLS ไม่ใช่เครื่องมือป้องกันผู้มี Build permission; ผู้มี Build สามารถ query model ตามสิทธิ์ของตนได้
- ถ้าต้องใช้ชื่อช่างหรือ audit trail ให้ทำ restricted dataset แยก ไม่เพิ่มลงโมเดล executive
- Export underlying data ให้ปิดเป็นค่าเริ่มต้นสำหรับ report audience ที่ไม่จำเป็น
- Business identifiers ให้ Hide in report view และใช้ drill-through เฉพาะกลุ่มที่อนุมัติ

### 11.4 RLS tests

ทดสอบอย่างน้อย:

1. User มี 1 site
2. User มีหลาย site
3. User ไม่มี mapping ต้องเห็น 0 rows
4. Mapping หมดอายุ
5. UPN casing ต่างกัน
6. Viewer export data
7. App audience แยก Operations/Finance

## 12. Refresh strategy

### 12.1 Current Excel phase

- Storage: SharePoint/OneDrive controlled library
- Mode: Import
- Refresh: ตาม SLA ปฏิบัติการและ license; เริ่ม 4 รอบ/วันและวัดความต้องการจริง
- Privacy level: Organizational
- Local absolute path: DEV only
- Incremental refresh: ไม่แนะนำกับ Excel ขนาดนี้ เพราะไม่มี query folding และปริมาณเพียง 1,586 rows

### 12.2 Production source phase

- ย้าย Service Tracking/SAP facts ไป Dataflow Gen2, SQL หรือ Lakehouse ที่รองรับ query folding
- ใช้ incremental refresh เมื่อ transaction fact โตและ source รองรับ `RangeStart`/`RangeEnd`
- แยก refresh cadence: service intake เร็วกว่า Finance/SAP
- แสดง source freshness แยก ไม่ใช้ refresh timestamp เดียวแทนทุก source
- ตั้ง refresh failure alert และ owner/escalation path

### 12.3 `RefreshAudit`

อย่างน้อยเก็บ:

- `SourceName`
- `SourceModifiedAt`
- `RefreshStartedAtUTC`
- `RefreshFinishedAtUTC`
- `RefreshFinishedAtLocal`
- `RowsRead`
- `RowsLoaded`
- `MaxServiceDate`
- `MaxCloseDate`
- `DuplicateServiceIDCount`
- `RefreshStatus`

## 13. Validation และ reconciliation

### 13.1 Power Query assertions

| Test | Current benchmark | Release rule |
|---|---:|---|
| Rows loaded | 1,586 | ต้องอธิบาย delta ทุก refresh |
| Distinct Service ID | 1,586 | ต้องเท่ากับ rows |
| Exact duplicates | 0 | ต้องเป็น 0 |
| Work type accepted values | PM/CM only | ค่าอื่นเข้า exception queue |
| Negative recorded amount | 0 | ต้องเป็น 0 เว้นแต่มี signed reversal design |
| Invalid source month | 1 | ต้องแก้หรือ quarantine; model ใช้ derived month |
| Date sequence exceptions | 2 assigned-before-service | ต้องมี owner disposition |
| Duration variance >1 minute | 1 | ต้องมี owner disposition |
| SLA rule mismatch | 0 จาก 1,449 evaluated | ต้องเป็น 0 |
| Site ID with name ambiguity | 35 | ลดด้วย Site master |

### 13.2 Aggregate reconciliation benchmarks

| Slice | Count | Recorded cost |
|---|---:|---:|
| All data | 1,586 | 19,853,145.19 |
| 2024 by `SERVICE_DATE` | 1 | 135,006.80 |
| 2025 by `SERVICE_DATE` | 1,123 | 15,331,857.14 |
| 2026 by `SERVICE_DATE` | 462 | 4,386,281.25 |
| 2025 CM by `SERVICE_DATE` | 975 | 13,226,635.84 |
| 2025 PM by `SERVICE_DATE` | 148 | 2,105,221.30 |

`qa_CostSummary` มีหนึ่ง overall row ที่ count และยอดรวมตรงกับ Fact ทั้งหมด 1,586 และ 19,853,145.19 แต่ไม่มีสูตร/lineage จึงใช้เป็น control check เท่านั้น

### 13.3 Finance reconciliation bridge

สร้าง reconciliation table/report ตามลำดับ:

`Service recorded amount → matched SAP actual → unmatched service → unmatched SAP → open commitment → accrual → approved exclusion → Finance control total`

ต้องแสดงทั้งจำนวนรายการและมูลค่า พร้อม drill-through สำหรับ reviewer ที่มีสิทธิ์

ห้ามหัก unmatched records ออกจากยอดเพื่อให้ variance ผ่าน

### 13.4 Semantic/DAX tests

1. `[Rows Loaded] = 1,586`
2. `[Work Order Count] = 1,586`
3. `[Duplicate Service ID Count] = 0`
4. `[Recorded Cost] = 19,853,145.19`
5. Filter PM/CM แล้วผลรวมกลับมาเท่ากับ total
6. ปี 2025 จาก `DimDate` ต้องได้ 15,331,857.14 ไม่ใช่ยอดจาก `MM`
7. Closure measure ใช้ inactive close-date relationship และตอบตาม close period
8. Official comparable measures เป็น blank เมื่อ `OfficialThroughDate` เป็น blank
9. `Publication Readiness Status` ต้อง blocked จนทุก gate ผ่าน
10. Totals ใน matrix ต้องเท่ากับ card ภายใต้ filter context เดียวกัน

### 13.5 UAT/operational tests

- Partial month แสดง warning
- Tooltip แสดง definition, date basis, source, freshness และ status
- Unknown ไม่หายเมื่อ filter PM/CM
- RLS no-mapping user เห็น 0 rows
- Finance variance ใช้ signed reversals ถูกต้อง
- Commitment ที่ Cancelled/Invoiced ไม่ค้างใน Open Commitment
- Accrual ถูก reverse เมื่อ actual posted
- Baseline, target และ cutoff เปลี่ยนได้เฉพาะ controlled process

## 14. Phased implementation

### Phase 0 — Governance and decision lock (1–3 วัน)

Deliverables:

- Baseline scope and exclusion decision
- Canonical date = `SERVICE_DATE` sign-off
- Currency/VAT basis confirmation
- KPI owner, Finance owner, Data owner, HSE owner
- `ModelControl` ownership and change process

Exit:

- Baseline status ไม่ใช่ `PENDING`
- Definition ของ Recorded Cost vs Finance Actual ได้รับอนุมัติ
- Safety/statutory publication rules ได้รับอนุมัติ

### Phase 1 — Clean staging and current-source model (3–5 วัน)

Deliverables:

- Power Query functions and staging queries
- PII/free-text exclusion
- QA exception queries
- `FactServiceOrder` + dimensions + relationships
- Phase 1 DAX and Data Quality page

Exit:

- Grain assertion ผ่าน
- Aggregate benchmarks ผ่านทั้งหมด
- วันที่/ระยะเวลา exception มี disposition
- Site ambiguity แสดงใน QA page

### Phase 2 — Finance truth and publication gate (1–2 sprints)

Deliverables:

- SAP actual, commitment, accrual and Finance control facts
- Service-to-SAP matching bridge
- Signed reversal handling
- Exposure/reconciliation measures
- Approved cutoff and baseline control

Exit:

- Finance reconciliation variance <= 1%
- SAP match >= 98%
- Asset match >= 98% สำหรับ records ที่ควรมี asset
- `Publication Readiness Status = READY`

### Phase 3 — Reliability and saving ledger (1–2 sprints)

Deliverables:

- Asset/Symptom masters
- Repeat repair 30/90D logic
- Maintenance action/self-maintenance fact
- Saving ledger and evidence workflow
- PM/legal compliance fact

Exit:

- Repeat logic validated against sampled work histories
- Self-maintenance reopen <= approved threshold
- Safety = PASS และ Statutory = PASS
- Finance-approved saving reconciles to ledger

### Phase 4 — Production hardening and rollout (1 sprint)

Deliverables:

- DEV/TEST/PROD deployment process
- RLS/OLS and app audiences
- Refresh audit/alerts
- Performance Analyzer and model-size review
- UAT evidence and release checklist

Exit:

- RLS tests ผ่าน
- Refresh SLA ผ่านต่อเนื่อง
- Executive cards, detailed pages and exports reconcile
- Owner/runbook พร้อมใช้งาน

## 15. Assumptions และรายการที่ต้องยืนยัน

1. `SERVICE_ID` เป็น authoritative service-order key; current file ยืนยัน uniqueness แต่ต้อง assert ทุก refresh
2. `SERVICE_DATE` เป็น reported/opened date และเป็น canonical analysis date
3. Duration fields ใช้หน่วยนาทีตามความสัมพันธ์กับ timestamps และ SLA rule
4. Source timestamps เป็น Asia/Bangkok local time
5. `จำนวนยอดเงิน` ใช้สกุล THB ตามบริบทธุรกิจ แต่ VAT basis ยังไม่ยืนยัน จึงใช้ชื่อ `RecordedCostTHB`
6. `MM` เป็น derived/helper field ไม่ใช่ source of truth
7. `TECHNICIAN_STATUS` เป็น reporting source ชั่วคราว; PTT variant ใช้ QA เท่านั้น
8. Missing Asset reference ไม่เท่ากับ Asset match failure จนกว่าจะมี Asset master
9. Current workbook ไม่มี accounting-line grain, commitment, accrual, saving approval, AM security map, safety incident หรือ statutory compliance
10. Baseline year 2025 และ target 20% เป็นค่าเริ่มต้นจากเอกสารเดิม แต่ approval ต้องเก็บใน `ModelControl`
11. เอกสารนี้เก็บเฉพาะ schema, aggregate checks และ implementation logic ไม่เก็บชื่อบุคคล ค่า identifier จริง หรือรายละเอียด raw
