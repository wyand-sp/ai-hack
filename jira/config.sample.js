const username = 'example@example.com';
const token = 'token';
const jql = 'updated >= "2024-07-05" AND updated <= "2024-07-07"'; // TODO: dynamic
const jiraURL = 'https://example.atlassian.net';

module.exports = { username, token, jql, jiraURL };