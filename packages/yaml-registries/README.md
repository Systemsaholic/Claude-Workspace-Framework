# YAML Registries Package

Structured data management using YAML files as single sources of truth.

## Overview

The YAML Registries pattern provides:
- **Centralized Data** - One file per entity type
- **Human Readable** - Easy to read and edit
- **Git-Friendly** - Version controlled, diff-able
- **Claude-Native** - Easy to parse and query

## Philosophy

Instead of databases, we use YAML files for entity management:

| Traditional | YAML Registry |
|-------------|---------------|
| Database table | `entities.yaml` file |
| Row | YAML entry with code key |
| Column | YAML field |
| Query | Claude reads and filters |
| Update | Claude edits file |

## Registry Types

### By Business Domain

| Business | Primary Registry | Entity |
|----------|------------------|--------|
| MSP | `clients.yaml` | Client companies |
| Travel Agency | `advisors.yaml` | Travel advisors |
| Consultancy | `clients.yaml` | Client companies |
| E-commerce | `products.yaml` | Products |
| Agency | `projects.yaml` | Projects |
| HR | `employees.yaml` | Staff |

### Common Registries

| Registry | Purpose |
|----------|---------|
| `suppliers.yaml` | Vendor/supplier relationships |
| `contacts.yaml` | Contact directory |
| `servers.yaml` | Infrastructure inventory |
| `domains.yaml` | Domain management |

## Registry Structure

### Standard Format

```yaml
# entities.yaml

# Header comment explaining the registry
# Last updated: YYYY-MM-DD

entities:
  ENTITY_CODE:
    # Required fields
    name: "Entity Name"
    status: active  # active, inactive, pending, etc.
    created: "YYYY-MM-DD"

    # Contact info (if applicable)
    email: "email@example.com"
    phone: "+1-555-000-0000"

    # Relationships
    parent: PARENT_CODE  # if hierarchical
    tags:
      - tag1
      - tag2

    # Domain-specific fields
    custom_field: value

# Statistics/metadata
stats:
  total_active: 0
  total_inactive: 0
  last_updated: "YYYY-MM-DD"
```

### Entity Codes

| Pattern | Use Case | Example |
|---------|----------|---------|
| `ABBREV` | Companies | `ACME`, `RCCL` |
| `FLAST` | People | `JSMITH`, `MDOE` |
| `kebab-case` | Slugs | `north-office` |
| `PREFIX-NUM` | Sequential | `PRJ-001` |

## Common Schemas

### Client/Company Registry

```yaml
clients:
  ACME:
    name: "Acme Corporation"
    status: active
    created: "2025-01-15"

    # Contact
    primary_contact: "John Smith"
    email: "john@acme.com"
    phone: "+1-555-123-4567"

    # Address
    address:
      street: "123 Main St"
      city: "New York"
      state: "NY"
      zip: "10001"
      country: "USA"

    # Services/relationship
    services:
      - managed-it
      - cloud-backup
    tier: premium

    # Billing
    billing_email: "billing@acme.com"
    payment_terms: net-30

    # Internal
    account_manager: "Jane Doe"
    folder_path: "clients/acme"
    notes: ""
```

### Person Registry (Advisors, Employees, etc.)

```yaml
advisors:
  JSMITH:
    name: "John Smith"
    status: active
    joined: "2025-06-15"

    # Contact
    email: "jsmith@example.com"
    phone: "+1-555-123-4567"

    # Role/specialization
    role: "Travel Advisor"
    specializations:
      - cruises
      - caribbean
      - luxury

    # Compensation (if applicable)
    commission_split: 80

    # Performance
    ytd_sales: 150000
    rating: 4.8

    # Internal
    manager: "MDOE"
    notes: ""
```

### Supplier/Vendor Registry

