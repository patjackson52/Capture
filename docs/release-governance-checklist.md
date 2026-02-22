# Release governance checklist (Android)

Use this checklist before promoting any candidate beyond internal testing.

## 1) Approval gates

- [ ] Engineering owner approves release candidate commit/tag
- [ ] QA sign-off completed on target devices and Android OS versions
- [ ] Product/release manager approval captured (ticket/change record)
- [ ] Security/privacy review completed for permission or data-path changes
- [ ] Branch protection + required checks passing on merge commit

## 2) Staged rollout plan

- [ ] Start in Play **Internal** track only
- [ ] Validate crash-free session baseline and critical funnels
- [ ] Promote to next audience in controlled increments (for example 5% → 20% → 50% → 100%)
- [ ] Monitor errors, ANR rate, performance regressions at each stage
- [ ] Hold progression if thresholds breached

## 3) Rollback triggers

Trigger rollback or halt if any occur:

- [ ] Crash/ANR rate exceeds defined SLO threshold
- [ ] P0/P1 defect confirmed in core user journey
- [ ] Security/privacy incident report received
- [ ] Install/update failures spike above baseline
- [ ] Backend/API incompatibility introduces widespread degradation

## 4) Rollback actions

- [ ] Halt further rollout immediately
- [ ] Revert/replace affected release in Play Console track
- [ ] Post incident update to release channel and stakeholders
- [ ] Open corrective-action issue with owner and due date
- [ ] Record root cause + prevention updates in runbook
