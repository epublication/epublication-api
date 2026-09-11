# Migration Guide: SHAB → ePublication (Announcement Type Mapping)

> **Context:** ePublication (Swiss Official Gazettes Portal) replaces the
> previous Amtsblattportal, through which official publications
> (announcements) of various public bodies at the three federal levels of
> Switzerland (federal, cantonal, municipal) were published. At the
> federal level, this concerns in particular the **SHAB**
> (Schweizerisches Handelsamtsblatt / Swiss Official Gazette of Commerce).
> On ePublication, announcements are published with a **simpler, more
> generic structure** than previously on the Amtsblattportal.

---

## Source

The complete, continuously maintained mapping tables (previous SHAB
categories/subcategories → new announcement types) are **not** duplicated
in this repository. Instead, they are maintained centrally in the Help
Center, to avoid redundancy and outdated copies:

- 🇩🇪 German: [Kataloge](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970274717084-Kataloge)
- 🇫🇷 French: [Catalogues](https://helpcenter-epublication.zendesk.com/hc/fr/articles/28970274717084-Catalogues)
- 🇮🇹 Italian: [Elenchi](https://helpcenter-epublication.zendesk.com/hc/it/articles/28970274717084-Elenchi)

> This page does **not exist in English**. English-speaking readers need
> to use one of the three language versions above.

From there, the corresponding Excel mapping table is linked as a download
for each gazette, including the **Swiss Official Gazette of Commerce
(SHAB)**. For most cantonal gazettes, the mapping tables have not yet been
published according to the page ("Mapping table coming soon...") — see
the page itself for the current status.

> **Note:** These mapping tables are still being worked on and are continuously extended/adjusted. Always consult the Help Center page for the binding, current status rather than a local copy.

## Practical Note on Usage

For the technical implementation of a given announcement type (fields,
`valueTypeConfig`, business cases), the mapping table is only a starting
point. The live definition via the API is authoritative:

```http
GET /public/interface/v1/announcement-types/{announcementTypeId}
```

See [Announcement Export](announcement-export.md), Section 7, for details
on this and other reference-data endpoints.

---

## Support & Further Links

- [Announcement Import](announcement-import.md) – separate document
- [Announcement Export](announcement-export.md) – separate document
- Business background document: [Standardized Announcement Types](https://helpcenter-epublication.zendesk.com/hc/de/articles/28970270476572-Standardisierte-Meldungstypen) (German)
