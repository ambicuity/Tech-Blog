---
layout: page
icon: fas fa-water
order: 3
title: Deep Dives
permalink: /courses/
---

## 🌊 My Engineering Library & Deep Dives

This is not a generic "Computer Science Curriculum." This is my personal engineering notebook.

As a Systems Engineer, I believe in **depth over breadth**. Below are the living documents where I deconstruct the legendary textbooks of our field and bridge the gap between their 1970s academic rigor and the modern, messy reality of Cloud Native infrastructure and AI environments.

These notes are heavily opinionated, brutally technical, and continually updated based on my lived experience in production.

<div class="row row-cols-1 row-cols-md-2 g-4 mb-5 mt-2">
  
  <!-- 1. System Design -->
  <div class="col">
    <a href="/courses/system-design/" class="text-decoration-none">
      <div class="card h-100 shadow-sm border-0">
        <div class="card-body">
          <h3 class="card-title text-dark"><i class="fas fa-server text-success me-2"></i>System Design for AI</h3>
          <p class="card-text text-muted">Deconstructing the Data-Intensive Application for modern LLM architectures, caching layers, and high-throughput pipelines.</p>
          <hr>
          <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">
              <i class="fas fa-book me-1"></i> Based on <strong>DDIA</strong>
            </small>
            <small class="text-secondary"><i class="far fa-clock me-1"></i> Last Updated: Feb 2026</small>
          </div>
        </div>
      </div>
    </a>
  </div>

  <!-- 2. OS -> Compute -->
  <div class="col">
    <a href="/courses/os/" class="text-decoration-none">
      <div class="card h-100 shadow-sm border-0">
        <div class="card-body">
          <h3 class="card-title text-dark"><i class="fab fa-linux text-warning me-2"></i>OS for Cloud Engineers</h3>
          <p class="card-text text-muted">Beyond Silberschatz. Understanding Linux cgroups, namespaces, and the actual kernel primitives powering Kubernetes and Containerd.</p>
          <hr>
          <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">
              <i class="fas fa-book me-1"></i> <strong>Linux Internals</strong>
            </small>
            <small class="text-secondary"><i class="far fa-clock me-1"></i> Last Updated: Jan 2026</small>
          </div>
        </div>
      </div>
    </a>
  </div>

  <!-- 3. DBMS -> Vector DBs -->
  <div class="col">
    <a href="/courses/dbms/" class="text-decoration-none">
      <div class="card h-100 shadow-sm border-0">
        <div class="card-body">
          <h3 class="card-title text-dark"><i class="fas fa-database text-danger me-2"></i>DBMS for the AI Era</h3>
          <p class="card-text text-muted">Bridging the "Cow Book" fundamentals with modern Vector Databases (Pinecone, Milvus) and advanced PostgreSQL internals.</p>
          <hr>
          <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">
              <i class="fas fa-book me-1"></i> <strong>Cow Book + Vector</strong>
            </small>
            <small class="text-secondary"><i class="far fa-clock me-1"></i> Last Updated: Dec 2025</small>
          </div>
        </div>
      </div>
    </a>
  </div>

  <!-- 4. Networking -->
  <div class="col">
    <a href="/courses/networking/" class="text-decoration-none">
      <div class="card h-100 shadow-sm border-0">
        <div class="card-body">
          <h3 class="card-title text-dark"><i class="fas fa-network-wired text-info me-2"></i>Cloud Networking</h3>
          <p class="card-text text-muted">Packet captures, Wireshark analysis, and BGP routing. Seeing Tanenbaum's theories in action across distributed mesh networks.</p>
          <hr>
           <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">
              <i class="fas fa-book me-1"></i> Based on <strong>Tanenbaum</strong>
            </small>
            <small class="text-secondary"><i class="far fa-clock me-1"></i> Last Updated: Nov 2025</small>
          </div>
        </div>
      </div>
    </a>
  </div>

</div>

> **Note**: I do not post placeholders. If a paradigm isn't listed here, it means I haven't finished bridging the theory to my production environments yet. Check back later.
