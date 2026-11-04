# ePublication – API Documentation for Announcement Export (Developer Guide)

> **Audience:** Both data consumers using the public view (e.g. media,
> general research tools) and third-party applications (upstream
> systems) using the authenticated view that want to retrieve published announcements from ePublication
> (Swiss Official Gazettes Portal) and process them further.
>
> **Scope:** This document describes **announcement export** — searching
> and retrieving already-published (or, for the respective consumer,
> visible) announcements. For submitting new announcements, see the
> separate *"API Documentation for Announcement Import"*.

---

<a id="fair-use-policy"></a>
**Fair Use Policy**

As a guideline, a single API consumer should not retrieve more than the number of new announcements published per day system-wide (roughly 2,000–3,000) — with typical usage (a search followed by one detail request per announcement), that corresponds to roughly 2,000–3,000 requests per day.

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
| Credential | Personal API key | Technical User (OAuth2 access token) |
| Visible announcements | only publicly visible ones, with status `PUBLISHED` or `CANCELLED` | all announcements the authenticated consumer is authorized for, in any status except `DELETED` |
| Additional fields in the detail | – | `plannedPublicationDate`, `responsiblePerson`, `lastProcessingDateTime`, `apiReference`, `internalReference`, `billingInformation` |
| Search filters | `gazette`, `publishingEntity`, `term`, `language`, `status`, `announcementTypes`, plus `organisationType`, `topics`, `cantons`, `municipalityIds`, `persons`, `enumValues`, `publicationDateFrom/To` | `gazette`, `publishingEntity`, `term`, `language`, `status`, `announcementTypes`, `lastProcessingDateFrom/To` |

> **Important:** The public search filter `status` accepts **only**
> `PUBLISHED` and `CANCELLED` — any other value is rejected with `400`,
> because the public projection does not show those statuses.

---

## 2. Prerequisites & Access

- **Public endpoints:** require the **personal API key** of a registered
  portal user, obtained in the personal user account (one key per user).
  See [Authentication](authentication.md).
- **Authenticated endpoints:** require the access token of a **Technical
  User** (OAuth2 client credentials) — the same credential used for
  announcement import; no separate credential is needed just for
  search/detail. See [Authentication](authentication.md).
- Only the preview environment is available at the moment.

---

## 3. API Basics

| Item | Value |
|---|---|
| Specification | OpenAPI 3.1.0 |
| Base URL (Production) | `https://epublication.ch` |
| Base URL (Preview) | `https://preview.epublication.ch` |
| Content-Type | `application/json` |
| Character encoding | UTF-8 |
| Pagination | zero-based `page`, `pageSize` (max. 100); the response includes `total` and `currentPage` |
| Sorting | `sort.field` + `sort.direction` (`ASC`/`DESC`); only the fields listed by the respective endpoint are allowed — anything else results in `400` |

> Only a subset of sort fields is supported. For announcement searches:
> `publicationNumber`, `publicationDateTime`, `status`. For the
> announcement type search: `announcementTypeId`, `version`.

---

## 4. Searching Announcements

### 4.1 Public Search

```http
POST /public/interface/v1/announcements
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "filter": {
    "gazette": "CANT0002",
    "term": "abc",
    "status": "PUBLISHED"
  },
  "page": 0,
  "pageSize": 20,
  "sort": { "field": "publicationDateTime", "direction": "DESC" }
}
```

| Item | Value |
|---|---|
| `operationId` | `searchInterfacePublicAnnouncements` |
| Request DTO | `PublicSearchAnnouncementCriteriaDto` |
| Response (`200`) | `ListPageDtoAnnouncementPublicListApiDto` (paginated list of `AnnouncementPublicListApiDto`) |
| Auth | personal API key |

