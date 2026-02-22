# Android signing prerequisites checklist

Use this checklist before enabling signed Play Store release builds.

## Keystore and keys

- [ ] Production upload keystore generated and stored securely (offline backup + vault)
- [ ] Keystore alias documented in secure secrets manager
- [ ] Keystore password stored in secure secrets manager
- [ ] Key password stored in secure secrets manager
- [ ] Rotation / recovery owner identified

## CI secrets

- [ ] `ANDROID_KEYSTORE_BASE64` added
- [ ] `ANDROID_KEYSTORE_PASSWORD` added
- [ ] `ANDROID_KEY_ALIAS` added
- [ ] `ANDROID_KEY_PASSWORD` added
- [ ] Secrets scoped to correct repo/environment
- [ ] Branch protection and required checks configured

## Build/release readiness

- [ ] `VERSION` file matches `versionName` in `app/build.gradle.kts`
- [ ] `versionCode` incremented for each Play upload candidate
- [ ] `Android Play Internal CD` workflow tested with `upload_enabled=false`
- [ ] `Android Play Internal CD` workflow tested with `upload_enabled=true`
- [ ] Artifact retention window reviewed
- [ ] Release notes process defined

## Store integration

- [ ] Google Play Console app created/configured
- [ ] Service account (if used) scoped minimally
- [ ] Internal track upload test completed
- [ ] Rollback procedure documented
