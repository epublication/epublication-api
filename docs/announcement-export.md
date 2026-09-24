# ePublication – API Documentation for Announcement Export (Developer Guide)

> **Audience:** Both anonymous/public consumers (e.g. media, general
> research tools) and authenticated third-party applications (upstream
> systems) that want to retrieve published announcements from ePublication
> (Swiss Official Gazettes Portal) and process them further.
>
> **Scope:** This document describes **announcement export** — searching
> and retrieving already-published (or, for the respective consumer,
> visible) announcements. For submitting new announcements, see the
> separate *"API Documentation for Announcement Import"*.

---

**Fair Use Policy**

As a guideline, a single API consumer should not retrieve more than the order of magnitude of announcements per day — with typical usage (a search followed by one detail request per announcement), that corresponds to roughly 2,000–3,000 requests per day.

Thank you for respecting these policies. We reserve the right to technically limit excessive or abusive usage.


## Table of Contents

1. [Overview: Public vs. Authenticated View](#1-overview-public-vs-authenticated-view)
2. [Prerequisites & Access](#2-prerequisites--access)
3. [API Basics](#3-api-basics)
4. [Searching Announcements](#4-searching-announcements)
5. [Retrieving Announcement Detail](#5-retrieving-announcement-detail)
6. [Downloading Attachments](#6-downloading-attachments)
7. [Reference Data Endpoints](#7-reference-data-endpoints)
8. [Error Handling](#8-error-handling)
9. [Best Practices](#9-best-practices)
10. [Support & Further Links](#10-support--further-links)

---

## 1. Overview: Public vs. Authenticated View

Announcement export exists **in parallel in two variants**, with identical
core functionality (search + detail) but a different result scope:

| | Public zone | Authenticated zone |
|---|---|---|
| Path prefix | `/public/interface/v1/**` | `/interface/v1/**` |
| Auth | none (anonymous) | required |
| Visible announcements | only publicly visible ones, with status `PUBLISHED` or `CANCELLED` | all announcements the authenticated consumer is authorized for (possibly including further statuses) |
| Additional fields in the detail | – | `responsiblePerson`, `lastProcessingDateTime`, `apiReference`, `internalReference`, `billingInformation` |

> **Important:** The public search filter `statuses` accepts **only**
> `PUBLISHED` and `CANCELLED` — any other value is rejected with `400`,
> because the public projection does not show those statuses.

---

## 2. Prerequisites & Access

- **Public endpoints:** no access request needed, no auth.
- **Authenticated endpoints:** require M2M OAuth2 client credentials via a
  Technical User — the same credential used for announcement import (see
  [Authentication](authentication.md)); no separate credential is needed
  just for search/detail. This mechanism is **planned, not yet live**
  (target: early October 2026).

---

## 3. API Basics

| Item | Value |
|---|---|
| Specification | OpenAPI 3.1.0 (`External_OpenAPI_Spec.json`) |
| Base URL (Production) | `https://epublication.ch` |
| Base URL (Preview) | `https://preview.epublication.ch` |
| Content-Type | `application/json` |
| Character encoding | UTF-8 |
| Pagination | zero-based `page`, `pageSize` (max. 100); the response includes `total` and `currentPage` |
| Sorting | `sort.field` + `sort.direction` (`ASC`/`DESC`); only the fields listed by the respective endpoint are allowed — anything else results in `400` |

> ⚠️ Currently, only a subset of sort fields is supported:
> `publicationNumber`, `publicationDateTime`, `status`.

---

## 4. Searching Announcements

### 4.1 Public Search

```http
POST /public/interface/v1/announcements
Content-Type: application/json

{
  "filter": {
    "gazette": "CANT0002",
    "term": "abc",
    "statuses": ["PUBLISHED"]
  },
  "page": 0,
  "pageSize": 20
}
```

| Item | Value |
|---|---|
| `operationId` | `searchInterfacePublicAnnouncements` |
| Request DTO | `PublicSearchAnnouncementCriteriaDto` |
| Response (`200`) | `ListPageDtoAnnouncementPublicListApiDto` (paginated list of `AnnouncementPublicListApiDto`) |
| Auth | none |

The response returns **only references** (including `publicationNumber`),
not the full content — for details, see
[Section 5](#5-retrieving-announcement-detail).

### 4.2 Authenticated Search

```http
POST /interface/v1/announcements
Content-Type: application/json
Authorization: Bearer <token>

{
  "filter": {
    "gazette": "CANT0002",
    "publishingEntity": "CHE-123.456.789-001"
  },
  "page": 0,
  "pageSize": 20
}
```

| Item | Value |
|---|---|
| `operationId` | `searchInterfaceAnnouncements` |
| Request DTO | `SearchAnnouncementCriteriaDto` |
| Response (`200`) | `ListPageDtoAnnouncementAuthorizedListApiDto` (paginated list of `AnnouncementAuthorizedListApiDto`) |
| Auth | required (see [Authentication](authentication.md)) |

Functionally identical to the public search, but restricted to the
announcements the authenticated consumer is authorized for — possibly
including further statuses beyond just `PUBLISHED`/`CANCELLED`.

### 4.3 Filter Fields (`filter`)

Both search endpoints use structurally identical filter DTOs
(`AnnouncementPublicFilterApiDto` and `AnnouncementFilterApiDto`
respectively). All filters are optional and are combined with AND.

| Field | Type | Status | Description |
|---|---|---|---|
| `gazette` | string | **active** | Restrict results to this gazette, by business ID; matches both the primary and any secondary gazette |
| `publishingEntity` | string | **active** | Restrict results to announcements issued by this publishing entity, by business ID |
| `term` | string | **active** | Free-text search on the announcement content; exactly one term (3–500 characters); separators like spaces/commas are **not** interpreted as delimiters, but become part of the search term |
| `statuses` | string[] | **active** | Public search only allows `PUBLISHED`/`CANCELLED` (otherwise `400`); the authenticated search may allow further statuses |
| `businessCase` | string | ⚠️ MOCK | accepted, but has no effect yet |
| `organisationType` | string | ⚠️ MOCK | accepted, but has no effect yet |
| `publicationDateFrom` / `publicationDateTo` | date | ⚠️ MOCK | accepted, but has no effect yet |
| `cantons` | string[] | ⚠️ MOCK | accepted, but has no effect yet |
| `municipalityIds` | integer[] | ⚠️ MOCK | accepted, but has no effect yet (Swiss BFS municipality numbers) |
| `announcementTypes` | string[] | ⚠️ MOCK | accepted, but has no effect yet |
| `topics` | string[] | ⚠️ MOCK | accepted, but has no effect yet |

> **Practical note:** Currently only `gazette`, `publishingEntity`, `term`,
> and `statuses` are effective. All other filters are accepted by the API
> (no error) but do not (yet) change the result. Third-party applications
> should for now rely only on these four fields when filtering and,
> if needed, restrict further on the client side.

---

## 5. Retrieving Announcement Detail

### 5.1 Public Detail

```http
GET /public/interface/v1/announcements/{publication-number}
```

| Item | Value |
|---|---|
| `operationId` | `getInterfacePublicDetail` |
| Response (`200`) | `AnnouncementPublicDetailApiDto` |
| Auth | none |

### 5.2 Authenticated Detail

```http
GET /interface/v1/announcements/{publication-number}
Authorization: Bearer <token>
```

| Item | Value |
|---|---|
| `operationId` | `getInterfaceAnnouncementByPublicationNumber` |
| Response (`200`) | `AnnouncementAuthorizedDetailApiDto` |
| Auth | required |

### 5.3 Fields in the Detail

Both detail DTOs share the same core; the authorized detail additionally
returns processing/reference/billing information.

| Field | Authorized only? | Description |
|---|---|---|
| `id`, `publicationNumber` | – | unique identifier / publication number |
| `hasPrivacyRestrictions` | – | ⚠️ MOCK flag from the submission |
| `publicationDateTime`, `publicityEndDate` | – | actual/planned publication time or end of public visibility |
| `announcementType` | – | referenced announcement type |
| `publishingEntity` | – | publishing entity |
| `gazette`, `secondaryGazettes` | – | primary/secondary gazettes |
| `legalBasis` | – | legal basis |
| `status` | – | lifecycle status |
| `primaryTopic`, `topics` | – | topics |
| `primaryAffectedCanton`, `affectedCantons` | – | affected cantons |
| `primaryAffectedMunicipality`, `affectedMunicipalities` | – | affected municipalities |
| `languages`, `primaryLanguage` | – | languages of the announcement |
| `title` | – | multilingual title |
| `businessCase` | – | business case |
| `legalBlock` | – | legal notice/contact/deadlines, if applicable |
| `content` | – | content data (elements per language) |
| `links`, `cancellationReason` | – | ⚠️ MOCK fields |
| `responsiblePerson` | ✅ authorized only | responsible person |
| `lastProcessingDateTime` | ✅ authorized only | last processing timestamp |
| `apiReference`, `internalReference` | ✅ authorized only | ⚠️ MOCK, own references from the submission |
| `billingInformation` | ✅ authorized only | billing information |

---

## 6. Downloading Attachments

```http
GET /public/interface/v1/announcements/attachments/{uuid}   # without auth
GET /interface/v1/announcements/attachments/{uuid}          # with auth
```

| Item | Value |
|---|---|
| `operationId` (public) | `downloadAttachmentPublicly` |
| `operationId` (authenticated) | `downloadAttachment` |

> ⚠️ **v1.0 limitation, explicitly documented in the spec:** Attachment
> content is **not yet persisted**. Any valid UUID reference returns the
> same fixed placeholder document — regardless of the content actually
> uploaded. The public endpoint additionally does **not** check whether
> the referencing announcement is even published. Per the spec, the
> contract (shape) is considered final and will not change once real
> storage is introduced — third-party applications can therefore already
> integrate against this endpoint today.

---

## 7. Reference Data Endpoints

These endpoints return the centrally maintained master data used to
resolve references in announcement type and announcement payloads. All of
them are public, unpaginated, and available without auth:

| Endpoint | `operationId` | Purpose |
|---|---|---|
| `GET /public/interface/v1/topics` | `getTopicsViaInterface` | All topics with key, translations, and description — resolves an announcement type's `mandatoryTopics`/`allowedTopics` |
| `GET /public/interface/v1/terms` | `getTermsViaInterface` | All terms with key, `valueType`, and description — the `valueType` determines the structure of `valueTypeConfig` and of the submitted values (see the announcement import documentation, Section 7) |
| `GET /public/interface/v1/organisation-types` | `getOrganisationTypesViaInterface` | All organisation types with key and translations — resolves `authorisedOrganisationTypes` and `publishingEntity.organisationType` |
| `GET /public/interface/v1/enum-values` | `getEnumValuesViaInterface` | All enum values — the options an `ENUM`-typed element offers in its `valueTypeConfig` |
| `GET /public/interface/v1/business-cases` | `getBusinessCasesViaInterface` | All business cases with key and description — resolves an announcement type's `businessCases[].key` |
| `GET /public/interface/v1/announcement-types/{announcementTypeId}` | `getAnnouncementTypeDetailViaInterface` | Complete definition of an announcement type (business cases, content elements, topics, pricing, publication rules) |
| `GET /public/interface/v1/announcements/schema` | `getAnnouncementJsonSchema` | Full JSON schema (Draft 2020-12) of an announcement — usable for client-side validation, code generation, or documentation |

> **Tip:** `GET .../announcements/schema` is well suited to load the
> announcement JSON schema directly into an online validator and check
> your own payloads client-side before submitting — complementing the
> server-side `POST .../announcements/validate` (see the announcement
> import documentation).

---

## 8. Error Handling

| HTTP status | Meaning | Typical cause |
|---|---|---|
| `400` | Invalid request | e.g. an invalid `statuses` value in the public search, unknown `sort.field` |
| `401` | Not authenticated | missing/invalid token on authenticated endpoints |
| `403` | No access | the announcement exists but is not visible to the consumer |
| `404` | Not found | `publication-number` or `announcementTypeId` does not exist |
| `500` | Server error | `ServerErrorResponse` |

---

## 9. Best Practices

- **Search first, then load the detail** — the search endpoints
  deliberately return only references (`publicationNumber`); only load the
  full object on demand via the detail endpoint, to avoid unnecessary data
  volume.
- **Rely only on active filters** — `gazette`, `publishingEntity`, `term`,
  `statuses`; filter client-side for anything marked ⚠️ MOCK until it takes
  effect server-side.
- **Cache reference data, but set a TTL** — topics, terms, organisation
  types, enum values, and business cases rarely change, but should not be
  cached indefinitely without revalidation.
- **Don't use attachment downloads for content verification in v1.0** —
  since a placeholder is always returned currently, a test download says
  nothing about the actual file content.
- **Use pagination consistently** — `pageSize` is capped at 100; iterate
  over `page` for larger result sets rather than trying to load everything
  in one request.

---

## 10. Support & Further Links

- Business background document: [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen) (German)
- API Documentation for Announcement Import – separate document
- [Glossary of the Announcement Standard](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970039873052-Kleines-Glossar-zum-Meldungsstandard) (German)
