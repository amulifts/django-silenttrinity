# SilentTrinity TeamServer

## Overview

**SilentTrinity TeamServer** is a robust and secure Command and Control (C2) server designed to manage and orchestrate communication between the server and multiple remote agents. Built with Django, WebSockets, and ZeroMQ, TeamServer facilitates real-time data exchange, secure communications, and comprehensive session management, making it an ideal solution for cybersecurity operations, automation, and remote management tasks.

## Key Features

- **Real-Time Communication:**
  - **WebSocket Server:** Enables bidirectional, low-latency communication with clients using WS/WSS protocols.
  - **ZeroMQ IPC:** Facilitates inter-process communication within server components using the PUB/SUB pattern.

- **Security:**
  - **End-to-End Encryption:** Implements ECDH for secure key exchange and AES-GCM for encrypting messages.
  - **CurveZMQ Encryption:** Secures ZeroMQ IPC channels to prevent unauthorized access.

- **User and Session Management:**
  - **Custom User Model:** Extends Django’s user model with UUIDs and timestamp fields for enhanced scalability.
  - **Session Tracking:** Monitors active client sessions, capturing essential client information and activity timestamps.
  - **Task Management:** Handles task assignments and stores results from client-executed tasks.

- **Logging and Monitoring:**
  - **Structured Logging:** Utilizes JSON-formatted logs with redaction of sensitive data for easy parsing and analysis.
  - **Rotating Logs:** Manages log sizes and backups to ensure efficient storage.
  - **Console Monitoring:** Provides colored console logs for real-time monitoring and debugging.

## Architecture

TeamServer leverages a modular architecture to ensure scalability, security, and maintainability:

1. **WebSocket Server:** Handles real-time communication with clients, supporting both secure (WSS) and insecure (WS) connections based on configuration.
2. **ZeroMQ IPC Server:** Manages inter-process communications between server components, utilizing secure CurveZMQ encryption when enabled.
3. **Django Backend:** upcoming feature ...
4. **Cryptography Module:** Ensures all communications are encrypted using industry-standard protocols (ECDH, AES-GCM).
5. **Logging Module:** Implements comprehensive logging with structured JSON output and sensitive data redaction.

## Getting Started

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/silenttrinity.git
   cd silenttrinity/silenttrinity
