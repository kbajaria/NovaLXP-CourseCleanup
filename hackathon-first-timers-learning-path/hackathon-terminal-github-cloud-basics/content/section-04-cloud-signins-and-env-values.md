# GCP sign-ins, projects, and environment values (15 minutes)

## Why cloud basics matter in this hackathon
Some track items connect to services such as BigQuery or Maps. That means you may need:

- the right Google account
- the right GCP project
- enabled APIs
- keys, tokens, or other environment values

## Four terms that matter
- **GCP project**: the container for services, billing, settings, and APIs
- **Credential**: a way to prove your app or user identity
- **API key / token**: a secret value that grants access
- **Environment variable**: a named value your app reads at runtime

## Rules beginners should follow
- Never paste secrets into chat, screenshots, or public repos.
- Keep track of which account you are signed into.
- If the instructions say to enable an API, do that before testing code.
- If a value starts with "replace-me", replace it with the real value before running the app.

## Common mismatch
You are signed into one Google account in the Cloud Console, but the workstation or app is still pointed at a different project or credential context. When something looks inconsistent, verify both the signed-in account and the selected project.

## Optional video
Watch: **Getting started with Google Cloud**
https://www.youtube.com/watch?v=GKEk1FzAN1A
