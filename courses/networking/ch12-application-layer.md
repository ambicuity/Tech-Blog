---
layout: page
title: "Networking Ch.12: App Layer"
permalink: /courses/networking/ch12-application-layer/
---

# Chapter 12: The Application Layer

> **Reference**: *Computer Networks* by Andrew S. Tanenbaum, Chapter 7

The layer where network applications and their application-layer protocols reside. The only layer the user actually interacts with.

## 12.1 DNS - The Domain Name System
Maps human-readable names (`www.google.com`) to IP addresses (`142.250.190.46`).
- **Hierarchy**: Root (.) $\to$ TLD (.com, .edu) $\to$ Domain (google.com).
- **Zones**: Administrative boundaries.
- **Resource Records**:
    - `A`: IPv4 Address.
    - `AAAA`: IPv6 Address.
    - `CNAME`: Alias/Canonical Name.
    - `MX`: Mail Exchange.

## 12.2 Electronic Mail (Email)
- **User Agent**: Outlook, Gmail.
- **Message Transfer Agent (MTA)**: Postfix, Sendmail. Relays mail.
- **Protocols**:
    - **SMTP (Simple Mail Transfer Protocol)**: Pushing mail from sender to server, and server to server. (Port 25).
    - **POP3 / IMAP**: Pulling mail from server to user.

## 12.3 The World Wide Web (HTTP)
- **URL (Uniform Resource Locator)**: `protocol://DNS-name/file-name`.
- **HTTP (HyperText Transfer Protocol)**:
    - Stateless Request/Response.
    - Verbs: `GET`, `POST`, `PUT`, `DELETE`.
    - Codes: 200 (OK), 404 (Not Found), 500 (Server Error).
- **HTML**: Markup language.

### Performance Enhancements
- **Caching**: Browser cache, Proxy cache, CDN.
- **HTTP/1.1**: Persistent connections (Keep-Alive).
- **HTTP/2**: Multiplexing (Multiple requests over one connection).
- **HTTP/3**: Based on **QUIC** (over UDP). Removes head-of-line blocking.
