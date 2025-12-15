# Color Palettes Reference

Color schemes for different platforms and component types.

---

## Default Palette (Platform-Agnostic)

| Component Type | Background | Stroke | Example |
|----------------|------------|--------|---------|
| Frontend/UI | `#a5d8ff` | `#1971c2` | Next.js, React apps |
| Backend/API | `#d0bfff` | `#7048e8` | API servers, processors |
| Database | `#b2f2bb` | `#2f9e44` | PostgreSQL, MySQL, MongoDB |
| Storage | `#ffec99` | `#f08c00` | Object storage, file systems |
| AI/ML Services | `#e599f7` | `#9c36b5` | ML models, AI APIs |
| External APIs | `#ffc9c9` | `#e03131` | Third-party services |
| Orchestration | `#ffa8a8` | `#c92a2a` | Workflows, schedulers |
| Validation | `#ffd8a8` | `#e8590c` | Validators, checkers |
| Network/Security | `#dee2e6` | `#495057` | VPC, IAM, firewalls |
| Classification | `#99e9f2` | `#0c8599` | Routers, classifiers |
| Users/Actors | `#e7f5ff` | `#1971c2` | User ellipses |
| Message Queue | `#fff3bf` | `#fab005` | Kafka, RabbitMQ, SQS |
| Cache | `#ffe8cc` | `#fd7e14` | Redis, Memcached |
| Monitoring | `#d3f9d8` | `#40c057` | Prometheus, Grafana |

---

## AWS Palette

| Service Category | Background | Stroke |
|-----------------|------------|--------|
| Compute (EC2, Lambda, ECS) | `#ff9900` | `#cc7a00` |
| Storage (S3, EBS) | `#3f8624` | `#2d6119` |
| Database (RDS, DynamoDB) | `#3b48cc` | `#2d3899` |
| Networking (VPC, Route53) | `#8c4fff` | `#6b3dcc` |
| Security (IAM, KMS) | `#dd344c` | `#b12a3d` |
| Analytics (Kinesis, Athena) | `#8c4fff` | `#6b3dcc` |
| ML (SageMaker, Bedrock) | `#01a88d` | `#017d69` |

---

## Azure Palette

| Service Category | Background | Stroke |
|-----------------|------------|--------|
| Compute | `#0078d4` | `#005a9e` |
| Storage | `#50e6ff` | `#3cb5cc` |
| Database | `#0078d4` | `#005a9e` |
| Networking | `#773adc` | `#5a2ca8` |
| Security | `#ff8c00` | `#cc7000` |
| AI/ML | `#50e6ff` | `#3cb5cc` |

---

## GCP Palette

| Service Category | Background | Stroke |
|-----------------|------------|--------|
| Compute (GCE, Cloud Run) | `#4285f4` | `#3367d6` |
| Storage (GCS) | `#34a853` | `#2d8e47` |
| Database (Cloud SQL, Firestore) | `#ea4335` | `#c53929` |
| Networking | `#fbbc04` | `#d99e04` |
| AI/ML (Vertex AI) | `#9334e6` | `#7627b8` |

---

## Kubernetes Palette

| Component | Background | Stroke |
|-----------|------------|--------|
| Pod | `#326ce5` | `#2756b8` |
| Service | `#326ce5` | `#2756b8` |
| Deployment | `#326ce5` | `#2756b8` |
| ConfigMap/Secret | `#7f8c8d` | `#626d6e` |
| Ingress | `#00d4aa` | `#00a888` |
| Node | `#303030` | `#1a1a1a` |
| Namespace | `#f0f0f0` | `#c0c0c0` (dashed) |

---

## Diagram Type Suggestions

| Diagram Type | Recommended Layout | Key Elements |
|--------------|-------------------|--------------|
| Microservices | Vertical flow | Services, databases, queues, API gateway |
| Data Pipeline | Horizontal flow | Sources, transformers, sinks, storage |
| Event-Driven | Hub-and-spoke | Event bus center, producers/consumers |
| Kubernetes | Layered groups | Namespace boxes, pods inside deployments |
| CI/CD | Horizontal flow | Source -> Build -> Test -> Deploy -> Monitor |
| Network | Hierarchical | Internet -> LB -> VPC -> Subnets -> Instances |
| User Flow | Swimlanes | User actions, system responses, external calls |
