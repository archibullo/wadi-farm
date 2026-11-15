# Wadi Farm Management (`wadi_farm`) — v0.4.0-alpha

**Status: pre-production install candidate; NOT field-approved.** Frappe v16 and ERPNext v16 are required.

Arabic overview: تطبيق مستقل لإدارة مزرعة وادي النقرة، مع نماذج للحقول والمحاصيل والمياه والري والأبقار والأغنام والطيور والحمام والأسماك والصوب والمعدات والصيانة والتجفيف والمخاطر. هذه نسخة تأسيسية قبل الإنتاج ولا تعني اكتمال تشغيل 26 وحدة.

## Included in this archive

- 100 standard Frappe DocType definitions, each with a Python controller, in 12 business categories, plus an Arabic navigational dashboard (`/farm_dashboard`).
- Farm-level Company consistency, cross-farm link checks, selected animal/egg/quantity constraints.
- Roles and granular DocPerm definitions. Farm operator API requires an explicit `WFM User Farm Access` record in addition to role membership.
- A mobile-ready **offline field log only**: `/assets/wadi_farm/mobile/index.html` (IndexedDB, cached app shell, idempotent sync).
- Authenticated manual telemetry ingestion endpoint, **no equipment actuation**.
- 26-feature requirements, schema design, architecture, workflows, assumptions and acceptance checklist.

## Not implemented yet

Full ERPNext stock/GL automation, cost allocations, approval workflows, accurate headcount/bird population ledgers, full field mapping/GIS, satellite processing, automated weather/irrigation connectors, real-time greenhouse/fish safety control, production dashboards, encrypted offline local storage, tested Proxmox deployment, end-to-end ERPNext v16 site installation, and complete Arabic UI translations.

**Never apply to production before a successful v16 staging install, database backup and end-to-end acceptance tests.**

## Setup and testing

Read [INSTALL.md](INSTALL.md), [TESTING.md](TESTING.md), [ROADMAP.md](ROADMAP.md), and [docs/DECISIONS.md](docs/DECISIONS.md).

## Data entry after a staging install

1. Create/select ERPNext `Company`; verify EGP and chart of accounts.
2. Create `WFM Farm` with unique code and its Company.
3. Create zone, fields, livestock/poultry houses, ponds or greenhouses only as needed.
4. Create farm roles and explicit user-to-farm assignments in `WFM User Farm Access`. Restrict ERPNext Desk users with matching User Permissions for `Company` and `WFM Farm`.
5. Mobile pilot: authenticate on the same HTTPS site, then open `/assets/wadi_farm/mobile/index.html` while connected to cache the application. After that, offline drafts can be recorded and synced later.

## Source code license

MIT. See [LICENSE](LICENSE). No tokens, secrets, host IPs, guest IDs or Proxmox credentials ship in this archive.
