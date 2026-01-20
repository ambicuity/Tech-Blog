---
layout: page
title: "System Design Ch.11: Stream Processing"
permalink: /courses/system-design/ch11-stream-processing/
---

# Chapter 11: Stream Processing

> **Reference**: *Designing Data-Intensive Applications* (DDIA) by Martin Kleppmann, Chapter 11

In batch processing, input is a bounded file. In **stream processing**, input is unbounded (never-ending).

## 11.1 Transmitting Event Streams
- **Producers** send events. **Consumers** process them.
- **Direct Messaging**: UDP/TCP/HTTP. (Data loss if consumer crashes).
- **Message Brokers (Queues)**: RabbitMQ, ActiveMQ.
    - AMQP/JMS standards.
    - Consumer acknowledges message. Broker deletes it.

### Log-Based Message Brokers (Kafka)
- Apache **Kafka**, Amazon Kinesis.
- Broker writes all messages to an append-only log on disk.
- **Offset**: Consumers track where they are in the log.
- **Replay**: Consumers can reset offset to re-read old messages.

## 11.2 Databases and Streams
- **Change Data Capture (CDC)**: Observe all changes written to a DB and replicate them to other systems (Search Index, Warehouse). Debezium is a popular tool.
- **Event Sourcing**: Store all changes to application state as a log of immutable events. (e.g., Accounting ledger).

## 11.3 Processing Streams
- **Complex Event Processing (CEP)**: Regex for events. (e.g., Fraud detection).
- **Stream Analytics**: Aggregations over windows.
    - **Tumbling Window**: Fixed, non-overlapping (00:00-00:05, 00:05-00:10).
    - **Hopping Window**: Fixed, overlapping (00:00-00:05, 00:01-00:06).
    - **Sliding Window**: Events within X minutes of each other.
- **Time**: Event Time (when it happened) vs Processing Time (when server saw it).
