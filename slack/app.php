<?php
// Read the incoming POST request from Slack
$request_body = file_get_contents('php://input');
$event_data = json_decode($request_body, true);

// Check for URL verification request (Slack's challenge)
if (isset($event_data['type']) && $event_data['type'] === 'url_verification') {
    echo json_encode(['challenge' => $event_data['challenge']]);
    exit;
}

// Process incoming messages
if (isset($event_data['event']) && $event_data['event']['type'] === 'message') {
    $message_text = $event_data['event']['text'];
    $user = $event_data['event']['user'];
    $channel = $event_data['event']['channel'];
    $timestamp = $event_data['event']['ts'];

    // Log the message (for debugging)
    error_log("New message received: $message_text");

    // You can send this message to your external API or store it
    sendMessageToAPI($message_text, $user, $channel, $timestamp);
}

// Function to send the message to an external API
function sendMessageToAPI($message, $user, $channel, $timestamp) {
    // TODO - send to vector store
}

http_response_code(200);  // Respond with HTTP 200 status to acknowledge receipt