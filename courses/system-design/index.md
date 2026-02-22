---
layout: page
title: System Design for AI (DDIA)
permalink: /courses/system-design/
---

## 🏗️ Foundations: Designing Data-Intensive Applications (DDIA)
*(Modern Supplements added for LLMs, Vector Databases, and Scalability Physics)*

This deep dive bridges the gap between classic Relational Database theory and the reality of production-grade Cloud Architecture.

---

## Chapter 1: The Foundations of Scalability & Latency

### 1.1 The Rigor: The P99 Lie
To measure scalability, we do not look at averages. The arithmetic mean is mathematically useless for measuring latency. We look at **Percentiles** ($p50, p90, p99$). The $p99$ latency indicates the slowest $1\%$ of requests. The slowest requests are often experienced by the users with the most data (your highest-paying Enterprise customers).

### 1.2 Modern Application: Tail Latency Amplification in AI Pipelines
When building a production RAG (Retrieval-Augmented Generation) pipeline, an end-user request requires scattering sub-requests across multiple downstream services: Semantic chunking, OpenAI Embeddings (`text-embedding-3-small`), a Vector DB query (Pinecone), and LLM generation (Anthropic Claude).

If each of those services has a $p99$ latency of $2.0$ seconds, the probability that a user request encounters at least one $2.0$-second delay is $1 - (0.99)^4 \approx 3.9\%$. 
Because you chained services, your $p95$ user latency geometrically becomes your downstream services' $p99$ latency. This is **Tail Latency Amplification**. You mathematically punish an exponential number of your users because of downstream dependency chains.

---

## Chapter 2: Data Models & Query Languages

### 2.1 The Rigor: Relational vs. Document Models
* **Relational Model (SQL)**: Excellent for joins, many-to-one, and many-to-many relationships. Enforces strict schema and data integrity natively via the Engine.
* **Document Model (NoSQL/MongoDB)**: Excellent for one-to-many relationships (Self-contained JSON). Relies on "Schema-on-Read." The brutal truth: Schema-less does not exist. The schema enforcement obligation is violently transferred from the optimized C++ database directly into your fragile python application code. `KeyError` exceptions become fatal runtime errors.

### 2.2 Modern Application: Vector Search and Dimensionality
An LLM cannot query a SQL database for "a document that feels optimistic." 
We map raw, unstructured data into high-dimensional geometric spaces ($1536$ dimensions) using neural Embeddings. In this space, vector distance directly correlates to semantic similarity. 

Because standard B-Trees cannot navigate high-dimensional space without invoking a catastrophic $O(N)$ dot-product scan (a consequence of the **Curse of Dimensionality**), Vector Databases rely on Approximate Nearest Neighbor (ANN) algorithms (like **HNSW - Hierarchical Navigable Small World** graphs). By mathematically trading perfect recall accuracy ($100\%$) for aggressive graph-hopping, they convert a 10-minute linear table scan into a 10-millisecond logarithmic query.

---

## Chapter 3: Encoding & Evolution

### 3.1 The Rigor: Backward and Forward Compatibility
A database outlives the application code that created it. To update an API without incurring downtime, you execute **Rolling Upgrades**. 
Nodes run different versions of the code simultaneously. 
* **Backward Compatibility**: Newer code must safely read data written by older code.
* **Forward Compatibility**: Older code must gracefully swallow and ignore newly added column payloads written by newer code.

### 3.2 The Engineer’s Perspective: The `SELECT *` Time-Bomb
A junior engineer aggressively executes `SELECT * FROM users` using raw tuples in Python because "it is faster to type."

**Gotcha:** `SELECT *` destroys mathematical forward compatibility. 
If an Ops engineer runs an unblocking `ALTER TABLE ADD COLUMN is_premium BOOLEAN;`, your v1.0 deployment crashes instantly in production. The Python tuple unpacking expects exactly 3 indices. The database suddenly returned 4 indices. Your entire API fleet throws a `ValueError: too many values to unpack`. 
Explicitly name string projections (`SELECT id, name`) to guarantee structural immunity to column evolution over decades of runtime.

---

## Chapter 4: Distributed Replication, Consensus, and Splitting Brains

### 4.1 The Rigor: Quorum Consistency
In a Leaderless architecture (DynamoDB, Cassandra), you enforce absolute **Strong Consistency** without sequential locking using Quorums.

If your cluster has $N$ nodes, you define $W$ nodes strictly required to acknowledge a Write, and $R$ nodes required to query a Read. To geometrically guarantee a client always receives the absolute newest data despite network failure or lag, you enforce the inequality:
$$ W + R > N $$

### 4.2 The Engineer’s Perspective: Splitting Brains and Fencing Tokens
In an active-passive setup, Node A is Primary. A network partition isolates Node A from the master Kubernetes Control Plane. 
The Control Plane assumes Node A is dead, panics, and promotes Node B to Primary.

**Gotcha:** Node A is *not* dead. It was merely experiencing an asymmetric network transit drop. Both Node A and Node B believe they hold the authoritative Master Lock, and both simultaneously push conflicting bytes to the attached Amazon EBS storage array. This mathematically triggers **Split-Brain Corruption**, irrecoverably destroying the database binary cluster state.

To fix this, distributed systems mandate **Fencing Tokens**. When Node B is promoted, the ZooKeeper Consensus Engine gives it strictly-increasing Monotonic Token #2. When Zombie Node A attempts to write, the physical storage controller checks the Token, realizes Node A is wielding expired Token #1, geographically rejects the write signal, and violently fences Node A out of the hardware subsystem forever.

---
*See [DBMS for the AI Era](/courses/dbms/) for the deeper mechanics of B-Trees, Indexing, and Isolation.*
