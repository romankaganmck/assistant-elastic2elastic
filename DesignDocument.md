# Design Document Template

## Overview
This document covers the template for the design documents which will be created for any features in the G2 or related microservices.

### When Not Applicable
Design document can be skipped in the following scenarios:
- No DB Changes
- No system impacts
- No new web service or end points

## Audience
All the Engineering managers, Architects, Team Leads, and those who need to reference it to create the design documents.

## Recommended Tools
To create the architecture or diagrams, you can use the following tools:
- Microsoft Visio
- Miro
- Eclipse Plugins can be used to create sequence and ER diagrams.

## Design Template
This template has multiple sections for their respective purposes, but all might not be applicable for each and every feature design.

- High-Level Design
- Low-Level Design
- Database Changes
- Diagrams
  - Class Diagram
  - Sequence Diagram
  - ER Diagram

### Existing System Impacts
- Functional
- Front-end UI
- Backend
- Deployment and/or CI/CD

### Non-Functional
- Performance
- Security
- Web Services
  - Endpoints
  - Authentication
  - Authorization
  - Consumers
  - Network and Connectivity
- Batch-Jobs
  - Batch Job Purpose
  - Frequency
- Configurations
  - Introduced / Updated / Removed

## Rollout Plan
- Build Profile
- Lower/Stage Environments
- Production Environment

## Data Updates
- Repair/Corrections
- Migration

## Error Handling
- Error Scenarios
- Exceptions handling

## Revision & Approval History
Auto-generated section hosting the version and approval history of this document

| Role    | Version           | Approver Name | Date       |
|---------|-------------------|---------------|------------|
| Author  | Initial version  |               | 06/10/2023 |

### Revision History
| Rev | Date       | Change Request# | Summary of Change | Author        |
|-----|------------|-----------------|-------------------|---------------|
| 0.1 | 06/10/2023 |                 | Initial version  | Parveen Kumar |
