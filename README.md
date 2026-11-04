# ePublication API Documentation

Developer documentation for the ePublication (Swiss Official Gazettes
Portal) external API.

## Contents

- [Authentication](docs/authentication.md) — credential types, header format,
  key issuance; single source of truth for auth across all documents below.
- [Announcement Export](docs/announcement-export.md) — for public consumers and
  authenticated third-party applications that search and retrieve
  published announcements.
- [Announcement Import](docs/announcement-import.md) — for developers of
  upstream systems (Fachapplikationen) that generate announcements and
  submit them for publication.
- [Migration Guide: SHAB → ePublication](docs/migration-shab.md) — mapping of
  legacy SHAB (Schweizerisches Handelsamtsblatt) announcement codes to the
  new ePublication announcement types.
- [Bruno examples](bruno/README.md) — runnable requests to try the
  announcement import API directly, alongside the written docs above.

## Status

The API-key authentication for data consumers and the Technical User
authentication for data suppliers are live in the **preview** environment.
The production environment is not available yet. Individual documents list
points that are still being confirmed.
