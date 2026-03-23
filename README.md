# How to use this repository?

It is advisable to first gain an overall understanding of the concept and functionality of the platform.
If you are unfamiliar with the portal, we recommend that you read the brief [introduction](https://github.com/epublication/overview) to ePublication, regardless of your intention to use the API. To obtain detailed technical background information, we recommend reading the [wiki](https://github.com/epublication/epublication-api/wiki) for this repository.

This repository describes the external management API for ePublication. The API enables programmatic interaction for publishing announcements in official gazettes. These RESTful APIs are designed for seamless third-party integration, with interactive documentation provided via Swagger UI. Access the documentation at ePublication Swagger UI.


# Getting started
In this guide, we'll walk you through the basics of using the ePublication API. 
There are several ways to familiarize yourself with the API.

* The most basic way: Try out the API using Swagger
* Send a request via cURL in the command-line interface
* Use the predefined Bruno collection provided in this repository

### Swagger 
Swagger is an open-source toolset built around the OpenAPI Specification that helps developers design, build, document, and consume RESTful web services. If you're interested in playing around and getting familiar with the API, there is no need to install local software, simply go to the public [Swagger Endpoints](https://preview.epublication.ch/api/management/swagger-ui/index.html?urls.primaryName=External#/External%20Consumers%3A%20Restricted%20APIs/searchInterfaceAnnouncements)

<img width="1064" height="222" alt="image" src="https://github.com/user-attachments/assets/565bb38b-e100-4b79-a7bd-4635aec8b988" />

However, authentication is required for certain requests (submitting announcements, retrieving unpublished announcements). Please [contact](https://helpcenter-epublication.zendesk.com/hc/de/requests/new?ticket_form_id=25547817106076) us for demo access. With the credentials provided, you'll be able to use the following restricted endpoints.

<img width="1063" height="173" alt="image" src="https://github.com/user-attachments/assets/ccb749c8-1845-4b41-8ebf-cfe7c118ca61" />

The endpoint for submitting announcements is likely to be of particular interest, Let's walk through this step by step.

1. Log in using the credentials provided.

   
<img width="658" height="448" alt="image" src="https://github.com/user-attachments/assets/a4e5bc7e-301d-4683-a698-fdea23170ad0" />  



2. Open the endpoint "../submission" and hit "Try it out".

   
<img width="1058" height="526" alt="image" src="https://github.com/user-attachments/assets/be0623ab-eecf-405d-9183-593b42404c5d" />  



3. Paste the code provided below. Note: The value of "publicationDateTime" must be in the future and fall on a weekday.
   
   
```json
{
  "publishingEntity": "PEA",
  "organizationUnit": "PEA-OE01",
  "gazette": "GZA",
  "announcementType": "110",
  "publicationPeriod": 25,
  "languages": [
    "DE" 
  ],
  "primaryLanguage": "DE",
  "secondaryGazettes": [
    "GZB" 
  ],
  "primaryTopic": "debtEnforcementBankruptcy", 
  "allowedTopics": [
    "debtEnforcementBankruptcy" 
  ],
  "primaryAffectedCanton": "ZH", 
  "affectedCantons": [
  "ZH"
  ],
  "primaryAffectedMunicipality": "Hausen am Albis", 
  "affectedMunicipalities": [
  "Hausen am Albis"
  ],
  "businessCase": "documentA", 
  "content": [ 
    {
      "language": "DE",
      "elements": [
        {
          "key": "name", 
          "label": "Titel der Meldung", 
          "type": "stringMultiLang", 
          "value": [
            "Some Sample Title" 
          ]
        },
    {
          "key": "notice",
          "label": "Inhalt",
          "type": "textarea", 
          "value": [
            "Some Sample Content: Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard <strong>dummy text</strong> ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book.<br /><br /><ul><li>It has survived not only five centuries</li><li>but also the leap into electronic typesetting</li></ul>Remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
          ]
        }
      ]
    }
  ],
  "publicationDateTime": "2026-04-02", 
  "status": "PUBLISHED"
}

```




### CLI
Another easy way to establish your first connection is to use the simple curl command below. Again, no authentication is required to view a list of published announcements. Just open a command prompt (e.g. cmd on your windows computer) and paste the following curl command. As a result, you should get a list in JSON format of the last 20 announcements published on epublication.ch.  


```bash
curl -X "POST" "https://preview.epublication.ch/api/management/public/interface/v1/announcements" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"page\": 0, \"pageSize\": 20}"

```

### Bruno

Bruno is an open-source API client alternative to tools like Postman and Insomnia. Bruno stores your collections directly in a folder on your filesystem using a plain-text markup language. 

Download Bruno: [https://www.usebruno.com](https://www.usebruno.com/)

Import the collection provided in this repository. You can find more information on how to use it in the “Docs” tab within the collection.


# What's next?
The MVP is now being continuously developed. New information and step-by-step instructions will be published continuously here.
