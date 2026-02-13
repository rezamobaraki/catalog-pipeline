# AWS Product Import Pipeline - Design Explanation

## Architecture Overview

This architecture implements an asynchronous, scalable, and resilient product import pipeline that handles large JSON
files containing product information.

---

## Design Decisions & Justifications

### 1. **Job Creation & File Upload Pattern**

**Decision:** Use a two-step process: job creation endpoint + pre-signed S3 URL upload

**Why:**

- **Avoids API Gateway/Lambda payload limits** (6MB for Lambda, 10MB for API Gateway)
- **Decouples job tracking from file transfer** - clients get immediate response with job_id
- **Pre-signed URLs** allow direct S3 upload, reducing load on API servers
- **Idempotency** enabled via job_id + checksum tracking in DynamoDB

---

### 2. **Event-Driven Orchestration**

**Decision:** S3 Events → EventBridge → Step Functions

**Why:**

- **EventBridge provides flexible routing** and filtering capabilities
- **Step Functions** offers visual workflow, built-in retry/catch per step, and execution history
- **Retry/Catch blocks** per step ensure resilience without custom retry logic
- **State machine pattern** makes the pipeline easy to debug and extend

---

### 3. **Processing Pipeline Steps**

| Step                         | Service                   | Justification                                                                  |
|------------------------------|---------------------------|--------------------------------------------------------------------------------|
| **Validation**               | Lambda                    | Stateless, fast JSON schema validation fits Lambda's model                     |
| **Antivirus**                | ECS Fargate               | ClamAV requires container (memory/libraries), runs for variable duration       |
| **Metadata Standardization** | Lambda                    | Rule-based transformation, quick execution                                     |
| **Media Processing**         | Lambda/ECS + MediaConvert | Lambda for small images; ECS/Batch for heavy workloads; MediaConvert for video |
| **Persistence**              | Lambda + RDS Proxy        | Batch writes via RDS Proxy to prevent connection exhaustion                    |
| **Search Indexing**          | Lambda + OpenSearch       | Bulk indexing for efficient search capabilities                                |

---

### 4. **Storage Strategy**

**S3 Bucket Prefixes:**

```
product-import-bucket/
├── raw/           # Original uploaded files (lifecycle: delete after 30 days)
├── processed/     # Normalized/standardized data
├── derivatives/   # Generated media (multiple resolutions)
└── quarantine/    # Infected/failed files for investigation
```

**Why separate prefixes:**

- **Lifecycle policies** can be applied per prefix
- **IAM permissions** can be scoped to specific prefixes
- **Clear separation** of processing stages

---

### 5. **Database Choices**

| Database              | Purpose                       | Why                                                                         |
|-----------------------|-------------------------------|-----------------------------------------------------------------------------|
| **DynamoDB**          | Job tracking & metadata rules | Fast key-value lookups, no connection limits, serverless scaling            |
| **Aurora PostgreSQL** | Product data persistence      | Relational integrity, complex queries, ACID transactions                    |
| **OpenSearch**        | Search indexing               | High-performance full-text search, faceted filtering by color/size/material |

**RDS Proxy:** Prevents Lambda connection storms by pooling connections.

---

### 6. **Error Handling & Notifications**

**Failure Path:**

1. Any step failure triggers Step Functions catch block
2. Error handler Lambda captures error details
3. Job status updated in DynamoDB (state: FAILED, error details)
4. SNS publishes notification
5. SES sends email to uploader with job_id and error summary

**Special Case - Antivirus:**

- Infected files moved to `quarantine/` prefix
- File access restricted via IAM
- Alert includes malware type detected

---

### 7. **Security Measures**

| Measure                     | Implementation                              |
|-----------------------------|---------------------------------------------|
| **Encryption at rest**      | SSE-KMS for all S3 buckets                  |
| **Encryption in transit**   | HTTPS enforced                              |
| **Least privilege**         | Separate IAM roles per Lambda/ECS task      |
| **Pre-signed URL security** | Short expiry (15 min), prefix-scoped        |
| **Network isolation**       | VPC endpoints for S3, OpenSearch (optional) |

---

### 8. **Observability**

| Tool                       | Purpose                                             |
|----------------------------|-----------------------------------------------------|
| **CloudWatch Logs**        | All Lambda/ECS logs centralized                     |
| **CloudWatch Metrics**     | Custom metrics for job duration, success rate       |
| **CloudWatch Alarms**      | Alert on high failure rate, long-running executions |
| **X-Ray**                  | Distributed tracing across services                 |
| **Step Functions Console** | Visual execution history and debugging              |

---

### 9. **Scalability Considerations**

- **Lambda concurrency:** Auto-scales to handle burst uploads
- **ECS Fargate:** Scales based on pending Step Functions tasks
- **Aurora Serverless v2:** Optional for variable workloads
- **OpenSearch:** Sized based on data volume and query patterns

---

### 10. **Cost Optimization**

- **S3 Lifecycle Policies:** Auto-delete raw files after retention period
- **Lambda:** Pay-per-execution, right-size memory allocation
- **Step Functions Express:** For high-volume, short-duration workflows (optional)
- **Reserved Capacity:** For predictable OpenSearch/Aurora workloads

---

## Flow Summary

```
1. Client → POST /jobs → API Gateway → Lambda
2. Lambda creates job in DynamoDB, returns job_id + pre-signed URL
3. Client uploads JSON to S3 (raw/)
4. S3 Event → EventBridge → Step Functions
5. Pipeline: Validate → Antivirus → Normalize → Media → Persist → Index
6. Success: Update DynamoDB, notify via SNS/SES
7. Failure: Quarantine (if virus), error handler, notify uploader
```

---

## Alternative Approaches Considered

| Alternative                   | Why Not Chosen                                |
|-------------------------------|-----------------------------------------------|
| SQS instead of Step Functions | Less visibility, harder error handling        |
| Lambda for antivirus          | ClamAV requires container, memory limits      |
| Elasticsearch                 | OpenSearch is AWS-managed, same functionality |
| DynamoDB for products         | Lacks complex query capabilities needed       |

---

## Future Enhancements

1. **DLQ (Dead Letter Queue):** For failed messages requiring manual review
2. **WAF:** On API Gateway for additional protection
3. **Batch Processing:** AWS Batch for very large media files
4. **Multi-region:** For disaster recovery requirements