```yaml
suppliers:
  RCCL:
    name: "Royal Caribbean International"
    type: cruise_line
    status: active

    # Contact
    contact:
      bdm_name: "Sales Rep"
      bdm_email: "rep@rccl.com"
      bdm_phone: "+1-555-000-0000"
      support_email: "support@rccl.com"

    # Commercial terms
    commission: 10
    payment_terms: "Monthly"
    contract_expires: "2026-12-31"

    # Access
    portal_url: "https://partner.rccl.com"
    portal_username: "user@company.com"

    # Categories
    categories:
      - cruise
      - caribbean
      - alaska

    notes: ""
```

### Server/Infrastructure Registry

```yaml
servers:
  web-prod-01:
    name: "Production Web Server 1"
    status: active

    # Network
    public_ip: "203.0.113.10"
    private_ip: "10.0.1.10"
    tailscale_ip: "100.64.0.10"
    hostname: "web-prod-01.company.com"

    # Specs
    provider: "AWS"
    region: "us-east-1"
    instance_type: "t3.medium"
    os: "Ubuntu 22.04"

    # Services
    services:
      - nginx
      - nodejs
      - postgresql

    # Access
    ssh_user: "ubuntu"
    ssh_key: "~/.ssh/prod_key"

    # Monitoring
    monitoring_url: "https://uptime.company.com/web-prod-01"

    # Maintenance
    backup_schedule: "daily"
    maintenance_window: "Sun 02:00-04:00 UTC"
```

## Entity Folders

Complement registries with per-entity folders for detailed docs:

```
entities/
├── ACME/
│   ├── profile.md          # Detailed profile
│   ├── contacts.md         # All contacts
│   ├── projects/           # Project folders
│   ├── agreements/         # Contracts, SOWs
│   ├── notes/              # Meeting notes
│   └── assets/             # Logos, files
```

### Profile Template

```markdown
# [Entity Name]

**Code:** ACME
**Status:** Active
**Since:** 2025-01-15

## Overview

[Description of the entity]

## Contacts

| Name | Role | Email | Phone |
|------|------|-------|-------|
| John Smith | CEO | john@acme.com | +1-555-123-4567 |

## Services

- Service 1
- Service 2

## Notes

[Running notes about the entity]

---
*Last updated: YYYY-MM-DD*
```

## Deployment

### Steps

1. **Identify entities** for your business
   ```
   What do you need to track?
   - Clients? Advisors? Products? Suppliers?
   ```

2. **Design schema** for each registry
   ```yaml
   # What fields do you need?
   # What's required vs optional?
   # What are valid status values?
   ```

3. **Create registry files**
   ```bash
   touch clients.yaml
   touch suppliers.yaml
   ```

4. **Create entity folders**
   ```bash
   mkdir -p clients/{ENTITY-CODE}
   ```

5. **Document in CLAUDE.md**
   ```markdown
   ## Key Files

   | File | Purpose |
   |------|---------|
   | `clients.yaml` | Client registry |
   ```

## Usage Patterns

### Lookup Entity

```
/client ACME
→ Read clients.yaml, find ACME entry, display details
```

### List Entities

```
/clients active
→ Read clients.yaml, filter by status=active, list names
```

### Update Entity

```
Update ACME status to inactive
→ Edit clients.yaml, change status field
```

### Add Entity

```
Add new client Globex Corporation
→ Add new entry to clients.yaml with code GLOBEX
```

## Best Practices

1. **One registry per entity type** - Don't mix clients and suppliers
2. **Consistent codes** - Use same pattern throughout
3. **Required fields first** - Name, status, created
4. **Document the schema** - Comment at top of file
5. **Update stats** - Keep counts current
6. **Git commit changes** - Track all modifications
7. **Validate periodically** - Ensure data consistency

## Integration Points

| System | Integration |
|--------|-------------|
| **Skills** | Lookup commands read registries |
| **Session Hub** | Route by entity code |
| **Email System** | Lookup contacts for emailing |
| **Memory System** | Reference entities in followups |

---

*Package version: 1.0.0*
