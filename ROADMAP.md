# Delivery roadmap and implementation truth

| Capability | v0.4.0-alpha in delivered code | Subsequent work required |
|---|---|---|
| App packaging, roles, Frappe DocTypes | 100 standard JSON + controllers | Real v16 install and migrations tests |
| Land, crop, water, irrigation | Master and transaction forms | Scheduling, calculations, GIS and ERP Stock postings |
| Cattle and sheep | Individual/group forms + selected validations | Herd ledger, breeding engine, medicines and financial valuation |
| Poultry, pigeons, ducks, chickens, etc. | 18 DocTypes + egg/sex/mortality integrity | Flock population ledger, FCR, hatch calculations, dashboards |
| Aquaculture | 12 DocTypes | Feed FCR, biomass reconciliation, water alert engine |
| Greenhouses | 8 DocTypes | Climate recipes, alerts, local controller integrations |
| Machinery, fuel, maintenance | 8 DocTypes | Asset workflow integration, hourmeter triggers and parts posting |
| Harvest, drying, packaging | 3 DocTypes | ERPNext production stock flow and true costing |
| Field offline data entry | PWA and authenticated idempotent draft API | Media sync, encryption, conflicts UX and device management |
| Device telemetry | Authenticated manual reading API | Supplier adapters, scaling, retention, calibrations and alarming |
| Remote device actuation | Intentionally blocked | OT safety certification and dual approval per device |
| Weather/satellite | Metadata/forms | Providers, imagery storage, raster & NDVI processing |
| Risk, insurance, visitors, SOP, recalls | 9 DocTypes | Approvals, notifications and complete recall workflow |
| ERPNext accounting/stock | Reference links only | Posted stock and GL integration with tests and reconciliations |
| Reporting and Arabic interface | Basic Frappe Desk + Arabic mobile form | Dashboards, translations, Arabic print formats |
| Hosting and backups | Deployment instructions only | Proxmox staging, secure VPN, backups and restore drills |

**Release gate for real farm use:** T-01–T-15 tested on a pinned v16 staging branch, reviewed farm/company permissions, transaction posting and reconciliation, reliable encrypted mobile storage and restore tests.