The response (`items`, `total`, `currentPage`) returns **only references**,
not the full content. Each item contains `publicationNumber`,
`announcementType` (`type`, `version`, `name`), `publicationDateTime`,
`title`, `status`, `gazette` and `secondaryGazettes` (`gazetteId`,
`gazetteCategory`, `gazetteName`). For the full announcement, see
[Section 5](#5-retrieving-announcement-detail).

### 4.2 Authenticated Search

```http
POST /interface/v1/announcements
Content-Type: application/json
Authorization: Bearer <access-token>

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
| Auth | Technical User (see [Authentication](authentication.md)) |

The authenticated search is restricted to the announcements the
authenticated consumer is authorized for, and accepts every status except
`DELETED`. It takes a **smaller filter set** than the public search (see
[Section 4.3](#43-filter-fields-filter)). The items have the same fields as
in the public search; the gazettes additionally carry `gazetteType`.

### 4.3 Filter Fields (`filter`)

All filters are optional. Filters are combined with **AND** — naming
several narrows the result to announcements matching all of them. The one
exception: `cantons` and `municipalityIds` form **one geographic filter**
whose parts are combined with **OR**, so naming both returns the
announcements matching either.

**Public search** (`POST /public/interface/v1/announcements`)

| Field | Type | Description |
|---|---|---|
| `gazette` | string | Business ID of a gazette, e.g. `CANT0002`; matches the primary and any secondary gazette |
| `publishingEntity` | string | Business ID of the publishing entity, e.g. `CHE-123.456.789-001` |
| `term` | string | Free-text search on the announcement content; exactly one term of 3–500 characters. Separators such as spaces or commas are **not** interpreted as delimiters but become part of the term |
| `language` | string | Language code, e.g. `fr`; lower and upper case are both accepted |
| `status` | string | `PUBLISHED` or `CANCELLED` only |
| `organisationType` | string | Key of one organisation type (max. 100 characters), e.g. `OT01` — see [Section 7](#7-reference-data-endpoints) |
| `topics` | string[] | Topic keys, max. 100 |
| `cantons` | string[] | Canton codes in upper case, max. 26 |
| `municipalityIds` | integer[] | Swiss BFS municipality numbers, max. 100 |
| `announcementTypes` | object[] | Max. 100 entries, see [Announcement type filter](#announcement-type-filter) |
| `persons` | string[] | Max. 4 of `NATURAL`, `LEGAL:0106`, `LEGAL:0107`, `LEGAL:OTHER`, see [Person and detail filters](#person-and-detail-filters) |
| `enumValues` | string[] | Max. 100 entries of the form `elementKey:valueKey`, e.g. `publicationArea:newConstruction` |
| `publicationDateFrom` / `publicationDateTo` | date | `yyyy-MM-dd`, applied to `publicationDateTime`, see [Date filters](#date-filters) |

**Authenticated search** (`POST /interface/v1/announcements`)

| Field | Type | Description |
|---|---|---|
| `gazette` | string | as above |
| `publishingEntity` | string | as above |
| `term` | string | as above |
| `language` | string | as above |
| `status` | string | Any status **except** `DELETED`. `DELETED` is rejected with `400` rather than answered with an empty page, which would read as "there are none in this state" |
| `announcementTypes` | object[] | as above |
| `lastProcessingDateFrom` / `lastProcessingDateTo` | date | `yyyy-MM-dd`, applied to `lastProcessingDateTime` ("Last modified" in the portal), see [Date filters](#date-filters) |

The filters that exist only in the public search (`organisationType`,
`topics`, `cantons`, `municipalityIds`, `persons`, `enumValues`) are
**accepted and ignored** by the authenticated search: HTTP `200`, with the
result as if they had been left out. They are not refused with `400`.

> **Breaking change for existing integrations:** `publicationDateFrom` and
> `publicationDateTo` do not apply to the authenticated search. Earlier
> versions accepted them without applying them. Use
> `lastProcessingDateFrom`/`lastProcessingDateTo` instead. The old names
> are now unknown fields: accepted and ignored, HTTP `200`, as before.

#### Announcement type filter

Each entry of `announcementTypes` has the form
`{ "type": "SR101", "businessCases": ["..."] }`; `businessCases` is
optional (max. 50) and may be absent or empty.

- `type` is either a **master key** (e.g. `SR101`) or a **gazette's own
  key** (e.g. `SR101-CANT0002`). The search accepts either and does not
  check which kind it is.
- A master key finds the announcements of every gazette's type built on
  that master. With `gazette` or `publishingEntity` set, the result is
  narrowed to that gazette's or that entity's announcements.
- A gazette's own key finds only announcements whose **primary** gazette
  uses that type. An announcement that has the gazette only as a
  secondary gazette is not found.

#### Person and detail filters

- `persons`: `NATURAL` is a natural person. `LEGAL:0106` (Aktiengesellschaft),
  `LEGAL:0107` (GmbH) and `LEGAL:OTHER` (any other legal form, or none)
  are legal persons. **For every legal person, send all three `LEGAL:*`
  tokens.** An announcement matches when it names **any** of the given
  persons.
- `enumValues`: values of the **same** element are combined with OR;
  values of **different** elements must all match.
- A `persons` value other than the four tokens, or an `enumValues` entry
  that does not match `\w+:\w+`, is `400 validationFailed`; the position
  is given in `args[0].key`, e.g. `filter.persons[0]`. A wrong shape (a
  string instead of a list, an object instead of a string) is `400`
  `http.error.mismatchInput` with the field, e.g. `filter.enumValues.[0]`.
  A well-formed element or value key that no announcement uses is `200`
  with an empty page.

#### Date filters

For `publicationDateFrom`/`publicationDateTo` (public search) and
`lastProcessingDateFrom`/`lastProcessingDateTo` (authenticated search).
Days are in Swiss time and both days are included.

- Only `...From`: the announcements from exactly that day.
- Both: from the start of `...From` to the end of `...To`.
- Only `...To`, or `...To` before `...From`: `400`, `errorType` `BUSINESS`,
  `field` empty, `i18nKey` `announcement.searchDateFromMissing` or
  `announcement.searchDateRangeReversed`.
- A date before the year 1 or after the year 9999: `400`, `i18nKey`
  `announcement.searchDateOutOfRange`.
- A value that is not `yyyy-MM-dd`: `400`, like any unreadable request body.

#### How far filters are checked

Each value is checked on its own, for shape and bounds. Values are **not**
checked against each other. A combination that cannot match returns `200`
with an **empty page**, for example a gazette's own key sent with another
gazette, an announcement type that the publishing entity did not approve,
or a language, organisation type or topic the gazette does not offer.
`gazette` and `publishingEntity` can be sent together; the result then
matches both.

**Errors:** `400` for a malformed or out-of-set value — a `status` the
endpoint does not accept, a `term` under 3 or over 500 characters, a list
over its bound, an unsupported `sort.field`. A well-formed value that
names no record is `200` with an empty page. This holds for `gazette`,
`publishingEntity`, `topics`, `organisationType` and `announcementTypes`
alike. The declared responses are `200`, `400`, `401` and `500` — there is
no `404` and no `422` on a search.

> **Practical note:** Filters reduce what you have to fetch and process.
> Combine them (for example `gazette` + `announcementTypes` + a date
> filter) instead of filtering client-side. See also the
> [Fair Use Policy](#fair-use-policy) at the top of this document.

---

## 5. Retrieving Announcement Detail

### 5.1 Public Detail

```http
GET /public/interface/v1/announcements/{publication-number}
Authorization: Bearer <api-key>
```

| Item | Value |
|---|---|
| `operationId` | `getInterfacePublicDetail` |
| Response (`200`) | `AnnouncementPublicDetailApiDto` |
| Auth | personal API key |

### 5.2 Authenticated Detail

```http
GET /interface/v1/announcements/{publication-number}
Authorization: Bearer <access-token>
```

| Item | Value |
|---|---|
| `operationId` | `getInterfaceAnnouncementByPublicationNumber` |
| Response (`200`) | `AnnouncementAuthorizedDetailApiDto` |
| Auth | Technical User |

### 5.3 Fields in the Detail

Both detail DTOs share the same core; the authorized detail additionally
returns processing/reference/billing information.

| Field | Authorized only? | Description |
|---|---|---|
| `id`, `publicationNumber` | – | unique identifier / publication number |
| `hasPrivacyRestrictions` | – | flag from the submission (no platform effect yet) |
| `publicationDateTime`, `publicityEndDate` | – | actual/planned publication time or end of public visibility |
| `announcementType` | – | referenced announcement type |
| `publishingEntity` | – | publishing entity |
| `gazette`, `secondaryGazettes` | – | primary/secondary gazettes (`gazetteId`, `gazetteCategory`, `gazetteName`; the authorized detail additionally has `gazetteType`) |
| `legalBasis` | – | legal basis |
| `status` | – | lifecycle status |
| `primaryTopic`, `topics` | – | topics |
| `primaryAffectedCanton`, `affectedCantons` | – | affected cantons |
| `primaryAffectedMunicipality`, `affectedMunicipalities` | – | affected municipalities |
| `languages`, `primaryLanguage` | – | languages of the announcement |
| `title` | – | multilingual title |
| `businessCase` | – | business case |
| `legalBlock` | – | legal notice/contact/deadlines, if applicable. Each deadline has `label`, `type` (`DATE`, `DURATION`, `DAYS`, `MONTHS`, `NOINFO`) and a `value` that depends on the type: a date, `{from, to}`, an integer ≥ 1, or absent for `NOINFO` |
| `content` | – | content data (elements per language) |
| `links`, `cancellationReason` | – | not yet persisted: submitted values are accepted and dropped |
| `responsiblePerson` | ✅ authorized only | responsible person |
| `lastProcessingDateTime` | ✅ authorized only | last processing timestamp |
| `plannedPublicationDate` | ✅ authorized only | planned publication date from the submission |
| `apiReference`, `internalReference` | ✅ authorized only | own references from the submission (stored and returned unchanged, without platform logic) |
| `billingInformation` | ✅ authorized only | billing information: `invoiceAddress` (`email`, `contactName`, `additionalName`, `addressLine1`, `POBoxNumber`, `street`, `houseNumber`, `zipCode`, `town`, `language`), `sapOrderNumber` and `announcementFees` (`apiDiscount`, `gazettes[]` with `gazetteId`, `gazetteFeeModel`, `announcementPrice`, and `total`). `zipCode` is a plain string, because an invoice address may be foreign; `announcementPrice` and `total` are strings, not numbers |

---

## 6. Downloading Attachments

Announcements can contain attachments (content elements of type
`attachmentEmbedded` or `attachmentLinked`). Their `url` is a
platform-relative reference of the form `/{uuid}`; the download endpoints
take the UUID **without** the leading slash.

```http
GET /public/interface/v1/announcements/attachments/{uuid}   # personal API key
GET /interface/v1/announcements/attachments/{uuid}          # Technical User
```

| Item | Value |
|---|---|
| `operationId` (public) | `downloadAttachmentPublicly` |
| `operationId` (authenticated) | `downloadAttachment` |
| Response (`200`) | the file, as `application/pdf`, `image/png` or `image/jpeg`; the type is read from the file content |

| Status | Authenticated download | Public download |
|---|---|---|
| `200` | the file | the file of an announcement in a public status |
| `400` | the reference is not a well-formed UUID | the reference is not a well-formed UUID |
| `401` | missing or invalid credentials | the API key is missing or not valid |
| `403` | the caller may not read the announcement that holds the attachment (same rule as the authorized detail) | – |
| `404` | no announcement holds an attachment with this reference, or the file is no longer available | no public announcement holds an attachment with this reference, its announcement type may not be read through the interface, or the file is no longer available — all three answer the same |
| `503` | downloads are not available at the moment | downloads are not available at the moment |

The link of an `attachmentLinked` element in a generated PDF points at the
portal's own **anonymous** download (`/public/announcement/attachments/{uuid}`),
because a reader of the PDF has no API key. That anonymous link is not part
of the API.

Uploading attachments is part of the announcement import — see
[Announcement Import](announcement-import.md).

---

## 7. Reference Data Endpoints

These endpoints return the centrally maintained master data used to
resolve references in announcement type and announcement payloads. All of
them are in the public zone (personal API key) and unpaginated:

| Endpoint | `operationId` | Purpose |
|---|---|---|
| `GET /public/interface/v1/topics` | `getTopicsViaInterface` | All topics with `key`, multilingual `label` and `description` — resolves an announcement type's `mandatoryTopics`/`allowedTopics` |
| `GET /public/interface/v1/terms` | `getTermsViaInterface` | All terms with key, `valueType`, and description — the `valueType` determines the structure of `valueTypeConfig` and of the submitted values (see the announcement import documentation, Section 7) |
| `GET /public/interface/v1/organisation-types` | `getOrganisationTypesViaInterface` | All organisation types with `key` and multilingual `label`. Keys are opaque strings (`OT01` … `OT04`), not readable names. Resolves `authorisedOrganisationTypes` and `publishingEntity.organisationType`, and is the catalog for the `organisationType` search filter |
| `GET /public/interface/v1/enum-values` | `getEnumValuesViaInterface` | All enum values with `key` and `description` — the options an `ENUM`-typed element offers in its `valueTypeConfig`; also the source of the value keys for the `enumValues` search filter |
| `GET /public/interface/v1/business-cases` | `getBusinessCasesViaInterface` | All business cases with `key` and `description`. There is no multilingual label here: the same business case can be labelled differently by different announcement types, so the label lives on the announcement type (`businessCases[].label`). Resolves an announcement type's `businessCases[].key` |
| `POST /public/interface/v1/announcement-types` | – | Searches announcement types, see [7.1](#71-searching-announcement-types) |
| `GET /public/interface/v1/announcement-types/{announcementTypeId}?version=` | `getAnnouncementTypeDetailViaInterface` | Complete definition of an announcement type (business cases, content elements, topics, pricing, publication rules), see [7.2](#72-announcement-type-detail) |
| `GET /public/interface/v1/announcements/schema` | `getAnnouncementJsonSchema` | The general announcement JSON schema (Draft 2020-12) — **not** specific to one announcement type. Usable for client-side validation, code generation, or documentation |

### 7.1 Searching announcement types

```http
POST /public/interface/v1/announcement-types
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "filter": { "gazette": "CANT0002" },
  "page": 0,
  "pageSize": 20,
  "sort": { "field": "announcementTypeId", "direction": "ASC" }
}
```

The only filter is `gazette`. `sort.field` accepts `announcementTypeId` and
`version`; any other field is rejected with `400`. The response (`items`,
`total`, `currentPage`) lists, per announcement type, `announcementType`
(the ID to use in a submission), `version`, `name` and `description`.

### 7.2 Announcement type detail

`GET /public/interface/v1/announcement-types/{announcementTypeId}` returns
the complete definition. The path variable is the business ID of the
announcement type derivate, e.g. `SR101-CANT0002` — the same value the
search returns in `announcementType`. The optional query parameter
`version` (a positive integer) pins an exact version, which reproduces a
historical definition; without it, or with an empty `version=`, the latest
version is returned.

| Status | Cause |
|---|---|
| `200` | found |
| `400` | `version` is not a positive integer (not a number, or zero or less) |
| `404` | no announcement type with this ID, or no such version |

The response contains, among others:

| Field | Meaning |
|---|---|
| `announcementTypeId`, `version`, `name`, `description`, `legalBasis` | identification and texts |
| `authorisedOrganisationTypes` | organisation type keys that may use the type |
| `businessCases[]` | per business case: `key`, `label`, `description`, `hasLegalBlock`, `legalNoticeDefault`, `setContactDefault` and `deadlines[]` (`label`, `description`, `deadlineDefault` with `type` and `value`) |
| `elements[]` | the content elements, see below |
| `publicityPeriod` | `defaultValue`, `min`, `max` (days) |
| `allowedPublicationDays`, `livePublication`, `allowGeneratePDF` | publication rules |
| `exclusivePrimaryGazetteTypes` | gazette categories that are exclusive as primary gazette |
| `price`, `apiDiscount` | pricing |
| `allowAccessViaInterface` | whether the type may be used through the interface |
| `affectedRegionType`, `setDefaultAffectedRegion` | affected-region rules |
| `mandatoryTopics`, `allowedTopics` | topic keys, see `GET /topics` |
| `supportedLanguages` | languages the type supports |

Each entry of `elements[]` has `key`, multilingual `label`, `mandatory`,
`multiple`, `isPartOfTitle`, `hiddenOnView` (the flag the announcement
detail calls `hidden`), `hideLabel`, `description`, `valueTypeConfig` and
`defaultValue`.

Every key in the response resolves against a published catalog:
`elements[].key` via `GET /terms`, `businessCases[].key` via
`GET /business-cases`, `mandatoryTopics`/`allowedTopics` via `GET /topics`
and `authorisedOrganisationTypes` via `GET /organisation-types`.

> **Important:** the `valueType` of a term (`GET /terms`) is the **only**
> place that tells you the value type of an element — the announcement type
> detail does not publish it. It determines the shape of the element's
> `valueTypeConfig` and of the values a submission may carry.

> **Tip:** `GET .../announcements/schema` is well suited to load the
> announcement JSON schema directly into an online validator and check
> your own payloads client-side before submitting — complementing the
> server-side `POST .../announcements/validate` (see the announcement
> import documentation).

---

## 8. Error Handling

| HTTP status | Meaning | Typical cause |
|---|---|---|
| `400` | Invalid request | e.g. an invalid `status` value, a malformed filter, an invalid date filter, unknown `sort.field`, an invalid `version` |
| `401` | Not authenticated | missing, invalid or expired API key or token |
| `403` | No access | the announcement exists but is not visible to the consumer |
| `404` | Not found | `publication-number`, `announcementTypeId` or attachment reference does not exist. Not returned by the searches: a search that matches nothing is `200` with an empty page |
| `500` | Server error | `ServerErrorResponse` |

---

## 9. Best Practices

- **Search first, then load the detail** — the search endpoints
  deliberately return only references (`publicationNumber`); only load the
  full object on demand via the detail endpoint, to avoid unnecessary data
  volume.
- **Filter on the server** — combine `gazette`, `announcementTypes`, `status`
  and a date filter instead of fetching broadly and filtering client-side.
  For incremental synchronization, use `lastProcessingDateFrom` in the
  authenticated search.
- **Cache reference data, but set a TTL** — topics, terms, organisation
  types, enum values, and business cases rarely change, but should not be
  cached indefinitely without revalidation.
- **Treat an empty page as an answer, not an error** — a filter
  combination that cannot match returns `200` with an empty page, never `404`.
- **Use pagination consistently** — `pageSize` is capped at 100; iterate
  over `page` for larger result sets rather than trying to load everything
  in one request.

---

## 10. Support & Further Links

- Business background document: [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen) (German)
- API Documentation for Announcement Import – separate document
- [Glossary of the Announcement Standard](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970039873052-Kleines-Glossar-zum-Meldungsstandard) (German)
