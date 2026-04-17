```yaml
---
layout: post
title: "Kubernetes Policy Drift: A Postmortem on Preventing Future Outages"
date: 2024-01-26 12:00:00 -0000
categories: [kubernetes, security, policy-as-code]
tags: [admission-control, opa, kyverno, policy-drift, outage, postmortem]
description: "A detailed account of a Kubernetes production outage caused by policy drift in admission control, outlining the timeline, root cause, and prevention strategies."
author: "Production Engineering Team"
---

Were your recent Kubernetes deployments unexpectedly blocked, leading to service degradation? Our team recently experienced a production outage stemming from a subtle but critical issue: Kubernetes policy drift. This postmortem dissects the incident, explores the root cause, and details the steps we're taking to prevent similar occurrences in the future, ensuring a more robust and reliable platform, and will help you take steps to measure and monitor your own clusters.

## Kubernetes Policy Drift: A Production Outage Story

We experienced a significant service disruption when a routine application deployment triggered a cascade of pod eviction errors across our Kubernetes cluster. The errors manifested as `admission webhook "validate-resource.example.com" denied the request: ... violates policy ...` messages, effectively halting new deployments and impacting existing workloads. The initial assumption was a faulty application update, but deeper investigation revealed a more systemic problem: a divergence between our intended Kubernetes policies and the policies actually enforced by our admission controller [CLAIM:Root-cause mechanism]. This divergence, or policy drift, resulted in the admission controller blocking deployments that should have been allowed under our intended configuration.

## The Incident: Unexpected API Deprecation & Admission Webhook Failure

The immediate trigger was the deployment of an application using a Kubernetes API version that had been deprecated [CLAIM:Failure mode under production load]. While our manifests *should* have been updated to reflect the new API version, a subtle oversight in our CI/CD pipeline allowed the outdated manifests to be deployed. This, in itself, wouldn't have been catastrophic if our admission controller had been correctly configured to flag deprecated APIs. However, the admission webhook responsible for validating API versions had silently failed due to a misconfiguration introduced during a recent update. This meant that the deprecated API version slipped through the initial validation checks, only to be caught later by a more general-purpose policy that treated all unknown API versions as invalid.

## Timeline of Events: From Manifest Generation to Cluster-Wide Impact

1.  **T-7 days:** A Kubernetes cluster upgrade to v1.27 was performed. This upgrade deprecated a specific API version used by several of our applications.
2.  **T-3 days:** The platform team updated the admission webhook configuration to include validation rules for the new API versions in v1.27. However, a subtle error in the YAML configuration caused the webhook to silently fail to initialize.
    ```yaml
    # Incorrect webhook configuration
    apiVersion: admissionregistration.k8s.io/v1
    kind: ValidatingWebhookConfiguration
    metadata:
      name: validate-resource.example.com
    webhooks:
      - name: api-version-check.example.com
        clientConfig:
          service:
            name: api-version-validator
            namespace: platform-team
          caBundle: LS0tLS1CRUdJTi... # (truncated)
        rules:
          - apiGroups:   ["apps"]
            apiVersions: ["v1beta1"] # Incorrect - should be v1
            operations:  ["CREATE", "UPDATE"]
            resources:   ["deployments"]
        failurePolicy: Fail
        admissionReviewVersions: ["v1", "v1beta1"] # typo here!
        sideEffects: None
    ```
3.  **T-1 day:** A developer committed a change to an application deployment manifest that still used the deprecated API version. The CI/CD pipeline, lacking specific validation for deprecated APIs, did not flag the issue.
4.  **T+0:** The updated application deployment was initiated. The admission webhook, due to its failed state, did not intercept the request. The deployment proceeded, but pods failed to start due to the deprecated API version.
5.  **T+15 minutes:** Alerting systems triggered on the increasing number of failing pods. Initial investigations focused on the application itself.
6.  **T+1 hour:** The platform team identified the failed admission webhook and the deprecated API version as the root cause.

## Branch Point: Identifying the Policy Drift Culprit

The key branching point occurred when the admission webhook configuration was updated. Instead of thoroughly validating the new configuration and monitoring its operational status, the platform team assumed the changes were successfully applied. This assumption masked the underlying failure, allowing the deprecated API version to slip through the cracks. Had we implemented automated validation and monitoring of the admission webhook, we would have detected the misconfiguration immediately, preventing the subsequent outage.

## Root Cause Analysis: Why Our Admission Control Failed Us

The root cause of the outage was a combination of factors [CLAIM:Root-cause mechanism]:

*   **Lack of Automated Validation:** We lacked automated tests to validate the admission webhook configuration after updates. This allowed the misconfiguration to persist undetected.
*   **Insufficient Monitoring:** We did not have sufficient monitoring in place to detect that the admission webhook was failing. We relied on application-level alerts, which only triggered after the damage was done.
*   **Incomplete CI/CD Pipeline:** Our CI/CD pipeline did not include specific checks for deprecated API versions. This allowed outdated manifests to be deployed to the cluster.
*   **Manual Configuration Errors:** The error in the webhook configuration itself was a result of manual configuration, which is prone to human error.

## Prevention Strategies: Hardening Kubernetes Policies Against Drift

To prevent similar outages in the future, we are implementing the following strategies:

*   **Policy as Code (PaC):** We are adopting a Policy as Code approach using tools like OPA (Open Policy Agent) and Kyverno. This allows us to define policies in a declarative manner and store them in Git, enabling version control, automated testing, and auditability.
*   **Automated Policy Validation:** We are integrating automated tests into our CI/CD pipeline to validate admission webhook configurations and OPA/Kyverno policies. These tests will ensure that policies are correctly configured and enforced.
*   **Enhanced Monitoring:** We are implementing more comprehensive monitoring of our admission webhooks and OPA/Kyverno deployments. This includes monitoring their operational status, policy enforcement rates, and any errors or exceptions.
    ```yaml
    # Example Prometheus query to monitor admission webhook success rate
    sum(rate(admission_webhook_admission_duration_seconds_count{name="api-version-check.example.com",operation="VALIDATE"}[5m]))
      /
    sum(rate(admission_webhook_admission_duration_seconds_count{name="api-version-check.example.com"}[5m]))
    ```
*   **CI/CD Pipeline Enhancements:** We are adding checks to our CI/CD pipeline to detect and flag deprecated API versions. This will prevent outdated manifests from being deployed to the cluster.
*   **Centralized Policy Management:** We are establishing a centralized policy management system to ensure consistent policy enforcement across all our Kubernetes clusters.
*   **Regular Policy Audits:** We will conduct regular audits of our Kubernetes policies to identify and address any potential drift or inconsistencies.

## Operational Checklist: Future-Proofing Admission Control

To ensure the ongoing effectiveness of our admission control policies, we are implementing the following operational checklist [CLAIM:Operational mitigation]:

*   [ ] **Policy Versioning:** Implement a robust versioning strategy for all admission control policies, including webhooks and OPA/Kyverno policies.
*   [ ] **Automated Testing:** Integrate automated tests into the CI/CD pipeline to validate policy configurations and enforcement.
*   [ ] **Monitoring & Alerting:** Implement comprehensive monitoring of admission webhooks and OPA/Kyverno deployments, including success rates, error rates, and policy enforcement metrics.
*   [ ] **Drift Detection:** Implement automated drift detection mechanisms to identify discrepancies between intended policies and actual enforcement.
*   [ ] **Rollback Procedures:** Establish clear rollback procedures for policy updates in case of errors or unexpected behavior.
*   [ ] **Documentation:** Maintain comprehensive documentation of all admission control policies, including their purpose, configuration, and intended behavior.
*   [ ] **Regular Audits:** Conduct regular audits of Kubernetes policies to identify and address any potential drift or inconsistencies.
*   [ ] **API Version Awareness:** Regularly update application manifests and admission control policies to reflect the latest Kubernetes API versions.

## Evidence & References

*   Kubernetes Documentation on Admission Controllers: [https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
*   Open Policy Agent (OPA) Documentation: [https://www.openpolicyagent.org/docs/latest/](https://www.openpolicyagent.org/docs/latest/)
*   Kyverno Documentation: [https://kyverno.io/docs/](https://kyverno.io/docs/)
*   Runtime metrics from Prometheus, Grafana dashboards showing admission webhook failure rates.
*   Audit logs from Kubernetes API server, showing the denied requests due to policy violations.
*   Vendor documentation for our Kubernetes platform, detailing best practices for admission control configuration and management.