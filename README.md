> [!IMPORTANT] 
> If you are unfamiliar with the portal, we recommend that you read the brief [introduction](https://github.com/epublication/overview) to ePublication, regardless of your intention to use the APIs.
# Getting started
In this guide, we'll walk you through the basics of using the ePublication API.
1. Create account 
> [!IMPORTANT]
> The MVP environment is currently available. To try it out, please contact us.
2. Request announcement list
> Go to [Swagger](https://web.seco-amtsblattportal-int.sdlc.aws.elca.ch/api/management/swagger-ui/index.html?urls.primaryName=External#/External%20Consumers%3A%20Restricted%20APIs/searchInterfaceAnnouncements)
3. Request announcement
> Go to Swagger

 
# The Announcement API
> [!TIP] 
> Who might be interessted in this API?
> - Data client
> - Data supplier

[An OpenAPI description of the Announcement API can be found here](https://web.seco-amtsblattportal-dev.sdlc.aws.elca.ch/api/management/swagger-ui/index.html?urls.primaryName=External)

Examples: Bruno Collection here

```
curl -X 'POST' \
  'https://web.seco-amtsblattportal-int.sdlc.aws.elca.ch/api/management/public/interface/v1/announcement-types' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "filter": {
    "announcementType": "SR102"
  },
  "page": 0,
  "pageSize": 20,
  "sort": {
    "field": "businessId",
    "direction": "ASC"
  }
}'
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
