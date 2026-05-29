# DevOps Infrastructure — Production Readiness Module

Load this module ONLY for a full production-readiness review — a launch gate, disaster recovery validation, or compliance audit. These are NOT expected to be completed for every infrastructure change. For routine CI/CD or containerization tasks, the core checklist in the main agent file is sufficient.

---

## Pre-Launch Gate Checklist

Work through each category systematically. Every unchecked item should have a documented exception with owner and resolution date.

### Security

- [ ] No secrets committed to version control (scan with `git log -p | grep -i "password\|token\|secret\|key"`)
- [ ] All secrets in secrets manager (Vault, AWS Secrets Manager, GitHub Secrets) — not in `.env` files deployed to servers
- [ ] IAM roles use least-privilege policies — no wildcard `*` permissions on sensitive actions
- [ ] Security groups restrict inbound access: only required ports from required sources
- [ ] Backends (databases, internal services) in private subnets — not reachable from the internet
- [ ] SSL/TLS enabled on all external endpoints with HSTS header set
- [ ] Encryption at rest for databases, S3 buckets, and EBS volumes containing sensitive data
- [ ] Encryption in transit enforced (TLS 1.2+ minimum; TLS 1.3 preferred)
- [ ] Container images scanned for vulnerabilities (Trivy, ECR scanning, or equivalent)
- [ ] No container running as root user
- [ ] Security headers configured: `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Content-Security-Policy`
- [ ] Audit logging enabled: CloudTrail (AWS), Cloud Audit Logs (GCP), or equivalent
- [ ] Dependency audit clean: `npm audit` shows no high/critical CVEs, or exceptions documented
- [ ] Default credentials changed on all managed services
- [ ] Network egress restricted (containers can only reach required external services)

### Reliability

- [ ] Health check endpoints exist, respond correctly, and are wired into the load balancer / orchestrator
- [ ] Auto-scaling policies configured with appropriate min/max bounds and cooldown periods
- [ ] Load balancer configured with connection draining (graceful shutdown during deployments)
- [ ] Database connection pooling configured (prevents connection exhaustion under load)
- [ ] Retry logic implemented for transient failures (external APIs, message queues)
- [ ] Circuit breakers configured for service-to-service dependencies
- [ ] Graceful shutdown handlers registered (SIGTERM → drain requests → close connections → exit)
- [ ] Database read replicas configured (if applicable for read-heavy workloads)
- [ ] Multi-AZ deployment for stateful services (database, cache)
- [ ] RTO and RPO defined and documented (Recovery Time Objective, Recovery Point Objective)

### Backup and Disaster Recovery

- [ ] Database automated backups enabled with retention period matching RTO/RPO
- [ ] Backup restoration tested — not just verified to exist, but actually restored and verified
- [ ] Disaster recovery runbook documented and accessible to on-call team
- [ ] DR environment provisioned and tested (or documented approach for spinning up from IaC)
- [ ] Cross-region backup copies configured (if required by RPO)
- [ ] Data export procedure documented (for compliance or data portability)

### Deployment Safety

- [ ] Rollback procedure documented, tested, and timed (know how long it takes)
- [ ] Deployment tested in staging with production-equivalent data volume and traffic patterns
- [ ] Database migrations are backwards-compatible (old code can run against new schema)
- [ ] Feature flags used for risky new behavior (can disable without redeployment)
- [ ] Canary or blue-green deployment configured (for zero-downtime rollouts)
- [ ] Deployment locks in place (prevent concurrent deploys to same environment)

### Monitoring and Alerting

- [ ] Application error rate monitored with alert threshold defined (e.g., >1% 5xx over 5 minutes)
- [ ] Latency monitored (p95 and p99) with alert thresholds
- [ ] Infrastructure metrics monitored: CPU, memory, disk, network I/O
- [ ] Database performance monitored: query latency, connection count, replication lag
- [ ] Alert routing configured (on-call rotation, escalation policy)
- [ ] Dashboards created for key service health metrics
- [ ] Log aggregation configured (CloudWatch Logs, DataDog, Loki) with retention policy
- [ ] Synthetic monitoring or uptime checks configured for external-facing endpoints
- [ ] Dead-letter queues monitored for message queue failures

### Testing

- [ ] Infrastructure tested in dev environment first
- [ ] Infrastructure tested in staging environment with production-equivalent config
- [ ] Load testing performed for high-traffic paths (if applicable) — results documented
- [ ] Rollback procedure rehearsed (not just documented)
- [ ] Health checks verified to actually detect unhealthy state (not just return 200 always)
- [ ] Disaster recovery test performed and results documented

### Documentation

- [ ] Architecture diagram created and current (shows services, data flows, network boundaries)
- [ ] Deployment runbook written (step-by-step for on-call responders, not just authors)
- [ ] All environment variables documented in `.env.example` with descriptions
- [ ] Secrets rotation procedure documented (who, how often, how to rotate without downtime)
- [ ] Disaster recovery procedures documented in runbook
- [ ] Access control documented (who has access to what, and how access is granted/revoked)
- [ ] On-call runbook updated with this service's common failure modes and remediation steps
- [ ] techContext.md and systemPatterns.md updated in memory bank

### Cost

- [ ] Cost estimate reviewed before provisioning (AWS Cost Calculator or equivalent)
- [ ] Budget alerts configured (alert at 80% of expected monthly spend)
- [ ] Right-sized resources (don't over-provision; use metrics to validate sizing)
- [ ] Reserved instances or savings plans considered for steady-state workloads
- [ ] Auto-scaling configured to scale down during low-traffic periods
- [ ] Unused resources removed (old AMIs, snapshots, EBS volumes, load balancers)
- [ ] Data transfer costs reviewed (cross-AZ, cross-region, internet egress)

### Team Readiness

- [ ] On-call team briefed on the new service or change
- [ ] Runbook accessible to all on-call members (not just the author)
- [ ] Alert ownership assigned (team knows who responds to which alerts)
- [ ] Escalation path documented (what to do if on-call cannot resolve within 30 minutes)

---

## Production Readiness Sign-Off

Before marking production launch complete, obtain acknowledgment from:

- [ ] Engineering lead (technical implementation reviewed)
- [ ] Security review (security section above verified)
- [ ] On-call lead (runbooks reviewed, team briefed)
- [ ] Product/business stakeholder (launch timing and rollback criteria agreed)

Document any items marked as exceptions with: item, reason for exception, owner, and resolution date.
