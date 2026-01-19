<?php
// server/utils.php

/**
 * Shared Utility Functions for Tech Blog Newsletter
 */

/**
 * Reads subscribers from a CSV file.
 * 
 * @param string $csv_file Absolute path to the subscribers CSV file.
 * @return array List of unique subscriber emails.
 */
function getSubscribers(string $csv_file): array
{
    $emails = [];
    if (file_exists($csv_file)) {
        if (($handle = fopen($csv_file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                if (filter_var($data[0], FILTER_VALIDATE_EMAIL)) {
                    $emails[] = $data[0];
                }
            }
            fclose($handle);
        }
    }
    return array_unique($emails);
}

/**
 * Sends a newsletter email using professional HTML template.
 * 
 * @param string $to Recipient email address.
 * @param string $subject Email subject.
 * @param string $html_body raw HTML content of the email body.
 * @param string $sender_email Sender email address (e.g., newsletter@domain.com).
 * @return bool True if mail accepted for delivery, False otherwise.
 */
function sendNewsletter(string $to, string $subject, string $html_body, string $sender_email): bool
{
    // Headers
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
    $headers .= "From: Ritesh Rana <" . $sender_email . ">" . "\r\n";
    $headers .= "Reply-To: contact@riteshrana.engineer" . "\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();
    $headers .= "Return-Path: <" . $sender_email . ">" . "\r\n";
    $headers .= "List-Unsubscribe: <https://riteshrana.engineer/unsubscribe.php?email=" . urlencode($to) . ">" . "\r\n";

    // Base64 Encode Subject to handle special chars
    $encoded_subject = "=?UTF-8?B?" . base64_encode($subject) . "?=";

    // Base64 Encode Body to strictly limit line length (prevent spam/transmission errors)
    $base64_body = chunk_split(base64_encode($html_body));

    // Update headers for Base64 transfer
    $headers .= "Content-Transfer-Encoding: base64\r\n";

    return mail($to, $encoded_subject, $base64_body, $headers);
}

/**
 * Fetches the latest 3 posts from the RSS feed.
 * 
 * @param string $feed_url URL of the RSS feed.
 * @return array Array of posts ['title', 'link', 'description', 'guid']
 */
function getLatestPostsFromFeed(string $feed_url): array
{
    $rss = @simplexml_load_file($feed_url);
    if ($rss === false) {
        return [];
    }

    $posts = [];
    $count = 0;
    foreach ($rss->channel->item as $item) {
        if ($count >= 3)
            break; // Get top 3

        // Clean description (remove images/scripts, limit length)
        $description = strip_tags((string) $item->description);
        $description = substr($description, 0, 150) . '...';

        $posts[] = [
            'title' => (string) $item->title,
            'link' => (string) $item->link,
            'description' => $description,
            'guid' => (string) $item->guid
        ];
        $count++;
    }
    return $posts;
}

/**
 * Generates the HTML Body for the newsletter.
 * 
 * @param string $content Main content (e.g., list of latest posts).
 * @param string $unsubscribe_link URL for unsubscribing.
 * @return string Full HTML email.
 */
function generateEmailTemplate(string $content, string $unsubscribe_link): string
{
    return '
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
            .container { max-width: 600px; margin: 0 auto; background: #ffffff; padding: 0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
            .header { background: #1a1a1a; color: #ffffff; padding: 30px 20px; text-align: center; }
            .header h1 { margin: 0; font-size: 24px; letter-spacing: -0.5px; }
            .header p { margin: 10px 0 0 0; color: #888888; font-size: 14px; }
            .content { padding: 40px 30px; line-height: 1.6; color: #333333; }
            .post-preview { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eeeeee; }
            .post-preview:last-child { border-bottom: none; }
            .post-title { font-size: 18px; font-weight: 700; color: #1a1a1a; text-decoration: none; display: block; margin-bottom: 8px; }
            .post-meta { font-size: 12px; color: #888888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
            .btn { display: inline-block; background: #0070f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: 500; margin-top: 15px; }
            .footer { background: #f9f9f9; padding: 30px; text-align: center; font-size: 12px; color: #888888; border-top: 1px solid #eeeeee; }
            .footer a { color: #888888; text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Ritesh Rana Tech Blog</h1>
                <p>Engineering insights delivered to your inbox.</p>
            </div>
            <div class="content">
                ' . $content . '
            </div>
            <div class="footer">
                <p>You received this email because you subscribed to my tech blog.</p>
                <p>
                    <a href="https://riteshrana.engineer">Visit Website</a> • 
                    <a href="' . $unsubscribe_link . '">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>';
}
?>