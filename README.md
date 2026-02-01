> [!IMPORTANT] 
> If you are unfamiliar with the portal, we recommend that you read the brief [introduction](https://github.com/epublication/overview) to ePublication, regardless of your intention to use the APIs.

# The Announcement API
> [!TIP] 
> Who might be interessted in this API?
> - Data client
> - Data supplier

General Announcement schema here

Examples: Bruno Collection here

```
{
  "publishingEntity": "PS01",
  "organizationUnit": "PS01-OE02",
  "createdOnBehalfOf": "dac",
  "internalReferenceNumber": "TBD",
  "primaryGazette": "CBE",
  "announcementType": "demoS4RC2",
  "publicationPeriod": 24,
  "languages": [
    "DE",
    "FR"
  ],
  "primaryLanguage": "DE",
  "secondaryGazettes": [],
  "primaryTopic": "CallsToCreditors",
  "allowedTopics": [
    "building"
  ],
  "primaryAffectedCanton": "BE",
  "affectedCantons": [
    "ZH",
    "LU"
  ],
  "primaryAffectedGemeinde": "Stallikon",
  "affectedGemeindes": [
    "Wettswil am Albis"
  ],
  "businessCase": "rennovate",
  "plannedPublicationDate": "2025-12-08",
  "content": [
    {
      "language": "DE",
      "elements": [
        {
          "key": "acquiringCompany",
          "label": "Legal Person DE",
          "type": "legalPerson",
          "value": [
            {
              "uid": "test",
              "organizationName": "test",
              "legalForm": "0107",
              "address": {
                "street": "test",
                "houseNumber": "123",
                "swissZipCode": "3000",
                "town": "test",
                "addressLine1": "test",
                "postOfficeBoxText": "test"
              }
            }
          ]
        },
        {
          "key": "legalRemedy",
          "label": "Textarea DE",
          "type": "textarea",
          "value": [
            "<p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.</p>"
          ]
        },
        {
          "key": "pointOfContact",
          "label": "Person DE",
          "type": "person",
          "value": [
            {
              "personType": "NATURAL",
              "naturalPerson": {
                "address": {
                  "street": "test",
                  "houseNumber": "123",
                  "swissZipCode": "3000",
                  "town": "test",
                  "addressLine1": "test",
                  "postOfficeBoxText": "test"
                },
                "officialName": "test",
                "firstName": "test"
              },
              "legalPerson": {}
            }
          ]
        },
        {
          "key": "projectAddress",
          "label": "Address DE",
          "type": "address",
          "value": [
            {
              "street": "test",
              "houseNumber": "123",
              "swissZipCode": "3000",
              "town": "test",
              "addressLine1": "test",
              "postOfficeBoxText": "test"
            }
          ]
        },
        {
          "key": "testDateFromTo",
          "label": "DateFromTo DE",
          "type": "dateFromTo",
          "value": [
            {
              "from": "2025-11-01",
              "to": "2025-11-02"
            }
          ]
        },
        {
          "key": "testUrl",
          "label": "URL DE",
          "type": "url",
          "value": null
        },
        {
          "key": "deceasedPerson",
          "label": "Verstorbene Person",
          "type": "composite",
          "value": [
            {
              "subElements": [
                {
                  "label": "Peronalien",
                  "type": "naturalPerson",
                  "value": [
                    {
                      "officialName": "tes",
                      "firstName": "test",
                      "address": {
                        "addressLine1": "test test",
                        "street": "test",
                        "houseNumber": "test",
                        "postOfficeBoxText": "test",
                        "town": "test",
                        "swissZipCode": "3000"
                      }
                    }
                  ]
                },
                {
                  "label": "Geburtsdatum",
                  "type": "date",
                  "value": [
                    "2025-11-08"
                  ]
                },
                {
                  "label": "Todesdatum",
                  "type": "date",
                  "value": [
                    "2025-11-09"
                  ]
                },
                {
                  "label": "Todesart",
                  "type": "enum",
                  "value": [
                    "Nicht natürlich"
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "language": "FR",
      "elements": [
        {
          "key": "acquiringCompany",
          "label": "Legal Person DE",
          "type": "legalPerson",
          "value": [
            {
              "uid": "test",
              "organizationName": "test",
              "legalForm": "0107",
              "address": {
                "street": "test",
                "houseNumber": "123",
                "swissZipCode": "3000",
                "town": "test",
                "addressLine1": "test",
                "postOfficeBoxText": "test"
              }
            }
          ]
        },
        {
          "key": "legalRemedy",
          "label": "Textarea FR",
          "type": "textarea",
          "value": [
            "<p>Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged.</p>"
          ]
        },
        {
          "key": "pointOfContact",
          "label": "Person DE",
          "type": "person",
          "value": [
            {
              "personType": "NATURAL",
              "naturalPerson": {
                "address": {
                  "street": "test",
                  "houseNumber": "123",
                  "swissZipCode": "3000",
                  "town": "test",
                  "addressLine1": "test",
                  "postOfficeBoxText": "test"
                },
                "officialName": "test",
                "firstName": "test"
              },
              "legalPerson": {}
            }
          ]
        },
        {
          "key": "projectAddress",
          "label": "Address DE",
          "type": "address",
          "value": [
            {
              "street": "test",
              "houseNumber": "123",
              "swissZipCode": "3000",
              "town": "test",
              "addressLine1": "test",
              "postOfficeBoxText": "test"
            }
          ]
        },
        {
          "key": "testDateFromTo",
          "label": "DateFromTo DE",
          "type": "dateFromTo",
          "value": [
            {
              "from": "2025-11-01",
              "to": "2025-11-02"
            }
          ]
        },
        {
          "key": "testUrl",
          "label": "URL DE",
          "type": "url",
          "value": [
            "https://www.example.com"
          ]
        },
        {
          "key": "deceasedPerson",
          "label": "Verstorbene Person",
          "type": "composite",
          "value": [
            {
              "subElements": [
                {
                  "label": "Peronalien",
                  "type": "naturalPerson",
                  "value": [
                    {
                      "officialName": "tes",
                      "firstName": "test",
                      "address": {
                        "addressLine1": "test test",
                        "street": "test",
                        "houseNumber": "test",
                        "postOfficeBoxText": "test",
                        "town": "test",
                        "swissZipCode": "3000"
                      }
                    }
                  ]
                },
                {
                  "label": "Geburtsdatum",
                  "type": "date",
                  "value": [
                    "2025-11-08"
                  ]
                },
                {
                  "label": "Todesdatum",
                  "type": "date",
                  "value": [
                    "2025-11-09"
                  ]
                },
                {
                  "label": "Todesart",
                  "type": "enum",
                  "value": [
                    "Nicht natürlich"
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "publicationDate": "2025-12-24",
  "status": "SUBMITTED"
}
```

# The Editor API
> [!TIP] 
> Who might be interessted in this API?
> - Editor
> - Data client
> - Data supplier

Search announcement types --> [Swagger](https://web.seco-amtsblattportal-dev.sdlc.aws.elca.ch/api/management/swagger-ui/index.html#/External%20Consumers%3A%20Public%20APIs/getAllAnnouncementTypeViaInterface)
This API allows to search for all announcement types in the platform. It returns a paginated list of announcement types with minimal information. The response data could be used to prepare request for respective endpoints. Search parameters and pagination settings can be specified in the body. See schema description of request body on parameters for searching and pagination.

# The Admin API
> [!TIP] 
> Who might be interessted in this API?
> - Software Developer
> - Anyone with a deeper interest in understanding the code of the portal

Details coming soon
