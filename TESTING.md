# Tests and acceptance evidence

## Executed locally in this handoff
- Pure Python unit tests for offline event validation and idempotency hashing.
- Static schema audit of all DocTypes, fields, local links, controller paths, roles, and permissions.
- Python syntax compilation.

## Not executable without a Frappe v16 bench
- Actual `bench get-app`, `install-app`, `migrate` and `bench execute` inside a site.
- Integration/API checks for mobile login/CSRF, multi-farm roles, stock transfer, duplicate transaction across concurrent HTTP requests, upgrade/restore and offline browser tests.

## Staging acceptance matrix
| ID | Scenario | Expected outcome | Status |
|---|---|---|---|
| T-01 | Install on a clean ERPNext v16 site | 100 WFM DocTypes import and all role references resolve | Not run |
| T-02 | Create Farm/Zone/Field | Company must match across linked records | Not run |
| T-03 | A farm operator without `WFM User Farm Access` | No farm visible through mobile API | Not run |
| T-04 | Farm A operator attempts to log event in Farm B | Rejected | Not run |
| T-05 | Record 30 events offline then sync twice | Only 30 new `WFM Field Log` records | Not run |
| T-06 | Change payload while keeping same event UUID | Returned as conflict | Not run |
| T-07 | Create Bird Pair using two males | Rejected | Not run |
| T-08 | Enter 100 eggs, allocate 110 | Rejected | Not run |
| T-09 | Bird mortality with individual ring and count=2 | Rejected | Not run |
| T-10 | Assign bird/pond from another farm | Rejected | Not run |
| T-11 | Try enabling `control_enabled` on Device | Rejected; nothing actuated | Not run |
| T-12 | Feed/harvest entries without ERPNext Stock Entry | No automatic or duplicate Stock Entry (known alpha limitation) | Not run |
| T-13 | Full backup + upgrade + restore rehearsal | Data, files, roles and integrity intact | Not run |
| T-14 | Offline shared-device user change | Old user's queue must not be sent under another identity | Not run |
| T-15 | Test on Android Chrome and iOS Safari | No data loss; reauth and storage behaviors documented | Not run |

## Commands from repository root (local tests only)
```bash
python -m unittest discover -s tests -v
python tools/check_schema.py
python -m compileall -q wadi_farm
```

## Commands on staging site only
```bash
bench --site YOUR_STAGING_SITE execute wadi_farm.qa.smoke.run_smoke_checks
bench --site YOUR_STAGING_SITE run-tests --app wadi_farm
```

Do not claim certification for OT safety, animal withdrawal rules, production accounting or regulatory compliance from these tests.
