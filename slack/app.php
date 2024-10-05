<?php
include dirname(__FILE__) . DIRECTORY_SEPARATOR . 'config.php';

// Read the incoming POST request from Slack
$request_body = file_get_contents('php://input');
$event_data = json_decode($request_body, true);

// Check for URL verification request (Slack's challenge)
if (isset($event_data['type']) && $event_data['type'] === 'url_verification') {
	echo json_encode(['challenge' => $event_data['challenge']]);
	exit();
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
	$data = [
		'user' => USERNAME,
		'URI' => '#' . $channel . ' ' . $timestamp,
		'payload' => $message,
	];

	$options = [
		'http' => [
			'header' => "Content-type: application/json\r\n",
			'method' => 'POST',
			'content' => json_encode($data),
		],
	];

	$context = stream_context_create($options);
	$result = file_get_contents(CONSUME_URL, false, $context);
	// TODO: handle $result
}

// Respond with HTTP 200 status to acknowledge receipt
http_response_code(200);
