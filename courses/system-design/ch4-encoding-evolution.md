---
layout: page
title: "System Design Ch.4: Encoding"
permalink: /courses/system-design/ch4-encoding-evolution/
---

# Chapter 4: Encoding and Evolution

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 4

Applications change over time. Features are added, and data models evolve. We need to handle this evolution gracefully without downtime.

## 4.1 Formats for Encoding Data
Two types of data representations:
1.  **In-Memory**: Objects, structs, lists, pointers. Optimized for CPU.
2.  **On-the-Wire**: Byte sequences (JSON, XML, Protobuf). Optimized for transmission/storage.

**Translation** between them is called *encoding* (serialization) and *decoding* (deserialization).

### Textual Formats (JSON, XML, CSV)
- **Pros**: Human readable. Ubiquitous.
- **Cons**: Ambiguity (numbers vs. strings), verbose, no binary support without Base64.

### Binary Formats
- **Thrift (Facebook)** and **Protocol Buffers (Google)**
    - Require a **schema** definition.
    - Use field **tags** (numbers) instead of field names to save space.
- **Avro (Hadoop)**
    - Schema is dynamic. Excellent for schema evolution.

## 4.2 Modes of Data Flow
How does encoded data move between processes?

### 1. via Databases
- The process writing to the DB encodes the data; the process reading decodes it.
- **Scenario**: Rolling upgrade. Old code might read new data (Forward Compatibility), New code might read old data (Backward Compatibility).

### 2. via Service Calls (REST and RPC)
- **REST**: Resource-oriented, standard HTTP verbs.
- **RPC (Remote Procedure Call)**: Tries to make a remote network request look like a local function call. (gRPC, Finagle).
    - **gRPC**: Uses Protocol Buffers.

### 3. via Message-Passing (Asynchronous)
- **Message Brokers**: RabbitMQ, Kafka, ActiveMQ.
- One-way fire-and-forget. The sender doesn't wait for a response.
- Decouples sender from receiver.

## 4.3 Schema Evolution rules
- **Forward Compatibility**: Old code can read data written by new code.
- **Backward Compatibility**: New code can read data written by old code.
- **Protobuf/Thrift**:
    - **Adding fields**: Give it a new tag number. Old code ignores unknown tags (Forward compatible). New code handles missing tags as null/default (Backward compatible).
    - **Removing fields**: Only remove optional fields. Never reuse tag numbers.
