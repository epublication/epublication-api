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
- contains the **content elements** (`content.elements`) defined for that
  type, whose structure may be defined by the `valueTypeConfig` of the
  respective announcement type (e.g. enum fields),
- is submitted by a **publishing entity** (`publishingEntity`) whose
  organisation type must be permitted for the announcement type.

---

## 2. Prerequisites & Access

- **Authentication:** see the dedicated [Authentication](authentication.md)
  document for the credential type, header format, and key issuance
  process. Submission requires M2M OAuth2 client credentials via a
  Technical User — confirmed, but **not yet live** (planned for early
  October 2026).

---

## 3. Process Overview

1. **Determine the official gazette, the announcement type and business case** – which
   `announcementTypeId` and which `businessCase.key` matches the matter the
   third-party application wants to report? 
   The `announcementTypeId` consists of the ID of the master type and the Official Gazette ID.
   
   Example: An announcement regarding the opening of bankruptcy proceedings has the number 506. It is published in the SOGC, which has the number FEDE0001. The announcementTypeId is therefore 506-FEDE0001. The corresponding description file is available at
https://preview.epublication.ch/api/management/public/interface/v1/announcement-types/506-FEDE0001

2. **Populate the content elements according to the definition** – for each
   element defined in the announcement type's `elements[]`, supply a
   matching value in `content.elements` and, if necessary, configure them according to to the
   `valueTypeConfig` structure (see [Section 7](#7-content--values-according-to-the-announcement-type-definition)).
3. **Submit the announcement** – send the payload to the import endpoint.
4. **Process the response** – evaluate the response (success/validation
   errors); on success, store the `publicationNumber` for tracking.
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
announcement submission (Section 5) requires **M2M OAuth2 client
credentials** — confirmed. The credentials are obtained via a **Technical
User**, self-service created by a Publisher for their Publishing Entity.
This mechanism is **planned, not yet live** (target: early October 2026).
Until it ships, the credential third-party applications should use today
for submission is not yet confirmed.

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
| Other responses | `400`, `403`, `422`, `401`, `500` |

> ⚠️ **Auth note:** This endpoint lives under `/interface/v1/**` (the
> **restricted zone**) and requires M2M OAuth2 client credentials — see
> [Authentication](authentication.md) for the confirmed mechanism
> (Technical Users), which is planned but **not yet live**.

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
- Content elements of type `attachment` require a **platform-relative**
  `url` (leading slash plus UUID, e.g.
  `/3f2a1c9e-0000-4000-8000-000000000000`); an absolute URL is rejected.
  The reference comes from `PUT /interface/v1/announcements/attachments/upload`.
  Note for v1.0: attachment content is not persisted yet — a download
  currently returns a fixed placeholder document instead of the uploaded
  file.
- `hidden` and `hideLabel` of a content element are **read-only** — they
  come from the element configuration of the announcement type; a value
  submitted here is accepted but ignored.
- `links` and `cancellationReason` are part of the v1.0 request contract
  but are **not yet persisted** — a submitted value is accepted and
  discarded.

---

## 6. Data Model in Detail

- An announcement is submitted as a **complete** payload.
- The referenced `announcementTypeId` and `businessCase.key` must
  correspond to an active announcement type that is enabled for the
  gazette.

### 6.1 Schema: `AnnouncementSubmitApiDto`

Confirmed from `External_OpenAPI_Spec.json`. Required fields are shown in
bold.

| Field | Type | Description |
|---|---|---|
| **`publishingEntity`** | `PublishingEntityRef` | Per the OpenAPI ref schema: `{ publishingEntityId, uid }`, both required, `uid` must match the pattern `^CHE[1-9][0-9]{8}$` (12 characters). **A confirmed real request also includes** `organisationType` (`{ key, name }`), `publishingEntityName`, and `publishingEntityNameAddition` as embedded display fields — see the note below |
| `responsiblePerson` | string | Name of the responsible person; returned in the authorized detail (the public detail does not show it). **Derived automatically from the submitting Technical User's Client Name** — see the note below. Not required in the request body. |
| `apiReference` | string | ⚠️ **MOCK** – own reference, stored/returned unchanged, but without platform logic (yet) |
| `internalReference` | string | ⚠️ **MOCK** – second own reference, visible only in the authorized detail |
| `hasPrivacyRestrictions` | boolean | ⚠️ **MOCK** – whether the announcement contains sensitive personal data |
| **`gazette`** | `GazetteRef` | Per the OpenAPI ref schema: `{ gazetteId }`; must have `gazetteType=INTERNAL`. An external gazette can only be used as a secondary gazette. **A confirmed real request also includes** `gazetteCategory` and `gazetteName` — see the note below |
| **`announcementType`** | `AnnouncementTypeRef` | Per the OpenAPI ref schema: `{ type }` – business ID of the selected announcement type derivation, e.g. `"403-FEDE1000"`. **A confirmed real request also includes** an embedded `name` (multilingual) — see the note below |
| **`publicityPeriod`** | integer | Number of days the announcement should remain publicly visible, sent on submission |
| `publicityEndDate` | date | A confirmed real request sends this field *alongside* `publicityPeriod` on submission. Which of the two is authoritative if they conflict is unconfirmed |
| **`languages`** | string[] | Languages supported by the announcement, `de`/`fr`/`it`/`en`, min. 1, max. 4 entries |
| **`primaryLanguage`** | string | Primary language of the announcement (`de`/`fr`/`it`/`en`) |
| `title` | `MultilingualTextDto` | A confirmed real request sends a multilingual `title` on submission (e.g. `{ "de": "..." }`). |
| `legalBasis` | `MultilingualTextDto` | A confirmed real request sends this on submission. |
| **`secondaryGazettes`** | `GazetteRef[]` | Secondary gazettes (required field, but may be empty) |
| **`primaryTopic`** | `TopicRef` | `{ key }` – primary topic |
| **`topics`** | `TopicRef[]` | permitted topics |
| `primaryAffectedCanton` | string | Canton code (enum of all 26 cantons) |
| `affectedCantons` | string[] | affected cantons |
| `primaryAffectedMunicipality` | `MunicipalityRef` | `{ municipalityId, name? }` – resolved via the Swiss BFS municipality number |
| `affectedMunicipalities` | `MunicipalityRef[]` | affected municipalities |
| **`businessCase`** | `BusinessCaseRef` | Per the OpenAPI ref schema: `{ key }`, e.g. `"application"`. **A confirmed real request also includes** an embedded `name` (multilingual) |
| `legalBlock` | `LegalBlockApiDto` | Legal notice/contact/deadlines – required if the business case is configured with `hasLegalBlock = true` (see [5.1](#51-business-rules-from-the-spec-description)). Confirmed shape: `legalNotice` (multilingual), `deadlines[]` (`{ label, type, value }`), `contact` (multilingual, HTML allowed, e.g. `<br>` for line breaks) |
| **`content`** | `AnnouncementContentSubmitApiDto[]` | Content data of the announcement (array, see Section 7) |
| `plannedPublicationDate` | date-time | Required when `status=SUBMITTED`. Format `T00:00:00` with Swiss timezone (CET/CEST), e.g. `2026-01-01T00:00:00+01:00` |
| **`status`** | string | `SUBMITTED` (submit for processing) or `PUBLISHED` (publish immediately). Other enum values (`DRAFT`, `CANCELLED`, `HIDDEN`, `EXPIRED`, `ARCHIVED`, `STORED`, `DELETED`) are not intended as submission input per the description |
| `links` | string[] | ⚠️ **MOCK** – publication numbers of linked announcements, not yet persisted |
| `cancellationReason` | `MultilingualTextDto` | ⚠️ **MOCK** – reason for cancellation, not yet persisted |

> **Note:** Fields marked ⚠️ **MOCK** are, per the spec description, part
> of the v1.0 contract but have no platform effect yet — the value is
> accepted/stored or returned, but does not trigger any behavior yet. This
> is different from an open/unconfirmed item: these fields are
> deliberately specified this way, not unknown.

> **Reference objects are richer than the bare OpenAPI ref schemas
> suggest:** The OpenAPI spec's `PublishingEntityRef`/`GazetteRef`/
> `AnnouncementTypeRef`/`BusinessCaseRef` schemas define only the minimal
> identifying fields (e.g. `{ type }`, `{ gazetteId }`). However, a
> confirmed real, working request (from a Bruno example collection) embeds
> full display objects instead — e.g. `gazette` includes `gazetteCategory`
> and `gazetteName`, `publishingEntity` includes `organisationType`
> (itself `{ key, name }`) plus `publishingEntityName`/
> `publishingEntityNameAddition`, and `announcementType`/`businessCase`
> both include an embedded multilingual `name`. Whether the minimal
> ref-only form is also accepted (i.e. whether the extra fields are
> optional/ignored), or whether the full embedded form is actually
> required, is unconfirmed. Until confirmed, prefer mirroring the full
> form shown in [Section 8](#8-complete-example).

> **`responsiblePerson`:** Per business rule BR-009 of the Technical User
> specification (see [Authentication](authentication.md)),
> `responsiblePerson` is derived automatically from the submitting
> Technical User's Client Name once an announcement is submitted through
> the external API. The submitting system does **not** need to send this
> field. Since this is tied to the Technical User mechanism, which is
> **planned but not yet live** (target: early October 2026), treat this as
> the target-state behavior rather than something that can be relied on
> today.

---

## 7. `content` – Values According to the Announcement Type Definition

> `content` is an **array with one entry per language** declared in
> `languages`; each entry has a `language` code and an `elements` array.
> Every element carries its `key`, a display `label`, its `type` (the
> `Term` value type), `hidden`/`hideLabel` flags (read-only — see
> [5.1](#51-business-rules-from-the-spec-description)), and a `values`
> array — **always an array**, even for single scalar values.

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
`valueTypeConfig` (see the Announcement Type documentation, Section 7.1),
a confirmed real request supplies the **display text of the selected
option**, not a machine key:

```json
{
  "key": "businessCaseType",
  "label": "Art der Bewilligung",
  "type": "enum",
  "hidden": false,
  "hideLabel": false,
  "values": [
    "Zusammengesetzten ununterbrochenen Betrieb"
  ]
}
```

> A confirmed real example sends the **rendered text** of the option, not
> a machine key. Whether a machine key is also accepted, or whether the
> display text is the only accepted form — and whether that text must
> match exactly (including language) or is matched loosely — is
> unconfirmed.

### 7.4 `ADDRESS` elements

For elements with `{"enableAddress": true}`, an address object is expected
(structure analogous to 7.1); with `{"enableAddress": false}`, address
capture is omitted for this element. Not yet independently confirmed
against a real request.

> **Important:** The structural pattern in this section (envelope,
> per-language array, `values` arrays) is confirmed from one real, working
> example (announcement type `403-FEDE1000`). Field-level specifics for
> other `Term` types (`string`, `date`, `PERSON`, `attachment`, …) are
> **not yet independently verified** — please check against the actual
> `valueTypeConfig` definition of the respective type before relying on
> them.

---

## 8. Complete Example

> A confirmed real, working request for announcement type
> **`403-FEDE1000`** (Arbeitszeitbewilligung / work permit), business case
> **`application`**, against the `FEDE1000` test gazette —
> `publishingEntityId`/`uid` are replaced by this project's standing
> placeholder values.

```json
{
  "hasPrivacyRestrictions": false,
  "plannedPublicationDate": "2026-09-03T00:00:00+02:00",
  "publicityEndDate": "2026-11-12",
  "publicityPeriod": 91,
  "announcementType": {
    "type": "403-FEDE1000",
    "name": {
      "de": "Arbeitszeitbewilligung",
      "fr": "Autorisation de travail",
      "it": "Autorizzazione all'orario di lavoro",
      "en": "Work permit"
    }
  },
  "publishingEntity": {
    "publishingEntityId": "CHE-123.456.789-001",
    "uid": "CHE123456789",
    "organisationType": {
      "key": "general",
      "name": { "de": "Alle Meldungstypen" }
    },
    "publishingEntityName": { "de": "Sample Publishing Entity" },
    "publishingEntityNameAddition": { "de": "Test" }
  },
  "gazette": {
    "gazetteId": "FEDE1000",
    "gazetteCategory": "FEDERAL",
    "gazetteName": { "de": "Test-Amtsblatt (alle Standard-Meldungstypen)" }
  },
  "secondaryGazettes": [],
  "legalBasis": {
    "de": "Es gibt keine allgemeingültige Rechtsgrundlage."
  },
  "status": "SUBMITTED",
  "primaryTopic": {
    "key": "employment",
    "name": { "de": "Arbeit, Bildung und Beschaffung" }
  },
  "topics": [
    { "key": "employment", "name": { "de": "Arbeit, Bildung und Beschaffung" } }
  ],
  "primaryAffectedCanton": "ZH",
  "affectedCantons": ["ZH", "AG", "SH"],
  "languages": ["de"],
  "primaryLanguage": "de",
  "title": {
    "de": "Bewilligungsgesuch, Nachtarbeit, Sample Company Ltd, Muri bei Bern"
  },
  "businessCase": {
    "key": "application",
    "name": { "de": "Bewilligungsgesuch" }
  },
  "legalBlock": {
    "legalNotice": {
      "de": "Gegen diese Verfügung kann innert 30 Tagen nach Veröffentlichung das nächsthöhere Rechtsmittel ergriffen werden."
    },
    "deadlines": [
      { "label": { "de": "Frist" }, "type": "DAYS", "value": 30 }
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
          "label": "Art der Bewilligung",
          "type": "enum",
          "hidden": false,
          "hideLabel": false,
          "values": ["Zusammengesetzten ununterbrochenen Betrieb"]
        },
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
        },
        {
          "key": "notice",
          "label": "Angaben zur Bewilligung",
          "type": "textarea",
          "hidden": false,
          "hideLabel": false,
          "values": ["<p>Sample publication text ...</p>"]
        }
      ]
    }
  ]
}
```

> **Note:** `responsiblePerson` is intentionally **omitted** from this
> example — per the note above, it's derived automatically from the
> submitting Technical User's Client Name and does not need to be sent.
>
> Whether the minimal ref-only form (e.g.
> `{ "gazette": { "gazetteId": "FEDE1000" } }` without `gazetteCategory`/
> `gazetteName`) is also accepted, or whether the fuller embedded form
> shown here is required, is unconfirmed — see
> [Section 6.1](#61-schema-announcementsubmitapidto).

---

## 9. Status & Tracking

Whether the import endpoint synchronously returns an announcement
ID/reference number, whether there is a status lifecycle beyond
`SUBMITTED`/`PUBLISHED` with a corresponding query endpoint, and whether
third-party applications are notified of status changes (webhook/callback)
or need to poll — none of this is documented here yet.

---

## 10. Error Handling & Validation

The exact error format (status codes, error object structure, field-level
validation errors — especially for mismatches between the submitted
`content` and the expected `valueTypeConfig` structure of the
announcement type) is not documented here yet.

| HTTP status | Meaning | Typical cause |
|---|---|---|
| `400` | not yet documented | e.g. `content` does not match the announcement type's `valueTypeConfig`; a mandatory element is missing |
| `401` / `403` | not yet documented | Auth missing/expired, or `publishingEntity` not authorised for the announcement type |
| `404` | not yet documented | `announcementTypeId` or `businessCase.key` does not exist |
| `422` | not yet documented | Business validation failed (e.g. `mandatoryTopics` not covered, publicity period outside `min`/`max`) |

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
  fields (analogous to the recommendation in the Announcement Type
  documentation).

---

## 12. Support & Further Links

- [Runnable Bruno examples](../bruno/README.md) — try these requests directly
- Business background document: [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen) (German)
- API Documentation for Announcement Types (configuration of the templates) – separate document
- [Glossary of the Announcement Standard](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970039873052-Kleines-Glossar-zum-Meldungsstandard) (German)
