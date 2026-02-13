# Task 2 — Architect (AWS)

## Task description

Assume you have an API that receives a **large JSON file** containing product information that must be imported into
your system. Because processing this data **synchronously inside the API** would be too heavy, the flow should be:

1) receive the data
2) store it **temporarily**
3) process it asynchronously

## Processing steps (requirements)

Your processing pipeline must include:

- **Validation** of the incoming data (e.g., required attributes are present)
- **Antivirus scanning** of the uploaded file
- **Metadata standardization** (e.g., different color names such as “Galaxy Blue”, “Navy Blue”, “Royal Blue” should be
  normalized to a single format such as “Dark blue”)
- **Media processing** to generate different resolutions for use on different platforms
- **Persisting** the processed data into the correct collection/storage

## Error handling & notification

If any error occurs during processing, you must **notify the uploader** (assume you have their contact details).

## Search requirement

After processing, the system must support **high-performing search queries** on the processed data (e.g., search by
color, size, material, etc.).

## Deliverable

Create an **architecture diagram** (preferably using AWS services) that satisfies the requirements above.  
You may use diagrams.net, and you should submit the diagram as an **image**.  
Optionally include a short explanation to justify your design decisions.


