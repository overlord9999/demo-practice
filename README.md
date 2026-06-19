# demo-practice — NDA-Safe Playwright + CI Sandbox

A tiny Playwright + Python project that tests the **public** demo site
**[saucedemo.com](https://www.saucedemo.com)**. It exists for **Phase A, Week A2**
of the QA Skill Matrix (Git & CI/CD) — a repo you can safely push to GitHub and
run CI on, because it contains **zero client/BP data**.

> Companion docs:
> - `outputs/docs/Git_and_CICD_Practice_Plan.md` (the 2-week plan)
> - `outputs/docs/QA_Skill_Matrix_and_Growth_Roadmap.md` (Phase A)
>
> Its NDA-covered sibling, `automation/bp-e2e/`, stays **local-only, never pushed.**

## Setup (one time)

```bash
cd D:\Claude\automation\demo-practice
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
pip install -r requirements.txt
playwright install                  # downloads browser engines

cp .env.example .env                # OPTIONAL — public demo creds are the defaults
```

## Run

```bash
pytest -m smoke                 # fast critical-path checks
pytest -m smoke --headed        # watch the browser
pytest -m smoke --browser firefox
pytest                          # everything (smoke + regression)
pytest --html=report.html --self-contained-html   # with HTML report
```

## Layout

```
demo-practice/
├─ config.py            # reads DEMO_* from env (.env or CI secrets); public defaults
├─ conftest.py          # fixtures: base_url, demo_credentials
├─ pytest.ini           # markers (smoke/regression) + default options
├─ pages/               # Page Object Model
│  ├─ base_page.py
│  ├─ login_page.py
│  └─ inventory_page.py
├─ tests/
│  └─ test_login.py     # login + logout, positive & negative
└─ .github/workflows/ci.yml   # CI: smoke on push, full nightly, manual dispatch
```

## Why saucedemo for CI practice

- **Public sandbox** built for automation — safe to push and run publicly.
- **Stable `data-test` locators** on every control (the gold standard you ask
  BP devs for) — so the suite won't flake on cosmetic UI changes.
- **Documented test users** let you exercise real scenarios:
  `standard_user`, `locked_out_user`, `problem_user`, `performance_glitch_user`
  — all with password `secret_sauce`.

## CI secrets (Week A2)

Even though the creds are public, add them as GitHub **Secrets** to practice the
real pattern — repo **Settings → Secrets and variables → Actions**:

| Secret | Value |
|--------|-------|
| `DEMO_USER` | `standard_user` |
| `DEMO_PASSWORD` | `secret_sauce` |
