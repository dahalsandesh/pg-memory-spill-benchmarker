# CI/CD Query Performance Benchmarker

Evaluates database query performance and disk I/O bottlenecks under severe memory constraints.

## Components
- **Infra**: PostgreSQL (Memory-constrained container)
- **Bench**: Benchmarking scripts (Data seeding & Query execution)
- **API**: Metrics sink
- **Dashboard**: Visualization

## Setup

1. Spin up the database:
   ```bash
   cd infra
   docker-compose up -d
   ```
