import fetch from "node-fetch";

import { username, token, jql, jiraURL } from "./config.js"

// Configuration - TODO MOVE
const user = "damyan";
const endpoint = "https://aibudy.gauss.bg/consume_browser/";

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
  .then(async function (text) {
    const parsed = JSON.parse(text);

    let maxRecords = 5;
    for (const single of parsed.issues) {
      console.log(
        // single,
        single.key,
        single.fields.summary,
        // single.fields.description
      );

      await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user,
          URI: jiraURL + '/browse/' + single.key,
          payload: single.fields.summary + ' ' + single.fields.description
        })
      });

      if (maxRecords-- <= 0) {
        break;
      }
    };
  })
  .catch(err => console.error(err));