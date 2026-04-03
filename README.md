# How to use this repository?

This repository describes the external management API for ePublication. The API enables programmatic interaction for publishing announcements in official gazettes. These RESTful APIs are built in accordance with the OpenAPI specification for seamless third-party integration, with interactive documentation provided via Swagger UI.

The "Getting started" tutorial is designed to require no in-depth knowledge of the concepts behind ePublication nor profound programming skills. However, it is advisable to first gain an overall understanding of the concept and functionality of the platform for the implementation of the various announcement types at a later time.



> [!NOTE]
> The application's front end is accessible at https://preview.epublication.ch.

# Getting started
In this guide, we'll walk you through the basics of using the ePublication API. 
There are several ways to familiarize yourself with the API.

* The most basic way: Try out the API using Swagger
* Send a request via cURL in the command-line interface
* Use the predefined Bruno collection provided in this repository

## Swagger
Swagger is an open-source toolset built around the OpenAPI Specification that helps developers design, build, document, and consume RESTful web services. If you're interested in playing around and getting familiar with the API, there is no need to install local software, simply go to the public [Swagger Endpoints](https://preview.epublication.ch/api/management/swagger-ui/index.html?urls.primaryName=External#/External%20Consumers%3A%20Restricted%20APIs/searchInterfaceAnnouncements)

#### Get published announcements
Getting published announcements would work step by step as follows:<br /><br />1. No authentication is required for requesting published announcements (the screenshot below shows all endpoints that do not require authentication).<br /><br />
<img width="1064" height="222" alt="image" src="https://github.com/user-attachments/assets/565bb38b-e100-4b79-a7bd-4635aec8b988" /><br /><br />
2. The endpoint "../announcements" can be used to get the matching announcements in a list. The list contains only metadata, such as the announcement title and the publication number. The following sample code demonstrates the filtering possibilities. Using the specified filter criteria, only those announcements that were published in Gazette A and contain the term “Sample” will be returned. You can copy/paste the code into the "request body" field and hit "Try it out".<br /><br />
<img width="943" height="235" alt="image" src="https://github.com/user-attachments/assets/ed3d10b5-b488-4c9e-96a7-0a99a3816676" />
<br /><br />
A simple example requesting all publications published in "Gazette A" containing the term "Sample".
```json

{
  "filter": {
    "gazette": "GZA",
    "term": "Sample"
  },
  "page": 0,
  "pageSize": 20,
  "sort": {
    "field": "businessId",
    "direction": "ASC"
  }
}

```
<br />
The code above can be pasted into the request body field.<br /><br />
<img width="941" height="520" alt="image" src="https://github.com/user-attachments/assets/6e9adbaf-73bc-47ec-ad91-01c671f1cacd" /><br /><br />
If the request is successful (HTTP status 200), the list is returned as JSON.<br /><br />
<img width="940" height="342" alt="image" src="https://github.com/user-attachments/assets/9be70225-eddb-4f74-aa19-f662f6e5f345" /><br /><br />
3. The value of publicationNumber is then used to retrieve the detailed data of an announcement. To do this, the endpoint “../announcement/{publicationNumber}” is used. Copy the publicationNumber value in the field "publication-number".<br /><br />

<img width="938" height="392" alt="image" src="https://github.com/user-attachments/assets/16e76064-a49a-4b82-9aff-d52f2c3062e3" /><br /><br />

This procedure demonstrates how data retrieval should essentially be implemented

#### Submit announcement
The endpoint for submitting announcements is likely to be of particular interest, Let's walk through this step by step. Authentication is required for certain requests (submitting announcements, retrieving unpublished announcements). Please [contact](https://helpcenter-epublication.zendesk.com/hc/de/requests/new?ticket_form_id=25547817106076) us for demo access. With the credentials provided, you'll be able to use the following restricted endpoints.

<img width="1063" height="173" alt="image" src="https://github.com/user-attachments/assets/ccb749c8-1845-4b41-8ebf-cfe7c118ca61" /><br /><br />

1. Log in using the credentials provided.
   
<img width="658" height="448" alt="image" src="https://github.com/user-attachments/assets/a4e5bc7e-301d-4683-a698-fdea23170ad0" /><br /><br />  



2. Open the endpoint "../submission" and hit "Try it out".
   
<img width="1060" height="386" alt="image" src="https://github.com/user-attachments/assets/62936713-a4da-4b94-a95c-86b681a3fcda" /><br /><br />


3. You will now see an editable field with a white background. Delete the code in the field.
   
<img width="1058" height="613" alt="image" src="https://github.com/user-attachments/assets/b10d784e-a673-4eae-ac2e-edcb586e904b" /><br /><br />
 

4. Paste the code provided below in the field. Note: The value of "publicationDateTime" must be in the future and fall on a weekday.


   
   
```json
{
  "publishingEntity": "PEA",
  "organizationUnit": "PEA-OE01",
  "gazette": "GZA",
  "announcementType": "000",
  "publicationPeriod": 35,
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
<br /><br />
4. You should then get a HTTP 201 response. This means that the announcement was imported successfully.
   
<img width="1061" height="239" alt="image" src="https://github.com/user-attachments/assets/92354754-c7cd-4c16-abc8-5fac849a49e5" /><br /><br />

5. The announcement is now published. You can view the announcement in the application's front end at https://preview.epublication.ch..

<kbd><img width="1007" height="675" alt="image" src="https://github.com/user-attachments/assets/75ca342e-4f8b-485d-be51-75472094d3da" /></kbd><br /><br />


## CLI
Another easy way to establish your first connection is to use the simple curl command below. Again, no authentication is required to view a list of published announcements. Just open a command prompt (e.g. cmd on your windows computer) and paste the following curl command. As a result, you should get a list in JSON format of the last 20 announcements published on epublication.ch.  


```bash
curl -X "POST" "https://preview.epublication.ch/api/management/public/interface/v1/announcements" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"page\": 0, \"pageSize\": 20}"

```

## Bruno

Bruno is an open-source API client alternative to tools like Postman and Insomnia. Bruno stores your collections directly in a folder on your filesystem using a plain-text markup language. 

Download Bruno: [https://www.usebruno.com](https://www.usebruno.com/)

Import the collection provided in this repository. You can find more information on how to use it in the “Docs” tab within the collection.

### Sample collection
New sample imports for the following announcement types have been added to the Bruno collection:

- General official announcement
- Individual construction project
- Notice regarding the notary register
- Commercial register entry
- Commencement of bankruptcy proceedings
- Call for claims due to change in organisation

# What's next?
The MVP is now being continuously improved. New information and step-by-step instructions will be published continuously here.
Next will be:
- Schemes of the most important announcement types
- Catalog of the possible keys/terms to be used
- Catalog of the possible business cases to be used
