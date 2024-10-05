<?php

include dirname(__FILE__) . DIRECTORY_SEPARATOR . 'config.php';

try {
    # Get the timestamp of the latest email in the box
    $mailbox = imap_open("{" . SMTP_HOST . "/imap/ssl/novalidate-cert}INBOX", SMTP_MAIL, SMTP_PASS);
    $emailIds = imap_search($mailbox, 'ALL');
    rsort($emailIds);
    $header = $emailIds ? imap_headerinfo($mailbox, $emailIds[0]) : null;
    $timestamp = $header ? $header->udate : 0;

    # Get all emails older than MAX_AGE
    if ($timestamp > 0) {
        $emailIds = imap_search($mailbox, 'ALL');
        rsort($emailIds);
        $emails = [];

        foreach ($emailIds as $emailId) {
            $header = imap_headerinfo($mailbox, $emailId);
            if ($header->udate <= $timestamp - MAX_AGE) {
                break;
            }
            $contnet = imap_body($mailbox, $emailId);

            $emails[] = [
                "date" => $header->date,
                "subject" => $header->subject,
                "to" => $header->to,
                "content" => $contnet
            ];
            # TODO: Call the vector store
        }
    }
} catch (Exception $e) {
    throw $e;
}