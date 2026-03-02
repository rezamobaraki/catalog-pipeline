# Kafka Product Import Pipeline - Design Justification

## Architecture Overview

Event-driven, cloud-agnostic pipeline: **MinIO → Kafka → Consumers → PostgreSQL/Elasticsearch**

---

## Design Decisions

| Decision                  | Justification                                                                                |
|---------------------------|----------------------------------------------------------------------------------------------|
| **Kafka + KRaft**         | High throughput, message replay, no Zookeeper dependency (KRaft is built-in since Kafka 3.5) |
| **Pre-signed MinIO URL**  | S3-compatible; client uploads directly, no API payload limits                                |
| **Kafka Consumer Groups** | Horizontal scaling, back-pressure handling, exactly-once semantics                           |
| **PgBouncer**             | Connection pooling prevents DB exhaustion from parallel consumers                            |
| **PostgreSQL**            | ACID compliance for product data, JSONB for flexible attributes                              |
| **Elasticsearch**         | High-performance search by color, size, material (as required)                               |
| **Redis**                 | Sub-ms job status lookups, TTL auto-expiry                                                   |
| **Debezium CDC**          | Real-time PostgreSQL → Kafka sync for ES updates                                             |
| **Celery or Airflow**     | Celery for real-time tasks; Airflow for complex DAGs/batch jobs                              |
| **Dead Letter Queue**     | Failed messages → DLQ → Error Handler → notify uploader                                      |

---

## Flow Summary

```
1. POST /jobs → FastAPI saves job in Redis, returns pre-signed URL
2. Client uploads JSON → MinIO (raw/)
3. MinIO Event → Kafka (product.uploads topic)
4. Pipeline: Validate → Antivirus → Normalize → Media → Persist → Index → Notify
5. Error: Retry with backoff → DLQ → Error Handler → notify uploader
```

---

## Key Requirements Addressed

| Requirement                   | Solution                                              |
|-------------------------------|-------------------------------------------------------|
| Async processing              | Kafka consumers process in parallel                   |
| Validation                    | Validator consumer checks JSON schema                 |
| Antivirus                     | ClamAV consumer scans files                           |
| Metadata standardization      | Normalizer consumer (e.g., "Navy Blue" → "Dark Blue") |
| Media processing              | Media consumer generates resolutions                  |
| Persistence                   | PostgreSQL via PgBouncer                              |
| Search by color/size/material | Elasticsearch with keyword fields                     |
| Error notification            | SMTP notification to uploader                         |

---

## Medallion Architecture

The pipeline follows a **Medallion (Bronze → Silver → Gold)** layered data model. Each Kafka consumer writes its output to a dedicated MinIO prefix, creating an auditable trail:

| Layer      | Pipeline Step                | MinIO Prefix             | Data State                                         |
|------------|------------------------------|--------------------------|----------------------------------------------------|
| **Bronze** | Upload                       | `raw/{job_id}/`          | Original file as received from the client          |
| **Silver** | Validate → AV → Normalize   | `silver/{job_id}/`       | Validated, scanned, metadata-standardized product data |
| **Gold**   | Media → Persist → Index     | `gold/{job_id}/`         | Enriched data with generated media, persisted in PostgreSQL & indexed in Elasticsearch |

### Benefits

- **Traceability**: Every consumer writes its output to both the next Kafka topic and a MinIO snapshot — inspecting `silver/` reveals exactly what the normalizer produced before persistence.
- **Replayability**: Kafka's message replay + MinIO layer snapshots allow re-processing from any stage without re-uploading.
- **Debugging**: Kafka consumer offsets + MinIO layer snapshots provide full lineage from raw upload to indexed product.

### Step-Level Intermediate Results

Each consumer writes a result artifact to MinIO alongside publishing to the next Kafka topic:

```
minio://product-pipeline/
├── raw/{job_id}/upload.json           # Bronze: original upload
├── silver/{job_id}/validated.json     # After schema validation
├── silver/{job_id}/scanned.json       # After antivirus (clean flag)
├── silver/{job_id}/normalized.json    # After metadata standardization
├── gold/{job_id}/media-manifest.json  # Generated media URLs
└── gold/{job_id}/persisted.json       # Final record IDs in PostgreSQL
```

This allows operators to:
- Trace any product back to its raw input
- Compare before/after for each transformation step
- Replay individual steps using Kafka consumer offsets or MinIO snapshots
- Retain data lineage for compliance and auditing

---

## Why Kafka vs AWS Native?

| Kafka             | AWS (Step Functions) |
|-------------------|----------------------|
| Cloud-agnostic ✅  | AWS lock-in          |
| Message replay ✅  | Limited replay       |
| Higher throughput | Lower throughput     |
| More ops overhead | Fully managed        |
