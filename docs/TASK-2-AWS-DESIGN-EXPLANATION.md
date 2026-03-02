# AWS Product Import Pipeline - Design Justification

## Architecture Overview

Serverless, event-driven pipeline: **S3 → EventBridge → Step Functions → Lambda/ECS → Aurora/OpenSearch**

---

## Design Decisions

| Decision                         | Justification                                                          |
|----------------------------------|------------------------------------------------------------------------|
| **Pre-signed S3 URL**            | Bypasses API Gateway 10MB limit; client uploads directly to S3         |
| **EventBridge + Step Functions** | Visual workflow, built-in retry/catch, execution history for debugging |
| **Lambda for processing**        | Stateless, auto-scaling, pay-per-execution                             |
| **ECS Fargate for Antivirus**    | ClamAV needs container; exceeds Lambda memory/time limits              |
| **RDS Proxy**                    | Prevents Lambda connection storms to Aurora                            |
| **DynamoDB for job status**      | Fast key-value lookups, no connection limits, serverless               |
| **Aurora PostgreSQL**            | ACID compliance for product data, complex queries                      |
| **OpenSearch**                   | High-performance search by color, size, material (as required)         |
| **SNS + SES**                    | Notification to uploader on success/failure                            |
| **S3 quarantine/**               | Isolate infected files with restricted IAM access                      |

---

## Flow Summary

```
1. POST /jobs → Lambda creates job in DynamoDB, returns pre-signed URL
2. Client uploads JSON → S3 (raw/)
3. S3 Event → EventBridge → Step Functions
4. Pipeline: Validate → Antivirus → Normalize → Media → Persist → Index → Notify
5. Error: Catch block → quarantine (if virus) → notify uploader
```

---

## Key Requirements Addressed

| Requirement                   | Solution                                                   |
|-------------------------------|------------------------------------------------------------|
| Async processing              | Step Functions orchestrates Lambda/ECS                     |
| Validation                    | Lambda validates JSON schema                               |
| Antivirus                     | ECS Fargate runs ClamAV                                    |
| Metadata standardization      | Lambda normalizes colors (e.g., "Navy Blue" → "Dark Blue") |
| Media processing              | Lambda generates multiple resolutions                      |
| Persistence                   | Aurora PostgreSQL via RDS Proxy                            |
| Search by color/size/material | OpenSearch with keyword fields                             |
| Error notification            | SNS → SES emails uploader                                  |

---

## Medallion Architecture

The pipeline follows a **Medallion (Bronze → Silver → Gold)** layered data model. Each Step Functions step writes its output to a dedicated S3 prefix, creating an auditable trail:

| Layer      | Pipeline Step               | S3 Prefix               | Data State                                         |
|------------|-----------------------------|--------------------------|----------------------------------------------------|
| **Bronze** | Upload                      | `raw/{job_id}/`          | Original file as received from the client          |
| **Silver** | Validate → AV → Normalize  | `silver/{job_id}/`       | Validated, scanned, metadata-standardized product data |
| **Gold**   | Media → Persist → Index    | `gold/{job_id}/`         | Enriched data with generated media, persisted in Aurora & indexed in OpenSearch |

### Benefits

- **Traceability**: Every processing stage has its own snapshot in S3 — inspecting `silver/` reveals exactly what the normalizer produced before persistence.
- **Replayability**: If the Media or Persist step fails, re-run from the Silver layer without re-uploading or re-validating.
- **Debugging**: Step Functions execution history + S3 layer snapshots provide full lineage from raw upload to indexed product.

### Step-Level Intermediate Results

Each Lambda/ECS step writes a result artifact to S3 alongside updating the DynamoDB job record:

```
s3://product-pipeline/
├── raw/{job_id}/upload.json           # Bronze: original upload
├── silver/{job_id}/validated.json     # After schema validation
├── silver/{job_id}/scanned.json       # After antivirus (clean flag)
├── silver/{job_id}/normalized.json    # After metadata standardization
├── gold/{job_id}/media-manifest.json  # Generated media URLs
└── gold/{job_id}/persisted.json       # Final record IDs in Aurora
```

This allows operators to:
- Trace any product back to its raw input
- Compare before/after for each transformation step
- Replay individual steps during incident investigation
- Retain data lineage for compliance and auditing

