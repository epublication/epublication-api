# API Documentation for Announcement Import (Developer Guide for Third-Party Applications)

> **Who is this Information intended for?:** Developers of upstream systems / third-party applications who generate announcements in their own system and submit them for publication to ePublication (Swiss Official Gazettes Portal).

> **Scope:** This document describes the **announcement import** (creating
> and submitting individual announcements). For **obtaining announcements**,
> please refer to [Announcement Export](announcement-export.md). For a
> better understanding of the configuration of announcement types, see
> [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen)
> (German). An announcement can only be submitted for an announcement type
> that has previously been configured and enabled for the respective
> gazette.

---

## Table of Contents

1. [Overview: What is announcement import?](#1-overview-what-is-announcement-import)
2. [Prerequisites & Access](#2-prerequisites--access)
3. [Process Overview](#3-process-overview)
4. [API Basics](#4-api-basics)
5. [Core Resource: Submit an Announcement](#5-core-resource-submit-an-announcement)
6. [Data Model in Detail](#6-data-model-in-detail)
7. [`content` – Values According to the Announcement Type Definition](#7-content--values-according-to-the-announcement-type-definition)
8. [Complete Example](#8-complete-example)
9. [Status & Tracking](#9-status--tracking)
10. [Error Handling & Validation](#10-error-handling--validation)
11. [Best Practices for Upstream Systems](#11-best-practices-for-upstream-systems)
12. [Support & Further Links](#12-support--further-links)

---

## 1. Overview: What is announcement import?

Third-party applications (e.g. commercial registry offices, debt
enforcement/bankruptcy offices, courts, municipal administrations) generate
announcements in their own upstream systems and submit them to ePublication
via the announcement import api. There, the announcement is validated,
formatted, and published in the selected/designated gazette.

Every imported announcement
- is based on **exactly one** previously configured **announcement type**
  (`announcementTypeId`),
- belongs to **exactly one business case** (`businessCase`) of that type,
- contains the **content elements** (`content[].elements[]`) defined for that
  type, whose structure may be defined by the `valueTypeConfig` of the
  respective announcement type (e.g. enum fields),
- is submitted by a **publishing entity** (`publishingEntity`) whose
  organisation type must be permitted for the announcement type.

---

## 2. Prerequisites & Access

- **Authentication:** see the dedicated [Authentication](authentication.md)
  document for the credential type, header format, and key issuance
  process. Submission requires an OAuth2 access token of a **Technical
  User** (client credentials), which a Publisher creates in the portal for
  their Publishing Entity. The production environment is not available
  yet; all examples use the preview environment.

---

## 3. Process Overview

1. **Determine the official gazette, the announcement type and business case** – which
   `announcementTypeId` and which `businessCase.key` matches the matter the
   third-party application wants to report? 
   The `announcementTypeId` consists of the ID of the master type and the Official Gazette ID.
   Announcement types can be searched with `POST /public/interface/v1/announcement-types`
   (see [Announcement Export](announcement-export.md), Section 7.1). Check the field
   `allowAccessViaInterface` of the type definition.
   
   Example: An announcement regarding the opening of bankruptcy proceedings has the number 506. It is published in the SOGC, which has the number FEDE0001. The announcementTypeId is therefore 506-FEDE0001. The corresponding description file is available at
https://preview.epublication.ch/api/management/public/interface/v1/announcement-types/506-FEDE0001

2. **Populate the content elements according to the definition** – for each
   element defined in the announcement type's `elements[]`, supply a
   matching value in `content[].elements[]` and, if necessary, configure them according to to the
   `valueTypeConfig` structure (see [Section 7](#7-content--values-according-to-the-announcement-type-definition)).
   If an element is an attachment, upload the file first and use the returned
   reference (see [Section 5.2](#52-uploading-attachments)).
3. **Submit the announcement** – send the payload to the import endpoint.
4. **Process the response** – evaluate the response (success/validation
   errors); on success (`201`), the response contains the announcement, including its
   `publicationNumber`; store it for tracking (see [Section 5.3](#53-response)).
5. **Track status** (if applicable) – see [Section 9](#9-status--tracking).

```
Third-party application                 ePublication
      │                                        │
      │  1. GET announcement type (reference)  │
      │ ─────────────────────────────────────► │
      │ ◄───────────────────────────────────── │
      │                                        │
      │  2. Assemble announcement              │
      │     (locally, in the third-party app)  │
      │                                        │
      │  3. POST submit announcement           │
      │ ─────────────────────────────────────► │
      │ ◄───────────────────────────────────── │
      │        Confirmation / error            │
```

---

## 4. API Basics

| Item | Value |
|---|---|
| Specification | OpenAPI 3.1.0 |
| Base URL (Production) | `https://epublication.ch` |
| Base URL (Preview) | `https://preview.epublication.ch` |
| Content-Type | `application/json` |
| Character encoding | UTF-8 |
| Multilingual support | Free-text content (e.g. `notice`) is submitted in the languages allowed by the announcement type configuration:

```
"content": [
		{
			"language": "de",
			"elements": []
        },
        {
			"language": "fr",
			"elements": []
        }
    ]
```

### 4.1 Authentication

See [Authentication](authentication.md) for the full picture. In short:
announcement submission (Section 5) requires an **OAuth2 access token**
(client credentials) of a **Technical User**, which a Publisher creates in
the portal for their Publishing Entity. The token is sent as
`Authorization: Bearer <token>` and is valid for 12 hours. The validation
endpoint (`/public/interface/v1/announcements/validate`) uses the
**personal API key** of a portal user instead.

---

## 5. Core Resource: Submit an Announcement

```http
POST /interface/v1/announcements/submission
Content-Type: application/json

{ ... AnnouncementSubmitApiDto ... }
```

| Item | Value |
|---|---|
| `operationId` | `submitAnnouncement` |
| Request DTO | `AnnouncementSubmitApiDto` |
| Success response | `201 Created` |
| Other responses | `400`, `401`, `403`, `404`, `422`, `500` — see [Section 10](#10-error-handling--validation) |

> **Auth note:** This endpoint lives under `/interface/v1/**` (the
> **restricted zone**) and requires the access token of a Technical User —
> see [Authentication](authentication.md).

### 5.1 Business Rules 

The endpoint description has several validation rules that
go beyond the plain field schema:

- The raw request body is validated against `announcement-jsonschema.json`
  before binding (the same schema available at
  `GET /public/interface/v1/announcements/schema`).
- **`legalBlock`** is required if the selected `businessCase` of the
  resolved announcement type has `hasLegalBlock = true`; the number of
  `deadlines[]` must exactly match the business case's configuration, and
  `legalNotice`/`contact`/`deadlines` are required fields within it.
- **`plannedPublicationDate`** is required when `status = SUBMITTED`
  (planned publication date). When `status = PUBLISHED`, **no** date is
  sent — the platform sets `publicationDateTime` itself and returns it in
  the announcement detail. `status` must be `SUBMITTED` or `PUBLISHED`
  (the other enum values, such as `DRAFT` or `CANCELLED`, are not intended
  as submission input).
- Content elements of type `attachmentEmbedded` or `attachmentLinked`
  carry a **platform-relative** `url` (leading slash plus UUID, e.g.
  `/3f2a1c9e-0000-4000-8000-000000000000`); an absolute URL is rejected.
  The reference is the response of the upload endpoint, see
  [Section 5.2](#52-uploading-attachments). The type `attachment` no longer
  exists.
- `label`, `hidden` and `hideLabel` of a content element are **read-only** —
  they come from the platform and the element configuration of the
  announcement type; a value submitted here is accepted but ignored.
  `key`, `type` and `values` are required. The `type` is checked against the
  term of the element; a contradicting type is rejected.
- Two kinds of rule apply, with different status codes: the **schema
  gate** (a missing required field, a wrong shape) answers `400`; the
  **business rules** (`publicityPeriod`, `plannedPublicationDate`,
  `legalBlock`) answer `422`.
- `links` and `cancellationReason` are part of the request contract
  but are **not yet persisted** — a submitted value is accepted and
  discarded.

### 5.2 Uploading attachments

Attachment files are uploaded **before** the announcement is submitted. The
returned reference is then used as `url` of an `attachmentEmbedded` or
`attachmentLinked` content element.

```http
PUT /interface/v1/announcements/attachments/upload
Authorization: Bearer <access-token>
Content-Type: multipart/form-data
```

The body has one part, `file`. The file name is kept and shown with the
attachment. The file may be up to 100 MB; the size and file type rules of
the element are checked when the announcement is submitted, not at upload.

| Status | Meaning |
|---|---|
| `201` | `text/plain`: a new reference of the form `/{uuid}` in lower case. Send it exactly as returned as the `url` of the content element. This endpoint is the only way to get a reference. |
| `400` | no `file` part, an empty file, or a file name that is empty, longer than 255 characters, or too long once URL-encoded |
| `401` | missing or invalid credentials |
| `403` | the credentials may not upload (read-only, or not exactly one publishing entity) |
| `413` | the file is larger than 100 MB |
| `422` | the file is a password-protected PDF (`errorType` `BUSINESS`, `field` `file`, `i18nKey` `announcement.attachment.pdfa.passwordProtected`). Nothing is stored. A password-protected PDF is the only file refused at upload, before the malware check. |
| `503` | uploads are not available at the moment |

**Malware check.** Each file is checked for malware first, which takes a
few seconds. A submission sent before the check is done is refused with
`announcement.attachment.scan.pending`. Query the state until it is `CLEAN`:

```http
GET /interface/v1/announcements/attachments/uploads/{uuid}
Authorization: Bearer <access-token>
```

`{uuid}` is the reference **without** its leading slash. The response is
`{ "state": "...", "reasonKey": "...", "retryable": true }`:

| Field | Meaning |
|---|---|
| `state` | `PENDING`, `CLEAN`, `INFECTED` or `REJECTED` |
| `reasonKey` | why the file cannot be used; absent for `PENDING` and `CLEAN` |
| `retryable` | `true` if uploading the file again may succeed |

Poll every few seconds while the state is `PENDING`. The platform sets no
time limit, so stop after a time of your choice, for example 2 minutes.
`400`: the reference is not a well-formed UUID. `401`/`403`/`503`: as for
the upload. `404` (`announcement.attachment.notFound`): no file with this
reference was uploaded for the caller's publishing entity; a reference of
another publishing entity answers the same way.

**Rules for references**

- Submit within **7 days** of the upload. After that the file is removed.
- A reference belongs to **one** announcement. To use the same file in
  another announcement, upload it again.
- A submission accepts only a reference uploaded for the **same publishing
  entity**. Every Technical User of that publishing entity may use it.

### 5.3 Response

On success the endpoint answers `201 Created` with the announcement in the
same structure as the authenticated detail
(`AnnouncementAuthorizedDetailApiDto`, see
[Announcement Export](announcement-export.md), Section 5.2). It contains the
`publicationNumber`, which identifies the announcement from now on.

---

## 6. Data Model in Detail

- An announcement is submitted as a **complete** payload.
- The referenced `announcementTypeId` and `businessCase.key` must
  correspond to an active announcement type that is enabled for the
  gazette.

### 6.1 Schema: `AnnouncementSubmitApiDto`

Based on the OpenAPI specification. Fields that the schema requires
(`400` if missing) are shown in bold; fields required by a business rule
(`422`) are marked in the description.

| Field | Type | Description |
|---|---|---|
| **`publishingEntity`** | `PublishingEntityRef` | `{ publishingEntityId, uid }`, both required. `uid` must match the pattern `^CHE[1-9][0-9]{8}$` (12 characters) |
| `responsiblePerson` | string | Do not send. A value sent is ignored: the announcement is always filed under the **Client Name** of the submitting Technical User. Returned in the authorized detail only |
| `apiReference` | string | Own reference. Stored and returned unchanged, without platform logic |
| `internalReference` | string | Second own reference. Stored and returned unchanged, visible only in the authorized detail |
| `hasPrivacyRestrictions` | boolean | Whether the announcement contains sensitive personal data. No platform effect yet |
| **`gazette`** | `GazetteRef` | `{ gazetteId }`. The gazette must have `gazetteType=INTERNAL`; an external gazette can only be used as a secondary gazette |
| **`announcementType`** | `AnnouncementTypeRef` | `{ type }` – business ID of the selected announcement type derivate, e.g. `"403-FEDE1000"` |
| **`publicityPeriod`** | integer | Number of days the announcement should remain publicly visible. Business rule (`422`): at least 1 and within the `min`/`max` of the announcement type's `publicityPeriod` |
| **`languages`** | string[] | Languages of the announcement, lower case `de`/`fr`/`it`/`en`, min. 1, max. 4 entries |
| **`primaryLanguage`** | string | Primary language of the announcement (`de`/`fr`/`it`/`en`) |
| **`secondaryGazettes`** | `GazetteRef[]` | Secondary gazettes (required field, but may be empty) |
| **`primaryTopic`** | `TopicRef` | `{ key }` – primary topic, see `GET /public/interface/v1/topics` |
| **`topics`** | `TopicRef[]` | permitted topics, `{ key }` each |
| `primaryAffectedCanton` | string | Canton code (enum of all 26 cantons) |
| `affectedCantons` | string[] | affected cantons |
| `primaryAffectedMunicipality` | `MunicipalityRef` | `{ municipalityId, name? }` – `municipalityId` (Swiss BFS municipality number) is required, `name` optional |
| `affectedMunicipalities` | `MunicipalityRef[]` | affected municipalities |
| **`businessCase`** | `BusinessCaseRef` | `{ key }`, e.g. `"application"`. A business case that the announcement type does not declare is refused with `403` `announcement.submit.businessCaseUnauthorized` |
| `legalBlock` | `LegalBlockApiDto` | Legal notice/contact/deadlines – required (`422`) if the business case is configured with `hasLegalBlock = true` (see [5.1](#51-business-rules)). Shape: `legalNotice` (multilingual), `deadlines[]`, `contact` (multilingual, HTML allowed, e.g. `<br>` for line breaks). The number of `deadlines` must match the business case configuration. Each deadline has `label` (multilingual), `type` and a `value` that depends on the type — see the table below |
| **`content`** | `AnnouncementContentSubmitApiDto[]` | Content data of the announcement (array, see Section 7) |
| `plannedPublicationDate` | date-time | Required (`422`) when `status=SUBMITTED`. Format `T00:00:00` with Swiss timezone (CET/CEST), e.g. `2026-12-01T00:00:00+01:00` |
| **`status`** | string | `SUBMITTED` (submit for processing) or `PUBLISHED` (publish immediately). Other enum values (`DRAFT`, `CANCELLED`, `HIDDEN`, `EXPIRED`, `ARCHIVED`, `STORED`, `DELETED`) are not intended as submission input per the description |
| `links` | string[] | Publication numbers of linked announcements. Not yet persisted: accepted and dropped |
| `cancellationReason` | `MultilingualTextDto` | Reason for cancellation. Not yet persisted: accepted and dropped |

**Deadline types** (`legalBlock.deadlines[].type`)

| `type` | `value` |
|---|---|
| `DATE` | a date |
| `DURATION` | `{ "from": "...", "to": "..." }` |
| `DAYS` | an integer ≥ 1 |
| `MONTHS` | an integer ≥ 1 |
| `NOINFO` | absent |

> **Not part of the submission contract:** `title`, `legalBasis` and
> `publicityEndDate` are not fields of the submission request. If they are
> sent, they are currently ignored. Do not rely on this; leave them out.

> **Reference objects:** The references (`announcementType`,
> `publishingEntity`, `gazette`, `businessCase`, `primaryTopic`/`topics`,
> municipalities) consist only of the identifying fields shown in the table
> above. Display names (`name`, `gazetteName`, …) are not part of the
> contract and the platform sets them.

> **`responsiblePerson`:** The field is not evaluated on submission. The
> platform files the announcement under the Client Name of the Technical
> User that submits it, so choose a meaningful Client Name when creating the
> Technical User (see [Authentication](authentication.md)).

---

## 7. `content` – Values According to the Announcement Type Definition

> `content` is an **array with one entry per language** declared in
> `languages`; each entry has a `language` code and an `elements` array.
> Every element carries its `key`, its `type` (the `Term` value type) and a
> `values` array — **always an array**, even for single scalar values.
> `label`, `hidden` and `hideLabel` are set by the platform; a value sent
> here is ignored (see [5.1](#51-business-rules)).

```json
{
  "content": [
    {
      "language": "de",
      "elements": [
        {
          "key": "<element key from the announcement type definition>",
          "label": "<display label>",
          "type": "<Term type, e.g. enum / textarea / legalPerson / string / date>",
          "hidden": false,
          "hideLabel": false,
          "values": [ "..." ]
        }
      ]
    }
  ]
}
```

The structure of `content` is **not generic** beyond this envelope — the
set of `elements` and each one's expected `values` shape follows directly
from the `elements[]` of the selected announcement type: for each element
defined there (`key`, `valueTypeConfig`), the third-party application must
supply a matching value whose shape fits the respective `Term` type. The
third-party application must therefore query the announcement type in
advance (see Section 3) to know which elements are expected, in which
structure.

Patterns already confirmed:

### 7.1 `legalPerson` (e.g. `primaryEntityLegalPerson`)

`values` is an array containing one object:

```json
{
  "key": "primaryEntityLegalPerson",
  "label": "Betroffene Organisation",
  "type": "legalPerson",
  "hidden": false,
  "hideLabel": false,
  "values": [
    {
      "uid": "CHE123456789",
      "name": "Sample Company Ltd",
      "legalForm": "0106",
      "address": {
        "addressLine1": "",
        "street": "Musterstrasse",
        "houseNumber": "1",
        "town": "Bern",
        "swissZipCode": "3000"
      }
    }
  ]
}
```

> **Address fields:** `addressLine1` (separate additional line, may be
> empty), `street` (without the house number), `houseNumber` (separate),
> `town`, and `swissZipCode`. No `country` field has been observed;
> whether it's needed/accepted for non-Swiss addresses is unconfirmed.

### 7.2 `textarea` (e.g. `notice`)

Free-text content of the actual publication, as HTML. Still wrapped in the
same envelope; `values` contains one HTML string:

```json
{
  "key": "notice",
  "label": "Angaben zur Bewilligung",
  "type": "textarea",
  "hidden": false,
  "hideLabel": false,
  "values": [
    "<p>Publication text of the announcement ...</p>"
  ]
}
```

### 7.3 `enum` elements

For elements whose announcement type definition has an `ENUM`
`valueTypeConfig`, `values` contains the **display text of the selected
option**, in the language of the `content` entry. The element is identified
by its `key`; the option is identified by its text.

```json
{
  "key": "archivingType",
  "type": "enum",
  "values": [
    "Die publizierende Stelle erachtet die Meldung nicht als archivierungswürdig."
  ]
}
```

The available options are listed in the `valueTypeConfig` of the element in
the announcement type definition (`GET /public/interface/v1/announcement-types/{id}`).

### 7.4 `person` (e.g. `primaryEntityPerson`)

A `person` element carries a `personType` and the matching person object.
Confirmed for a legal person, here with a foreign address given as free
text in `additionalInformation` (HTML, `<br>` for line breaks):

```json
{
  "key": "primaryEntityPerson",
  "type": "person",
  "values": [
    {
      "personType": "LEGAL",
      "legalPerson": {
        "name": "Foreign Sample Company Ltd.",
        "legalForm": "0441",
        "additionalInformation": "123 Baker Street<br>LONDON<br>W1U 6WG<br>UNITED KINGDOM"
      }
    }
  ]
}
```

### 7.5 `url`

`values` contains one URL string:

```json
{
  "key": "url",
  "type": "url",
  "values": [ "https://example.org/register/entry/123" ]
}
```

### 7.6 `ADDRESS` elements

For elements with `{"enableAddress": true}`, an address object is expected
(structure analogous to 7.1); with `{"enableAddress": false}`, address
capture is omitted for this element. Not yet independently confirmed
against a real request.

> **Important:** The structural pattern in this section (envelope,
> per-language array, `values` arrays) is confirmed from one real, working
> example (announcement type `403-FEDE1000`). Field-level specifics for
> other `Term` types (`string`, `date`, `PERSON`, …) are
> **not yet independently verified** — please check against the actual
> `valueTypeConfig` definition of the respective type before relying on
> them. Attachment elements have the types `attachmentEmbedded` and
> `attachmentLinked`; their `url` is the reference returned by the upload
> (see [Section 5.2](#52-uploading-attachments)).

---

## 8. Complete Example

> A working request for announcement type **`403-FEDE1000`**
> (Arbeitszeitbewilligung / work permit), business case **`application`**,
> against the `FEDE1000` test gazette. `publishingEntityId` and `uid` are
> sample values.
>
> The `enum` element (`businessCaseType`) carries the display text of the
> selected option, see [Section 7.3](#73-enum-elements).

```json{
  "hasPrivacyRestrictions": false,
  "plannedPublicationDate": "2026-12-01T00:00:00+01:00",
  "publicityPeriod": 91,
  "announcementType": {
    "type": "403-FEDE1000"
  },
  "publishingEntity": {
    "publishingEntityId": "CHE-123.456.789-001",
    "uid": "CHE123456789"
  },
  "gazette": {
    "gazetteId": "FEDE1000"
  },
  "secondaryGazettes": [],
  "status": "SUBMITTED",
  "primaryTopic": {
    "key": "employment"
  },
  "topics": [
    {
      "key": "employment"
    }
  ],
  "primaryAffectedCanton": "ZH",
  "affectedCantons": [
    "ZH",
    "AG",
    "SH"
  ],
  "languages": [
    "de"
  ],
  "primaryLanguage": "de",
  "businessCase": {
    "key": "application"
  },
  "legalBlock": {
    "legalNotice": {
      "de": "Gegen diese Verfügung kann innert 30 Tagen nach Veröffentlichung das nächsthöhere Rechtsmittel ergriffen werden."
    },
    "deadlines": [
      {
        "label": {
          "de": "Frist"
        },
        "type": "DAYS",
        "value": 30
      }
    ],
    "contact": {
      "de": "Sample Amt, Musterabteilung<br>Musterstrasse 1<br>3000 Bern"
    }
  },
  "content": [
    {
      "language": "de",
      "elements": [
        {
          "key": "businessCaseType",
          "type": "enum",
          "values": [
            "Zusammengesetzten ununterbrochenen Betrieb"
          ]
        },
        {
          "key": "primaryEntityLegalPerson",
          "type": "legalPerson",
          "values": [
            {
              "uid": "CHE123456789",
              "name": "Sample Company Ltd",
              "legalForm": "0106",
              "address": {
                "addressLine1": "",
                "street": "Musterstrasse",
                "houseNumber": "1",
                "town": "Bern",
                "swissZipCode": "3000"
              }
            }
          ]
        },
        {
          "key": "notice",
          "type": "textarea",
          "values": [
            "<p>Sample publication text ...</p>"
          ]
        }
      ]
    }
  ]
}
```

> **Note:** `responsiblePerson` is intentionally **omitted** from this
> example — it is filed under the Client Name of the submitting Technical
> User.

---

## 9. Status & Tracking

A successful submission (`201`) returns the announcement, including its
`publicationNumber` and `status` (see [Section 5.3](#53-response)). With
`status = PUBLISHED` the announcement is published immediately; with
`SUBMITTED` it is submitted for processing for the `plannedPublicationDate`.

To follow an announcement afterwards, read it by its publication number with
the authenticated detail (`GET /interface/v1/announcements/{publication-number}`)
or search with `lastProcessingDateFrom` (see
[Announcement Export](announcement-export.md)). Notifications about status
changes (webhook/callback) are not documented; poll these endpoints.

---

## 10. Error Handling & Validation

Errors are returned with a status code and, for business errors, an error
object with `errorType`, `field`, `i18nKey` and `errorMessage`. Only the
**first** problem found is reported, not a collected list.

| HTTP status | Meaning | Typical cause |
|---|---|---|
| `400` | Data error / schema gate | a required field is missing (e.g. `content`), a wrong shape, or `content` does not match the element's term |
| `401` | Not authenticated | credentials missing, or a bearer token that cannot be decoded. Checked before any authorization rule runs |
| `403` | Not authorized | `announcement.submit.gazetteUnauthorized`, `announcement.submit.announcementTypeUnauthorized`, `announcement.submit.languagesUnauthorized`, `announcement.submit.businessCaseUnauthorized`, or the plain refusal of the role. Unlike the field checks, this family reports **one** problem — the first found |
| `404` | Not found | the addressed resource does not exist |
| `422` | Business rule violated | `publicityPeriod` outside the type's `min`/`max`, `plannedPublicationDate` missing for `SUBMITTED`, `legalBlock` missing or with the wrong number of deadlines |

---

## 11. Best Practices for Upstream Systems

- **Cache the announcement type definition, but refresh it regularly** –
  the structure of `elements[]`/`valueTypeConfig` can change, rigid caching
  without refresh leads to validation errors.
- **Client-side pre-validation** – before submitting, check that all
  `mandatory: true` elements of the announcement type are populated.
- **Handle unknown `valueTypeConfig` structures tolerantly** – if the
  third-party application works generically against multiple announcement
  types, key off the element's `Term` value rather than specific JSON
  fields.
- **Upload attachments early and check the scan state** — upload files
  before assembling the submission, wait for `CLEAN`, and submit within 7
  days of the upload.
- **Reuse nothing across announcements** — an attachment reference belongs
  to one announcement; upload the file again for another one.

---

## 12. Support & Further Links

- [Runnable Bruno examples](../bruno/README.md) — try these requests directly
- Business background document: [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen) (German)
- [Glossary of the Announcement Standard](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970039873052-Kleines-Glossar-zum-Meldungsstandard) (German)
