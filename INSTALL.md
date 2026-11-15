# Installation guide — ERPNext / Frappe v16

**ALPHA / STAGING ONLY. Site-level installation has not been verified in this authoring environment.**

## Prerequisites
- Working **Frappe 16 and ERPNext 16**, with the Python/Node versions specified by those branches (official v16 migration docs currently specify Python 3.14+ and Node.js 24+).
- A disposable Proxmox VM/LXC or dedicated Frappe bench site in a staging environment. Do not experiment on your production ERPNext site.
- A complete, restorable site backup (database, public/private files and app versions).

## Path A — from your GitHub repository
Commit the *contents* of this archive as the repository root, push to a new repo, and inside your Frappe bench run:

```bash
cd ~/frappe-bench
bench version
bench get-app --branch main https://github.com/YOUR_ACCOUNT/wadi_farm.git
bench --site YOUR_STAGING_SITE install-app wadi_farm
bench --site YOUR_STAGING_SITE migrate
bench build --app wadi_farm
bench --site YOUR_STAGING_SITE list-apps
bench --site YOUR_STAGING_SITE execute wadi_farm.qa.smoke.run_smoke_checks
```

Replace placeholders with your own repo and staging site. Do not invent a repository that has not been published.

## Path B — using the local Git bundle delivered with the package
1. Clone the companion `.bundle` into a local working directory (or initialize a Git repository from the ZIP), then push it to your own GitHub repository.
2. Apply Path A after the repository has been verified.
3. For a lab-only local Git clone, bench may accept a local Git URL, depending on Bench CLI revision; verify `bench get-app --help` on your v16 host before proceeding.

## Initial configuration
- Check `Wadi Farm` app tile on the v16 Desk; if not shown, inspect `add_to_apps_screen` and rebuild assets.
- Create `WFM Farm` (Company is required), then zones and fields.
- Assign users a farm role and `WFM User Farm Access` (one active assignment per user/farm).
- Also set ERPNext User Permissions for `Company` and `WFM Farm` so Desk-based access is restricted, not merely the mobile endpoint.
- Enable only the fields you need initially; there are **100 DocTypes** in the baseline.
- Open the mobile PWA over HTTPS: `/assets/wadi_farm/mobile/index.html`. Browser offline support requires opening it once online.
- See `TESTING.md` for exact smoke/negative/restore checks.

## Upgrade principles

```bash
cd ~/frappe-bench
bench --site YOUR_STAGING_SITE backup --with-files
# Verify backups AND dry-run your desired Git revision on staging.
bench --site YOUR_STAGING_SITE migrate
bench build --app wadi_farm
```

Do not roll back a schema migration by blindly downgrading code. Restore a verified snapshot if needed. Never hard-reset a running farm site to a different app revision without testing.

## Production warning
No tested inventory posts, general ledger integration, equipment control or life-safety control exists in this alpha. A Bench installation that succeeds does not mean all modules are production-safe.
