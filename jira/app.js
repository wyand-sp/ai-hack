import fetch from "node-fetch";

import { username, token, jql, jiraURL } from "./config.js"

fetch(jiraURL + '/rest/api/2/search?jql=' + jql, {
  method: 'GET',
  headers: {
    'Authorization': `Basic ${Buffer.from(username + ':' + token).toString('base64')}`,
    'Accept': 'application/json'
  }
})
  .then(response => {
    return response.text();
  })
  .then(text => {
    const parsed = JSON.parse(text);

    parsed.issues.map(single => {
        console.log(
            single.key,
            single.fields.summary,
            single.fields.description
        );
        // TODO: send to vector store
    });
  })
  .catch(err => console.error(err));