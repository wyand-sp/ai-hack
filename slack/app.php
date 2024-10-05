<?php
include dirname(__FILE__) . DIRECTORY_SEPARATOR . 'config.php';

// Read the incoming POST request from Slack
$requestBody = file_get_contents('php://input');
$eventData = json_decode($requestBody, true);

// Check for URL verification request (Slack's challenge)
if (isset($eventData['type']) && $eventData['type'] === 'url_verification') {
	echo json_encode(['challenge' => $eventData['challenge']]);
	exit();
}

// Process incoming messages
if (isset($eventData['event']) && $eventData['event']['type'] === 'message') {
	$messageText = $eventData['event']['text'];
	$user = $eventData['event']['user'];
	$channel = $eventData['event']['channel'];
	$timestamp = $eventData['event']['ts'];

	// Log the message (for debugging)
	error_log("New message received: $messageText");

	// You can send this message to your external API or store it
	sendMessageToAPI($messageText, $user, $channel, $timestamp);
}

// Function to send the message to an external API
function sendMessageToAPI($message, $user, $channel, $timestamp) {
	$data = [
		'user' => USERNAME,
		'URI' => 'Slack ' . $channel . ' ' . $timestamp,
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
