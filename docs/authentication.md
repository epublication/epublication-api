# ePublication – Authentication

> This document is the single source of truth for authentication across the
> external ePublication API. It is referenced from both the
> [Announcement Import](announcement-import.md) and
> [Announcement Export](announcement-export.md) documentation instead of
> being duplicated in each.

---

## Overview

The external API has two zones. Both use the same wire format
(`Authorization: Bearer <token>`), but with different credential types:

| Zone | Path prefix | Credential | Typical use |
|---|---|---|---|
| Public | `/public/interface/v1/**` | **Personal API key** of a registered portal user | Search, detail and reference data (data consumers); announcement validation |
| Restricted | `/interface/v1/**` | **M2M OAuth2 token** (client credentials) of a **Technical User** | Announcement submission (data suppliers); authenticated search and detail |

**All endpoints of the external API require a credential.** Requests
without a valid `Authorization` header are rejected with `401`.

Because both zones use the same header, a third-party application can
integrate against either with one uniform pattern: one place in any HTTP
client where the secret is configured.

```http
GET /public/interface/v1/announcements/{publication-number}
Authorization: Bearer <your-personal-api-key>
```

```http
POST /interface/v1/announcements/submission
Authorization: Bearer <access-token-of-your-technical-user>
Content-Type: application/json
```

> **Base URL:** the paths in this documentation are relative to
> `https://preview.epublication.ch/api/management` (preview environment).

---

## Environments

| Environment | Status |
|---|---|
| Preview | Available. Used for all examples in this documentation. |
| Production | **Not available yet.** It will require its own, dedicated registration; credentials from the preview environment will not work there. This page will be updated when production opens. |

---

## Public zone: personal API key

Every registered portal user can obtain a personal API key. It identifies
the user towards the public zone. (The API specification also calls it the *interface key*.)

| Attribute | Value |
|---|---|
| Header | `Authorization: Bearer <api-key>` |
| Scope | All endpoints under `/public/interface/v1/**` |
| Cardinality | **One API key per user** |
| Obtained | In the portal, in the **personal user account** |
| Server-side storage | Hashed. The key can therefore not be recovered by the operator. |
| Revocable | Yes |

How to obtain the key, and further background on delivering and retrieving
data through the interface, is described in the Help Center article
[Daten per Schnittstelle anliefern und beziehen](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970644593052-Daten-per-Schnittstelle-anliefern-und-beziehen)
(German).

Treat the key like a password: do not commit it to version control and do
not embed it in client-side code.

---

## Restricted zone: Technical User (M2M OAuth2)

Announcement submission, and the authenticated variants of search and
detail, use a **Technical User**: a machine client belonging to one
Publishing Entity. It authenticates with the OAuth2 *client credentials*
flow.

A **Publisher** of a Publishing Entity creates and manages Technical Users
in the portal (gear icon of the Publishing Entity → tab **Technische
Benutzer**).

| Attribute | Value |
|---|---|
| Created by | Publisher of the owning Publishing Entity |
| Credential | `clientId` + `clientSecret` |
| Token endpoint (preview) | `https://login.preview.epublication.ch/oauth2/token` – the **same endpoint for every Publishing Entity** |
| Grant type | `client_credentials` |
| Token validity | **12 hours.** Request a new token when it has expired (or shortly before). |
| Role | `Data Supplier` |
| Scope | The full **restricted zone**. One Technical User covers announcement submission as well as the authenticated search and detail endpoints; no separate credential per capability is needed. |
| Cardinality | **One Technical User per Publishing Entity.** An application that submits for several Publishing Entities (e.g. several cantons) needs one Technical User, with its own `clientId`/`clientSecret`, per entity. |
| Limits | Up to 100 Technical Users per Publishing Entity; 10,000 system-wide |
| Visibility of the secret | Shown **only once**, when the Technical User is created. It cannot be retrieved afterwards; if it is lost, create a new Technical User. |
| Client Name | Chosen at creation. It is recorded as the `responsiblePerson` of every announcement submitted with this Technical User (see [Announcement Import](announcement-import.md)). |

Only the Publisher can create a Technical User, so that only the Publisher
ever sees the client secret. Provider-Admin and Provider-Supporter roles can
view and delete Technical Users. **Deleting a Technical User revokes its
access immediately.**

### Requesting a token

```http
POST https://login.preview.epublication.ch/oauth2/token
Authorization: Basic base64(<clientId>:<clientSecret>)
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

The response contains an `access_token`, which is sent as
`Authorization: Bearer <access_token>` to the restricted zone until it
expires. Do not request a new token for every call; cache it for its
validity period.

The [Bruno examples](../bruno/README.md) show this flow, including
automatic token handling.

---

## Which credential do I need?

| I want to … | Credential |
|---|---|
| Search or retrieve published announcements, read reference data | Personal API key |
| Validate an announcement payload (`/public/interface/v1/announcements/validate`) | Personal API key |
| Submit announcements | Technical User |
| Use the authenticated search and detail (additional fields, see [Announcement Export](announcement-export.md)) | Technical User |
