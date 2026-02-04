# Signal Horizon Feature Requests

## Cloud Deployment (Vercel + Modal)

**Status:** Requested  
**Priority:** Medium  
**Requested:** 2026-02-04

### Description
Enable Signal Horizon to be deployed as a web service, allowing users to offer AI music generation on their own websites.

### Proposed Architecture
```
User → Vercel (UI + Auth) → Modal/Replicate (GPU) → Return audio
```

| Component | Platform | Purpose |
|-----------|----------|---------|
| Frontend | Vercel | Static Signal Horizon UI |
| API Gateway | Vercel Edge Functions | Auth, rate limiting, routing |
| GPU Backend | Modal / Replicate / RunPod | Music generation (DiT model) |

### Requirements
- Package DiT model for serverless GPU (Modal.com)
- API authentication layer
- Rate limiting and usage tracking
- Dev mode only (no LLM needed for cover/remix tasks)

### Notes
- Vercel has no GPU support — requires hybrid architecture
- Modal bills per-second, spins up on demand
- Cover/remix tasks skip LLM, reducing complexity
- ACE-Step is MIT licensed (commercial use permitted)
