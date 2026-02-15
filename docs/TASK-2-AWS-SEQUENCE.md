# AWS Product Import Pipeline - Sequence Diagrams

## 1. Upload Phase (Job Creation & File Upload)

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as API Gateway
    participant Lambda1 as Lambda (Create Job)
    participant DynamoDB
    participant S3

    Client->>API: POST /jobs
    API->>Lambda1: Invoke
    Lambda1->>DynamoDB: Save job (PENDING)
    Lambda1->>S3: Generate pre-signed URL
    Lambda1-->>Client: Return job_id + upload URL
    Client->>S3: Upload JSON (raw/)
```

---

## 2. Trigger Phase (Event-Driven Pipeline Start)

```mermaid
sequenceDiagram
    autonumber
    participant S3
    participant EventBridge
    participant StepFunctions as Step Functions

    S3->>EventBridge: S3 PutObject Event
    EventBridge->>StepFunctions: Start Pipeline Execution
```

---

## 3. Validation & Antivirus

```mermaid
sequenceDiagram
    autonumber
    participant StepFunctions as Step Functions
    participant LValidate as Lambda (Validate)
    participant ECS as ECS (Antivirus)
    participant S3

    StepFunctions->>LValidate: Invoke (Step 1)
    LValidate->>S3: Read raw file
    LValidate-->>StepFunctions: Validation result
    
    StepFunctions->>ECS: Invoke (Step 2)
    ECS->>S3: Scan file
    ECS-->>StepFunctions: File clean
```

---

## 4. Normalize & Media Processing

```mermaid
sequenceDiagram
    autonumber
    participant StepFunctions as Step Functions
    participant LNormalize as Lambda (Normalize)
    participant LMedia as Lambda (Media)
    participant S3

    StepFunctions->>LNormalize: Invoke (Step 3)
    LNormalize->>S3: Read/write metadata
    LNormalize-->>StepFunctions: Normalized data
    
    StepFunctions->>LMedia: Invoke (Step 4)
    LMedia->>S3: Store derivatives
    LMedia-->>StepFunctions: Media processed
```

---

## 5. Persistence & Indexing

```mermaid
sequenceDiagram
    autonumber
    participant StepFunctions as Step Functions
    participant LPersist as Lambda (Persist)
    participant LIndex as Lambda (Index)
    participant RDSProxy as RDS Proxy
    participant Aurora
    participant OpenSearch

    StepFunctions->>LPersist: Invoke (Step 5)
    LPersist->>RDSProxy: Connect
    RDSProxy->>Aurora: Write product data
    Aurora-->>LPersist: Confirm
    LPersist-->>StepFunctions: Data persisted
    
    StepFunctions->>LIndex: Invoke (Step 6)
    LIndex->>OpenSearch: Index for search
    LIndex-->>StepFunctions: Indexed
```

---

## 6. Success Notification

```mermaid
sequenceDiagram
    autonumber
    participant StepFunctions as Step Functions
    participant LNotify as Lambda (Notify)
    participant DynamoDB
    participant SNS
    participant SES
    participant Client

    StepFunctions->>LNotify: Invoke (Step 7)
    LNotify->>DynamoDB: Update job (COMPLETED)
    LNotify->>SNS: Publish success
    SNS->>SES: Send email
    SES-->>Client: ✓ Success notification
```

---

## 7. Error Handling

```mermaid
sequenceDiagram
    autonumber
    participant ECS as ECS (Antivirus)
    participant S3Quarantine as S3 (quarantine/)
    participant LError as Lambda (Error Handler)
    participant DynamoDB
    participant SNS
    participant SES
    participant Client

    ECS->>S3Quarantine: Move infected file
    S3Quarantine->>LError: Trigger error handler
    LError->>DynamoDB: Update job (FAILED)
    LError->>SNS: Publish error notification
    SNS->>SES: Send email
    SES-->>Client: ✗ Error notification
```
