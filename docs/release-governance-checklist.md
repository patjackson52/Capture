# Release governance checklist (Android CD readiness)

Use this checklist before enabling recurring Internal-track CD.

## CD readiness gates

- [ ] `Android CI / build-and-test` required check is enforced on `main`
- [ ] `Docs Link Check / check-doc-links` required check is enforced on `main`
- [ ] `Android Play Internal CD / internal-release` runs clean in dry-run mode
- [ ] Signing and Play secrets are stored in protected environment scope
- [ ] Environment protection rules enabled (required reviewers)
- [ ] Operator runbook reviewed with on-call/release owners

## Approval gates per release

- [ ] Engineering owner approves candidate commit/tag
- [ ] QA sign-off complete for critical paths
- [ ] Product/release owner approves scope + timing
- [ ] Security/privacy review complete for sensitive changes
- [ ] `docs/release-verification-evidence-template.md` completed and attached to PR/issue

## Staged delivery plan

- [ ] Internal first (status `draft` for initial validation)
- [ ] Promote only after acceptance criteria are met
- [ ] Monitor crash/ANR/error budgets for at least one validation window

## Rollback triggers

- [ ] Crash/ANR breach vs baseline
- [ ] P0/P1 defect in core flow
- [ ] Security/privacy incident
- [ ] Significant install/update failure spike

## Rollback response

- [ ] Stop rollout/promotions immediately
- [ ] Replace/deactivate bad release in Play Internal
- [ ] Communicate status + owner + ETA
- [ ] Open corrective action issue with deadline
- [ ] Update runbook/checklist with lessons learned

Related docs:
- Required checks policy: `docs/required-checks.md`
- First rollout execution pack: `docs/android-first-internal-rollout-execution-pack.md`
- Runbook: `docs/release-runbook-basics.md`
- Evidence template: `docs/release-verification-evidence-template.md`
