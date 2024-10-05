<?php

include dirname(__FILE__) . DIRECTORY_SEPARATOR . 'config.php';

try {
	# Get the timestamp of the latest email in the box
	$mailbox = imap_open('{' . SMTP_HOST . '/imap/ssl/novalidate-cert}INBOX', SMTP_MAIL, SMTP_PASS);
	$emailIds = imap_search($mailbox, 'ALL');
	rsort($emailIds);
	$header = $emailIds ? imap_headerinfo($mailbox, $emailIds[0]) : null;
	$timestamp = $header ? $header->udate : 0;

	# Get all emails older than MAX_AGE
	if ($timestamp > 0) {
		$emailIds = imap_search($mailbox, 'ALL');
		rsort($emailIds);

		foreach ($emailIds as $emailId) {
			$header = imap_headerinfo($mailbox, $emailId);
			if ($header->udate <= $timestamp - MAX_AGE) {
				break;
			}
			$contnet = imap_body($mailbox, $emailId);

			$data = [
				'user' => USERNAME,
				'URI' => 'Email "' . $header->subject . '" from ' . $header->date,
				'payload' => $contnet,
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
	}
} catch (Exception $e) {
	throw $e;
}
