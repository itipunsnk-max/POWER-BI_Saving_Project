# Power BI Data Contract

## FactServiceOrder

Grain: 1 row per Service ID

| Field | Type | Rule |
|---|---|---|
| ServiceID | Text | Required, unique |
| ReportedDateTime | DateTime | Required, Asia/Bangkok |
| CompletedDateTime | DateTime | Null while open |
| WorkTypeCode | Text | PM or CM only |
| SymptomCode | Text | Required before dispatch |
| RootCauseCode | Text | Required before technical close |
| ResolutionCode | Text | Required before financial close |
| AssetKey | Text | Required when asset exists |
| LocationKey | Text | Required |
| VendorKey | Text | Null for self maintenance |
| SeverityCode | Text | Critical/Urgent/Routine |
| MaintenanceLevel | Text | L0/L1/L2/L3 |
| IsRepeat30D | Boolean | Derived from Asset + Symptom |
| IsRepeat90D | Boolean | Derived from Asset + Symptom |
| IsSelfMaintenance | Boolean | Must have approved SOP |
| ReopenedWithin30D | Boolean | Reverses avoided saving |
| DowntimeHours | Decimal | Non-negative |
| SourceSystem | Text | Traceability |
| SourceUpdatedAt | DateTime | Freshness |

## FactCostTransaction

Grain: 1 row per SAP accounting document line

Required fields:

- AccountingDocumentID, LineID, ServiceID, InternalOrder
- PostingDate, CostElement, AmountExVAT, Currency
- CostStatus = Actual
- VendorKey, AssetKey, LocationKey
- IsReversal, ReversedDocumentID
- SourceUpdatedAt

## FactCommitment

Grain: 1 row per PO/PR/invoice-pending line

Required fields:

- CommitmentID, ServiceID, PO/PR reference
- ExpectedPostingDate, AmountExVAT
- Status = Open/Received/Invoiced/Cancelled
- SnapshotDate

## FactAccrual

Grain: 1 row per accrued cost estimate at month end

- AccrualID, ServiceID/InternalOrder
- AccrualMonth, AmountExVAT
- AccrualMethod, SourceReference
- ReversedDate when actual cost is posted

## FactMaintenanceAction

Grain: 1 row per action attempt

- ActionID, ServiceID, ActionDateTime
- ActionType = Observe/Remote/Self/Vendor/Statutory
- SOPVersion, PerformedByRole
- Outcome = Resolved/Escalated/Failed
- InterventionCost, StandardDispatchCost
- EvidenceURL

## FactSavingLedger

Grain: 1 row per validated saving event

- SavingID, SavingLever, ServiceID/AssetKey
- BaselineMethod, CounterfactualAmount
- ActualAmount, ImplementationCost, NetSaving
- EvidenceURL
- FinanceStatus, ApprovedDate, ApprovedByRole
- ReversalSavingID when reopened or invalidated

## Dimension masters

### DimWorkType

- `PM`: planned inspection, PM, statutory test
- `CM`: corrective repair, breakdown, other repair, symptom not specified

BM must be mapped into one of the two approved reporting groups or shown as
an explicit exception; do not silently drop it.

### DimSymptom

Minimum hierarchy:

`Asset category → Component → Symptom → Severity`

Never use `0`, blank, `อื่นๆ` or free text as the primary reporting code.
Keep free text as supporting evidence and map unresolved cases to
`UNKNOWN_PENDING_REVIEW`.

## Date rules

- Business timezone: Asia/Bangkok
- Comparable period ends at `LatestCompleteDate`
- Current incomplete month is excluded from official saving
- Finance locked month cannot be rewritten without an audit record
- Display source refresh and finance lock dates separately
