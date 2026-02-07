# Code Duplication Analysis Report

**Generated:** 2026-02-07 15:20:31

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Duplicate Blocks](#duplicate-blocks)
3. [Recommendations](#recommendations)

---

## 📊 Executive Summary

### Overall Metrics

- **Files Analyzed:** 128
- **Total Lines of Code:** 25,069
- **Duplicate Lines:** 11,743
- **Duplication Percentage:** 46.84%
- **Duplicate Blocks Found:** 921

### Breakdown by Type

- **🔴 Exact Duplicates:** 921
- **🟡 Structural Duplicates:** 0
- **🔵 Pattern Duplicates:** 0

### Assessment

🔴 **Critical** - Excessive duplication, immediate action required

### 🎯 Top File Offenders

Files with the most duplicate code:

1. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts` - 1384/686 LOC (201.7%, 168 blocks)
2. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts` - 1383/802 LOC (172.4%, 181 blocks)
3. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts` - 1296/552 LOC (234.8%, 157 blocks)
4. `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts` - 963/903 LOC (106.6%, 145 blocks)
5. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts` - 922/686 LOC (134.4%, 124 blocks)
6. `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts` - 899/61 LOC (1473.8%, 141 blocks)
7. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts` - 896/428 LOC (209.3%, 121 blocks)
8. `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts` - 874/565 LOC (154.7%, 133 blocks)
9. `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts` - 701/383 LOC (183.0%, 98 blocks)
10. `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts` - 573/265 LOC (216.2%, 74 blocks)

### 🗺️ Duplication Heatmap

```
Duplication Heatmap:
================================================================================
Legend: ░=Low(1-10%) ▒=Med(10-25%) ▓=High(25-50%) █=Critical(50%+)

█ /home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts 3733.3% (560/15 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts 1617.7% (275/17 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts 1473.8% (899/61 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/routes/asset.ts 1068.4% (203/19 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/routes/hub.ts  625.0% (75/12 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/types/hub.types.ts  289.5% (55/19 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/hub.test.ts  272.4% (267/98 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts  234.8% (1296/552 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts  216.2% (573/265 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts  209.3% (896/428 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts  201.8% (1384/686 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-password.service.ts  194.9% (115/59 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts  183.0% (701/383 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts  172.4% (1383/802 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts  156.4% (122/78 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-registration.service.ts  155.6% (126/81 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts  154.7% (874/565 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/types/property.types.ts  153.6% (169/110 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-e2e.test.ts  145.5% (419/288 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/asset-hvac-enrichment.test.ts  141.9% (376/265 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth.service.ts  139.5% (60/43 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts  134.4% (922/686 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/middleware/rateLimiter.ts  125.0% (50/40 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts  121.5% (470/387 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/email/email-templates.ts  107.1% (135/126 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts  106.6% (963/903 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/hub.service.ts   94.0% (125/133 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts   93.6% (206/220 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts   87.2% (308/353 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/utils/logger.ts   82.7% (43/52 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/profile/profile-updates.service.ts   81.5% (141/173 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts   81.2% (207/255 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/constants/asset.constants.ts   76.1% (89/117 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-session.service.ts   70.1% (103/147 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts   70.0% (56/80 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/profile/profile-login.service.ts   69.9% (51/73 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts   69.5% (153/220 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/profile.controller.ts   69.5% (137/197 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/schemas/profile.schemas.ts   67.7% (42/62 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/config/assetTypeOntologyMap.ts   65.7% (115/175 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/asset-count-sync.test.ts   64.2% (330/514 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/middleware/authenticate.ts   63.6% (35/55 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/schemas/asset.schemas.ts   63.0% (300/476 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/services/email/email.service.ts   57.1% (101/177 LOC)
█ /home/mark/applications/sentient-homes/MVP-backend/src/schemas/hub.schemas.ts   54.5% (12/22 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/performance/property.perf.test.ts   47.5% (159/335 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/ontology.controller.ts   47.4% (36/76 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/services/asset/asset.service.ts   45.4% (303/668 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/geocoding.service.test.ts   43.8% (117/267 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/services/property/geocoding.service.ts   40.0% (48/120 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/services/asset/product.service.ts   36.1% (88/244 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/auth-e2e.test.ts   35.8% (196/547 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts   35.8% (53/148 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/utils/retry.ts   32.8% (21/64 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/email.service.test.ts   32.3% (70/217 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property-data.service.test.ts   31.9% (207/650 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/health.test.ts   31.0% (18/58 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/csv-loader.service.test.ts   30.6% (77/252 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/rateLimiter.test.ts   29.7% (38/128 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/auth.service.test.ts   29.6% (211/714 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/src/services/property/address-suggestion.service.ts   28.2% (42/149 LOC)
▓ /home/mark/applications/sentient-homes/MVP-backend/scripts/fix-property-asset-counts.ts   28.2% (82/291 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/auth.routes.test.ts   24.0% (132/551 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/controllers/hub.controller.ts   22.4% (11/49 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/services/profile/profile.service.ts   22.1% (27/122 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.schemas.test.ts   21.8% (70/321 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/hvac-data.service.test.ts   21.6% (57/264 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/asset-workflow.test.ts   21.3% (50/235 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/services/asset/hvac-data.service.ts   20.0% (32/160 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/hub.service.test.ts   19.7% (57/290 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/profile.test.ts   19.2% (50/261 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/scripts/scraping/ahri-scraper.ts   18.0% (42/233 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/schemas/property.schemas.ts   17.3% (37/214 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/services/health.service.ts   16.2% (12/74 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/scripts/migrate-assets-to-types.ts   16.1% (39/243 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/utils/errorMapper.ts   15.6% (5/32 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/scripts/verify-asset-property-integrity.ts   15.4% (36/233 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/services/asset/csv-loader.service.ts   15.4% (33/214 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/asset.service.test.ts   13.1% (87/663 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/errorMapper.test.ts   12.9% (15/116 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/health.enhanced.test.ts   12.2% (20/164 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property-query.service.test.ts   10.8% (15/139 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/src/types/auth.types.ts   10.7% (6/56 LOC)
▒ /home/mark/applications/sentient-homes/MVP-backend/scripts/fix-asset-properties.ts   10.3% (10/97 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/src/services/property/property-data.service.ts    9.9% (17/172 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/schemas/property.schemas.test.ts    8.6% (50/580 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/retry.test.ts    8.2% (24/292 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/integration/ontology.routes.test.ts    7.6% (5/66 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/logger.test.ts    6.7% (10/150 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/types/auth.types.test.ts    6.6% (10/151 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/address-suggestion.service.test.ts    4.3% (25/580 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/src/types/water-heater.types.ts    3.3% (12/366 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/schemas/asset.schemas.test.ts    2.3% (15/656 LOC)
░ /home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/ontology.service.test.ts    2.3% (5/219 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/jest.config.js    0.0% (0/14 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/index.ts    0.0% (0/22 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/app.ts    0.0% (0/46 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/profile/index.ts    0.0% (0/6 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/email/email-validator.ts    0.0% (0/19 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/email/index.ts    0.0% (0/3 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/auth/index.ts    0.0% (0/4 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/property/index.ts    0.0% (0/6 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/services/property/property-query.service.ts    0.0% (0/36 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/config/env.ts    0.0% (0/38 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/middleware/errorHandler.ts    0.0% (0/35 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/routes/ontology.ts    0.0% (0/13 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/routes/health.ts    0.0% (0/36 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/routes/product-asset.ts    0.0% (0/14 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/routes/index.ts    0.0% (0/19 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/schemas/water-heater.schemas.ts    0.0% (0/370 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/schemas/auth.schemas.ts    0.0% (0/28 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/types/email.types.ts    0.0% (0/57 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/dynamodbErrorMapper.ts    0.0% (0/102 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/swagger.ts    0.0% (0/27 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/jwt.ts    0.0% (0/29 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/validationHelper.ts    0.0% (0/13 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/cognito.ts    0.0% (0/18 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/src/utils/dynamodb.ts    0.0% (0/16 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/scripts/check-properties-debug.ts    0.0% (0/42 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/scripts/generate-openapi.ts    0.0% (0/17 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/performance/auth.perf.test.ts    0.0% (0/48 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/unit/env.test.ts    0.0% (0/21 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/unit/schemas/hub.schemas.test.ts    0.0% (0/123 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/cognito.test.ts    0.0% (0/46 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/jwt.test.ts    0.0% (0/75 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/unit/utils/dynamodbErrorMapper.test.ts    0.0% (0/253 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/integration/swagger.test.ts    0.0% (0/26 LOC)
  /home/mark/applications/sentient-homes/MVP-backend/tests/integration/cors-security.test.ts    0.0% (0/67 LOC)
```

## 📋 Duplicate Blocks

Found **921 duplicate blocks** across the codebase.
Showing top **50** by severity.

### 🔴 Duplicate #1/50 - EXACT

**Type:** exact
**Instances:** 32
**Similarity:** 100.0%
**Hash:** `d41d8cd98f00...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-password.service.ts:L22-26` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-registration.service.ts:L24-28` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property-data.service.ts:L1-5` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/address-suggestion.service.ts:L113-117` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/address-suggestion.service.ts:L153-157` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts:L110-119` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts:L33-37` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts:L73-77` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts:L230-234` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts:L270-274` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/config/assetTypeOntologyMap.ts:L210-219` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L1-10` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/asset.ts:L158-162` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/property.schemas.ts:L139-143` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/hub.types.ts:L1-10` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts:L357-361` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts:L364-368` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts:L375-379` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts:L382-386` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/property.types.ts:L1-11` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L1-15` (15 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errorMapper.ts:L7-11` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/logger.ts:L4-13` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L115-119` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L374-378` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/scripts/scraping/ahri-scraper.ts:L1-20` (20 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/performance/property.perf.test.ts:L437-456` (20 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/asset-count-sync.test.ts:L1-10` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/ontology.service.test.ts:L1-5` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property-query.service.test.ts:L1-5` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/csv-loader.service.test.ts:L1-5` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/ontology.routes.test.ts:L1-5` (5 lines)

**Code Sample:**
```python
  /**
   * Calculate SECRET_HASH for Cognito requests when client has a secret
   * @param username - Username or email
   * @returns SECRET_HASH or undefined if no client secret configured
   */
```

---

### 🔴 Duplicate #2/50 - EXACT

**Type:** exact
**Instances:** 24
**Similarity:** 100.0%
**Hash:** `cbb184dd8e05...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L168-178` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/health.service.ts:L77-82` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth.service.ts:L23-33` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth.service.ts:L104-114` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/address-suggestion.service.ts:L41-46` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts:L369-374` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts:L255-265` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts:L323-333` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/geocoding.service.ts:L140-150` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/csv-loader.service.ts:L198-203` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/csv-loader.service.ts:L358-367` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/ontology.service.ts:L278-287` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/product.service.ts:L369-374` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/asset.types.ts:L738-743` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L80-85` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L206-215` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L223-228` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L234-239` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/profile.types.ts:L265-274` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/water-heater.types.ts:L324-329` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/retry.ts:L150-170` (21 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L157-167` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L269-283` (15 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/scripts/scraping/ahri-scraper.ts:L184-189` (6 lines)

**Code Sample:**
```python
  }
  /**
   * GET /properties OR GET /hubs/:hubId/properties
   * List all properties for a hub
   *
   * If hubId is provided in params, verifies it belongs to the user.
   * If no hubId in params, automatically uses the user's hub.
   *
   * Authorization: Hub must belong to requesting user
   */
```

---

### 🔴 Duplicate #3/50 - EXACT

**Type:** exact
**Instances:** 20
**Similarity:** 100.0%
**Hash:** `8b7e78408498...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L107-111` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L133-137` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L174-178` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L192-196` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L56-60` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L108-112` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L249-253` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L288-292` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L383-387` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L571-575` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L657-661` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/asset.ts:L189-193` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/hub.ts:L36-40` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L148-152` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L385-389` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L464-468` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L474-478` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L484-488` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L600-604` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L610-614` (5 lines)

**Code Sample:**
```python
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
```

---

### 🔴 Duplicate #4/50 - EXACT

**Type:** exact
**Instances:** 16
**Similarity:** 100.0%
**Hash:** `649360527276...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L89-93` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L99-103` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L109-113` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L188-192` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L198-202` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L208-212` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L267-271` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L277-281` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L287-291` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L332-336` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L342-346` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L352-356` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L411-415` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L421-425` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L533-537` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L543-547` (5 lines)

**Code Sample:**
```python
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
```

---

### 🔴 Duplicate #5/50 - EXACT

**Type:** exact
**Instances:** 13
**Similarity:** 100.0%
**Hash:** `46b12772972e...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L98-102` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L385-389` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L443-447` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L69-73` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L93-97` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L153-157` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L172-176` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L189-193` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L206-210` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L223-227` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L240-244` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L115-119` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L142-146` (5 lines)

**Code Sample:**
```python
      await authController.register(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
```

---

### 🔴 Duplicate #6/50 - EXACT

**Type:** exact
**Instances:** 12
**Similarity:** 100.0%
**Hash:** `852d09579aaf...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L510-514` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L672-676` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L38-42` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L253-257` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L199-203` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L456-460` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L616-620` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L869-873` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/hub.ts:L95-99` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L47-51` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L241-245` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L566-570` (5 lines)

**Code Sample:**
```python
   *           application/json:
   *             schema:
   *               type: object
   *               properties:
   *                 success:
```

---

### 🔴 Duplicate #7/50 - EXACT

**Type:** exact
**Instances:** 12
**Similarity:** 100.0%
**Hash:** `6f0ef4609828...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L135-139` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L194-198` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L58-62` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L110-114` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L251-255` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L290-294` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L385-389` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L573-577` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L659-663` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/hub.ts:L38-42` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L150-154` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L387-391` (5 lines)

**Code Sample:**
```python
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
```

---

### 🔴 Duplicate #8/50 - EXACT

**Type:** exact
**Instances:** 11
**Similarity:** 100.0%
**Hash:** `91fa35eb91db...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L492-496` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L624-628` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L105-109` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L172-176` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L147-151` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L337-341` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L126-130` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L225-229` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L306-310` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L369-373` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L438-442` (5 lines)

**Code Sample:**
```python
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
```

---

### 🔴 Duplicate #9/50 - EXACT

**Type:** exact
**Instances:** 11
**Similarity:** 100.0%
**Hash:** `c4f777731c33...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/schemas/property.schemas.test.ts:L356-360` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L177-181` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L457-461` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L474-478` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L530-534` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L582-586` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L736-740` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L813-817` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L885-889` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L919-923` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1071-1075` (5 lines)

**Code Sample:**
```python
            city: 'San Francisco',
            state: 'CA',
            zipCode: '94102',
            country: 'US',
          },
```

---

### 🔴 Duplicate #10/50 - EXACT

**Type:** exact
**Instances:** 10
**Similarity:** 100.0%
**Hash:** `f09b506ec316...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L71-76` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L112-117` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L131-136` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L148-153` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L165-170` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L182-187` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L199-204` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L112-117` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L574-579` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L627-632` (6 lines)

**Code Sample:**
```python
      };
      await authController.register(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
```

---

### 🔴 Duplicate #11/50 - EXACT

**Type:** exact
**Instances:** 10
**Similarity:** 100.0%
**Hash:** `3c15d70577d3...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L322-326` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L343-347` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L364-368` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L362-366` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L384-388` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L399-403` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L417-421` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L439-443` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L1031-1035` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L1075-1079` (5 lines)

**Code Sample:**
```python
      await authController.getMe(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
```

---

### 🔴 Duplicate #12/50 - EXACT

**Type:** exact
**Instances:** 10
**Similarity:** 100.0%
**Hash:** `625087822702...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L175-179` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L455-459` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L472-476` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L528-532` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L580-584` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L734-738` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L811-815` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L883-887` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L917-921` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1069-1073` (5 lines)

**Code Sample:**
```python
    address: {
      street: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      zipCode: '94102',
```

---

### 🔴 Duplicate #13/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `b6f949be01d5...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L67-73` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L257-263` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L303-309` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L349-355` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L395-401` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/profile.controller.ts:L210-215` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/profile.controller.ts:L287-292` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L601-606` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L759-764` (6 lines)

**Code Sample:**
```python
        duration: Date.now() - startTime,
      });
      if (handleValidationError(error, next)) {
        return;
      }
```

---

### 🔴 Duplicate #14/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `c75eee2e8e0a...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L71-77` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L261-267` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L307-313` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L353-359` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/auth.controller.ts:L399-405` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/profile.controller.ts:L213-218` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/profile.controller.ts:L290-295` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L604-609` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L762-767` (6 lines)

**Code Sample:**
```python
      if (handleValidationError(error, next)) {
        return;
      }
      next(error);
    }
```

---

### 🔴 Duplicate #15/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `8d9ce3981992...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L512-516` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L674-678` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L40-44` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L201-205` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L458-462` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L618-622` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L49-53` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L243-247` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L568-572` (5 lines)

**Code Sample:**
```python
   *               type: object
   *               properties:
   *                 success:
   *                   type: boolean
   *                   example: true
```

---

### 🔴 Duplicate #16/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `44a78ec6b617...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L221-225` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L253-257` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L463-467` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L266-270` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L289-293` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L321-325` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L327-331` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L349-353` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L367-371` (5 lines)

**Code Sample:**
```python
      await authController.login(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
```

---

### 🔴 Duplicate #17/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `7f6f203cb027...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L127-131` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L148-152` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L171-175` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L312-316` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L362-366` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L385-389` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L416-420` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L472-476` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L499-503` (5 lines)

**Code Sample:**
```python
      await authenticate(
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
```

---

### 🔴 Duplicate #18/50 - EXACT

**Type:** exact
**Instances:** 9
**Similarity:** 100.0%
**Hash:** `0c556d86d78e...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L293-297` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L546-550` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L671-675` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L709-713` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L757-761` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L787-791` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L833-837` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L968-972` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1099-1103` (5 lines)

**Code Sample:**
```python
        .send({
          address: {
            street: '123 Main St',
            city: 'San Francisco',
            state: 'CA',
```

---

### 🔴 Duplicate #19/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `fc7556b633c4...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts:L237-241` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts:L404-408` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts:L47-51` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts:L89-93` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts:L178-182` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/ontology.controller.ts:L119-123` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/ontology.controller.ts:L168-172` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/middleware/authenticate.ts:L22-26` (5 lines)

**Code Sample:**
```python
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
```

---

### 🔴 Duplicate #20/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `c87ef7e56ef4...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L514-518` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L676-680` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L42-46` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L203-207` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L460-464` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L51-55` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L245-249` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L570-574` (5 lines)

**Code Sample:**
```python
   *                 success:
   *                   type: boolean
   *                   example: true
   *                 data:
   *                   type: object
```

---

### 🔴 Duplicate #21/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `c8f741d12f48...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L510-519` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L672-681` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L38-47` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L199-208` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L456-465` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L47-56` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L241-250` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L566-575` (10 lines)

**Code Sample:**
```python
   *           application/json:
   *             schema:
   *               type: object
   *               properties:
   *                 success:
   *                   type: boolean
   *                   example: true
   *                 data:
   *                   type: object
   *                   properties:
```

---

### 🔴 Duplicate #22/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `84dd2919a62d...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/profile/profile-updates.service.ts:L207-227` (21 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/email/email.service.ts:L95-105` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth-registration.service.ts:L96-106` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/property/property.service.ts:L188-198` (11 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/asset.service.ts:L756-761` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/csv-loader.service.ts:L104-109` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/csv-loader.service.ts:L248-253` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/scripts/scraping/ahri-scraper.ts:L165-170` (6 lines)

**Code Sample:**
```python
    }
  }
  /**
   * Updates feature flags (admin only operation).
   * Merges provided flags with existing flags.
   *
   * @param userId - The user ID
   * @param featureFlags - Feature flags to set or update
   * @param currentVersion - Current profile version for optimistic locking
   * @returns Promise resolving to updated Profile
   *
   * @example
   * ```typescript
   * const updated = await updateService.updateFeatureFlags(
   *   'abc-123',
... (truncated)
```

---

### 🔴 Duplicate #23/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `c0c97e22db50...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/asset.schemas.ts:L226-235` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/asset.schemas.ts:L652-657` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/asset.schemas.ts:L688-697` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/asset.schemas.ts:L822-827` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/profile.schemas.ts:L41-46` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/property.schemas.ts:L57-62` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/property.schemas.ts:L107-112` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/schemas/property.schemas.ts:L191-200` (10 lines)

**Code Sample:**
```python
});
/**
 * Product reference schema (for asset creation)
 * Validates productId exists
 */
```

---

### 🔴 Duplicate #24/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `199487473f43...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L74-79` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L115-120` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L134-139` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L151-156` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L168-173` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L185-190` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling-edge-cases.test.ts:L202-207` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L115-120` (6 lines)

**Code Sample:**
```python
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      expect(authService.register).not.toHaveBeenCalled();
```

---

### 🔴 Duplicate #25/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `59f0cf52d852...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L71-76` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L155-160` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L174-179` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L191-196` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L208-213` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L225-230` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L242-247` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L117-123` (7 lines)

**Code Sample:**
```python
          mockResponse as Response,
          mockNext
        );
        expect(authService.register).not.toHaveBeenCalled();
        expect(mockNext).toHaveBeenCalled();
```

---

### 🔴 Duplicate #26/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `e0afa2646bfc...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L295-299` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L548-552` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L711-715` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L759-763` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L789-793` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L835-839` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L970-974` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1101-1105` (5 lines)

**Code Sample:**
```python
            street: '123 Main St',
            city: 'San Francisco',
            state: 'CA',
            zipCode: '94102',
            country: 'US',
```

---

### 🔴 Duplicate #27/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `4293f880e396...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L451-455` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L649-653` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L687-691` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L807-811` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L879-883` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L913-917` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1009-1013` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1065-1069` (5 lines)

**Code Sample:**
```python
        const response = await request(app)
          .post(`${env.API_PREFIX}/properties/address/lookup`)
          .set('Authorization', `Bearer ${mockAccessToken}`)
          .send({
            address: {
```

---

### 🔴 Duplicate #28/50 - EXACT

**Type:** exact
**Instances:** 8
**Similarity:** 100.0%
**Hash:** `1097098c1435...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L453-457` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L470-474` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L651-655` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L732-736` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L809-813` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L881-885` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L915-919` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-onboarding-e2e.test.ts:L1067-1071` (5 lines)

**Code Sample:**
```python
          .set('Authorization', `Bearer ${mockAccessToken}`)
          .send({
            address: {
              street: '123 Main St',
              city: 'San Francisco',
```

---

### 🔴 Duplicate #29/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `66f20ceb47fc...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/email/email.service.ts:L250-255` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/auth/auth.service.ts:L117-122` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/services/asset/hvac-data.service.ts:L245-250` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/types/auth.types.ts:L84-89` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L174-188` (15 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L290-304` (15 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/utils/errors/asset.errors.ts:L311-325` (15 lines)

**Code Sample:**
```python
  }
}
/**
 * Singleton instance of EmailService
 */
```

---

### 🔴 Duplicate #30/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `dcd53b2e4e9a...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/profile.ts:L235-239` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L40-44` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L537-541` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L809-813` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/asset.ts:L226-230` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L19-23` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L503-507` (5 lines)

**Code Sample:**
```python
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
```

---

### 🔴 Duplicate #31/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `e6068816ee6d...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L60-64` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L292-296` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L387-391` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L575-579` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L661-665` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L152-156` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L389-393` (5 lines)

**Code Sample:**
```python
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
```

---

### 🔴 Duplicate #32/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `2cfcba778cb4...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L56-65` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L288-297` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L383-392` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L571-580` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/property.ts:L657-666` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L148-157` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L385-394` (10 lines)

**Code Sample:**
```python
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
```

---

### 🔴 Duplicate #33/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `ed5670fbae05...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L45-49` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L117-121` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L178-182` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L333-337` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L383-387` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L597-601` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L768-772` (5 lines)

**Code Sample:**
```python
          street: "123 Main St",
          city: "Portland",
          state: "OR",
          zipCode: "97201",
          country: "US",
```

---

### 🔴 Duplicate #34/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `c36e691b1ed8...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L47-51` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L119-123` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L180-184` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L335-339` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L385-389` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L599-603` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L770-774` (5 lines)

**Code Sample:**
```python
          state: "OR",
          zipCode: "97201",
          country: "US",
        },
        yearBuilt: 2020,
```

---

### 🔴 Duplicate #35/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `7341e1d0e2e4...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L49-53` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L121-125` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L182-186` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L337-341` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L387-391` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L601-605` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L772-776` (5 lines)

**Code Sample:**
```python
          country: "US",
        },
        yearBuilt: 2020,
        squareFeet: 2000,
        homeType: HomeType.SINGLE_FAMILY,
```

---

### 🔴 Duplicate #36/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `f9d71810d8f1...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L38-42` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L102-106` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L307-311` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L339-343` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L371-375` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L407-411` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/profile.service.test.ts:L588-592` (5 lines)

**Code Sample:**
```python
        loginHistory: [],
        onboardingCompleted: false,
        onboardingProgress: 0,
        onboardingCurrentStep: null,
        onboardingCompletedSteps: [],
```

---

### 🔴 Duplicate #37/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `dc305e372750...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L106-111` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L194-199` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L215-220` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L236-241` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L260-265` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L288-293` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L338-343` (6 lines)

**Code Sample:**
```python
        mockRequest as Request,
        mockResponse as Response,
        mockNext
      );
      expect(mockStatus).toHaveBeenCalledWith(401);
```

---

### 🔴 Duplicate #38/50 - EXACT

**Type:** exact
**Instances:** 7
**Similarity:** 100.0%
**Hash:** `be8019ece9d2...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L108-113` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L196-201` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L217-222` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L238-243` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L262-267` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L290-295` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L340-345` (6 lines)

**Code Sample:**
```python
        mockNext
      );
      expect(mockStatus).toHaveBeenCalledWith(401);
      expect(mockJson).toHaveBeenCalledWith({
        success: false,
```

---

### 🔴 Duplicate #39/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `933d75e81cb4...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts:L264-268` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts:L327-331` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/asset.controller.ts:L379-383` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts:L113-117` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/product.controller.ts:L157-161` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/ontology.controller.ts:L50-54` (5 lines)

**Code Sample:**
```python
    });
  } catch (error) {
    next(error);
  }
}
```

---

### 🔴 Duplicate #40/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `afa5d1828968...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L40-45` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L187-192` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L260-265` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L411-416` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L567-572` (6 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/controllers/property.controller.ts:L727-732` (6 lines)

**Code Sample:**
```python
      const userId = req.user?.userId;
      if (!userId) {
        const error = new Error('Authentication required') as ApiError;
        error.statusCode = 401;
        throw error;
```

---

### 🔴 Duplicate #41/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `829eda463ba2...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/middleware/authenticate.ts:L46-50` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/middleware/authenticate.ts:L61-65` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L201-205` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L222-226` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L243-247` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/middleware/authenticate.test.ts:L267-271` (5 lines)

**Code Sample:**
```python
        success: false,
        error: {
          message: 'Invalid token format',
        },
      });
```

---

### 🔴 Duplicate #42/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `401c05a02fef...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L107-111` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L206-210` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L285-289` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L350-354` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L419-423` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L541-545` (5 lines)

**Code Sample:**
```python
 *         description: Too many requests - rate limit exceeded
 *         content:
 *           application/json:
 *             schema:
 *               type: object
```

---

### 🔴 Duplicate #43/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `45f00e49b36e...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L111-115` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L210-214` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L289-293` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L354-358` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L423-427` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L545-549` (5 lines)

**Code Sample:**
```python
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: Too many requests, please try again later
```

---

### 🔴 Duplicate #44/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `d91cacf9414d...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L107-116` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L206-215` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L285-294` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L350-359` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L419-428` (10 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/src/routes/auth.ts:L541-550` (10 lines)

**Code Sample:**
```python
 *         description: Too many requests - rate limit exceeded
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: Too many requests, please try again later
 */
```

---

### 🔴 Duplicate #45/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `ca40fa6555ee...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L494-500` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L769-775` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L789-795` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L809-815` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L829-835` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L871-877` (7 lines)

**Code Sample:**
```python
          mockRequest as Request,
          mockResponse as Response,
          mockNext
        );
        expect(authService.verifyEmail).not.toHaveBeenCalled();
```

---

### 🔴 Duplicate #46/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `ab127aae381c...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/error-handling.test.ts:L496-502` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L771-777` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L791-797` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L811-817` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L831-837` (7 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L873-879` (7 lines)

**Code Sample:**
```python
          mockNext
        );
        expect(authService.verifyEmail).not.toHaveBeenCalled();
        expect(mockNext).toHaveBeenCalled();
        const error = (mockNext as jest.Mock).mock.calls[0][0];
```

---

### 🔴 Duplicate #47/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `e605ba8e9fc1...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/asset-count-sync.test.ts:L81-85` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-e2e.test.ts:L73-77` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-e2e.test.ts:L213-217` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L79-83` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L162-166` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L208-212` (5 lines)

**Code Sample:**
```python
    address: {
      street: '123 Main St',
      city: 'Portland',
      state: 'OR',
      zipCode: '97201',
```

---

### 🔴 Duplicate #48/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `14b72c758ecf...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/asset-count-sync.test.ts:L83-87` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-e2e.test.ts:L75-79` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property-e2e.test.ts:L215-219` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L81-85` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L164-168` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/integration/property.test.ts:L210-214` (5 lines)

**Code Sample:**
```python
      city: 'Portland',
      state: 'OR',
      zipCode: '97201',
      country: 'US',
    },
```

---

### 🔴 Duplicate #49/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `16c13e2a384c...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L515-519` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L535-539` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L609-613` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L777-781` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L797-801` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/controllers/auth.controller.test.ts:L817-821` (5 lines)

**Code Sample:**
```python
      const error = (mockNext as jest.Mock).mock.calls[0][0];
      expect(error).toBeInstanceOf(Error);
      expect(error.message).toContain('Validation failed');
      expect(error.statusCode).toBe(400);
    });
```

---

### 🔴 Duplicate #50/50 - EXACT

**Type:** exact
**Instances:** 6
**Similarity:** 100.0%
**Hash:** `1a263d6545fb...`

**Found in:**
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L115-119` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L176-180` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L331-335` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L381-385` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L595-599` (5 lines)
- `/home/mark/applications/sentient-homes/MVP-backend/tests/unit/services/property.service.test.ts:L766-770` (5 lines)

**Code Sample:**
```python
        hubId: "hub-789",
        address: {
          street: "123 Main St",
          city: "Portland",
          state: "OR",
```

---

_... and 871 more duplicates not shown._

## 💡 Recommendations

### Priority Actions

### Best Practices Going Forward

1. **Extract Common Utilities:** Create shared functions for repeated logic
2. **Use Design Patterns:** Apply appropriate patterns (Factory, Strategy, Template Method)
3. **Code Reviews:** Flag duplication during reviews
4. **Automated Detection:** Run this analysis regularly (CI/CD integration)
5. **Documentation:** Document shared utilities and patterns

---

*Report generated by Code Duplication Analysis Skill*
