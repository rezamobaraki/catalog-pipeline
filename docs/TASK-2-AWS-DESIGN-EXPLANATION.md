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
