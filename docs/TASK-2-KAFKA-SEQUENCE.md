# Kafka Product Import Pipeline - Sequence Diagrams

## 1. API Layer & File Upload

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant NGINX
    participant FastAPI
    participant Redis
    participant MinIO as MinIO/S3

    Client->>NGINX: POST /jobs
    NGINX->>FastAPI: Forward request
    FastAPI->>Redis: Cache job status (PENDING)
    FastAPI->>MinIO: Generate pre-signed URL
    FastAPI-->>Client: Return job_id + upload URL
    Client->>MinIO: Upload JSON (raw/)
```

---

## 2. Event Streaming & Validation

```mermaid
sequenceDiagram
    autonumber
    participant MinIO as MinIO/S3
    participant Kafka
    participant Validator
    participant Antivirus as ClamAV

    MinIO->>Kafka: Bucket event (product.uploads)
    Kafka->>Validator: Consume message
    Validator->>MinIO: Read & validate file
    Validator->>Kafka: Publish (product.validated)
    Kafka->>Antivirus: Consume message
    Antivirus->>MinIO: Scan file for viruses
    
    alt Clean
        Antivirus->>Kafka: Publish (product.scanned)
    else Infected
        Antivirus->>Kafka: Publish to DLQ
    end
```

---

## 3. Processing (Normalize & Media)

```mermaid
sequenceDiagram
    autonumber
    participant Kafka
    participant Normalizer
    participant Media
    participant MinIO as MinIO/S3

    Kafka->>Normalizer: Consume (product.scanned)
    Normalizer->>MinIO: Transform metadata
    Normalizer->>Kafka: Publish (product.processed)
    
    Kafka->>Media: Consume (product.processed)
    Media->>MinIO: Store derivatives
    Media->>Kafka: Publish next
```

---

## 4. Persistence & Indexing

```mermaid
sequenceDiagram
    autonumber
    participant Kafka
    participant Persist
    participant Indexer
    participant PgBouncer
    participant PostgreSQL
    participant Elasticsearch

    Kafka->>Persist: Consume
    Persist->>PgBouncer: Connect
    PgBouncer->>PostgreSQL: Write product data
    PostgreSQL-->>Persist: Confirm
    Persist->>Kafka: Publish persisted
    
    Kafka->>Indexer: Consume
    Indexer->>Elasticsearch: Index for search
    Indexer->>Kafka: Publish indexed
```

---

## 5. Success Notification

```mermaid
sequenceDiagram
    autonumber
    participant Kafka
    participant Notifier
    participant Redis
    participant SMTP
    participant Client

    Kafka->>Notifier: Consume (indexed)
    Notifier->>Redis: Update job (COMPLETED)
    Notifier->>SMTP: Send success email
    SMTP-->>Client: ✓ Success notification
```

---

## 6. Error Handling

```mermaid
sequenceDiagram
    autonumber
    participant DLQ as Dead Letter Queue
    participant ErrorHandler
    participant Redis
    participant SMTP
    participant Client

    DLQ->>ErrorHandler: Consume failed message
    ErrorHandler->>Redis: Update job (FAILED)
    ErrorHandler->>SMTP: Send error notification
    SMTP-->>Client: ✗ Error notification
```

