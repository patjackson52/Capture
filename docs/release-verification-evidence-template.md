# Android Internal Release Verification Evidence Template

Copy this into the release PR description or release issue.

## Release identity
- Date/UTC:
- Operator:
- Version (`VERSION`/`versionName`):
- `versionCode`:
- Previous tag:
- Previous `versionCode`:
- Tag pushed:
- Target commit SHA:

## Dry-run evidence (required)
- Workflow URL (dispatch, `upload_enabled=false`):
- Result: pass/fail
- Artifact name:
- `aab_sha256` from metadata:
- Validation notes:

## Upload run evidence
- Workflow URL (tag-triggered):
- Result: pass/fail
- `release_status` used:
- Upload requested = true (yes/no):
- Missing secrets reported (should be `none`):

## Play Console verification
- Internal release visible (yes/no):
- Track status (`draft`/`inProgress`/`completed`):
- Package name:
- Screenshot/link evidence:

## QA sign-off
- Tester(s):
- Device matrix:
- Smoke tests executed:
- Result:
- Blocking issues:

## Go/No-go
- Engineering owner approval:
- QA approval:
- Product/release approval:
- Final decision: GO / NO-GO
- Notes:

## Rollback readiness
- Previous known-good versionCode:
- Rollback owner:
- Rollback comms channel:
