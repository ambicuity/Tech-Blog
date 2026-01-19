<?php
// cron_send.php - Automate Newsletter Sending
// Upload this to your 'server' folder.
// Run via Cron Job (e.g., every hour): php /path/to/server/cron_send.php YOUR_SECRET_KEY

// --- CONFIGURATION ---
$SECRET_KEY = 'CHANGE_ME_ON_SERVER'; // ⚠️ CHANGE THIS on your server file manager!
$FEED_URL = 'https://blog.riteshrana.engineer/feed.xml';
$STATE_FILE = __DIR__ . '/last_sent_post.txt';
$CSV_FILE = __DIR__ . '/subscribers.csv';
$SENDER_EMAIL = 'newsletter@riteshrana.engineer';
// ---------------------

// 1. Security Check
$provided_key = '';
if (php_sapi_name() === 'cli') {
    $provided_key = $argv[1] ?? '';
} else {
    $provided_key = $_GET['key'] ?? '';
}

if ($provided_key !== $SECRET_KEY) {
    http_response_code(403);
    die("Error: Access Denied. Invalid Key.");
}

// 2. Fetch RSS Feed
$content = @file_get_contents($FEED_URL);
if (!$content)
    die("Error: Could not fetch feed from $FEED_URL");

$xml = @simplexml_load_string($content);
if (!$xml)
    die("Error: Could not parse XML feed.");

// Get Latest Item (Support Atom & RSS)
$item = isset($xml->entry) ? $xml->entry[0] : (isset($xml->channel->item) ? $xml->channel->item[0] : null);

if (!$item)
    die("Error: No posts found in feed.");

// Extract Data
$title = (string) $item->title;
$link_obj = $item->link;
if (isset($link_obj['href'])) {
    $link = (string) $link_obj['href'];
} else {
    $link = (string) $link_obj;
}

// Unique ID (Use content link or ID tag)
$unique_id = (string) ($item->id ?? $link);

// Description (Summary/Content)
$desc_raw = (string) ($item->summary ?? $item->content ?? $item->description ?? '');
$desc_clean = strip_tags($desc_raw);
// Truncate to ~300 chars for the intro
if (strlen($desc_clean) > 300) {
    $desc_clean = substr($desc_clean, 0, 300) . '...';
}

echo "Checked Feed: Found '$title' ($unique_id)\n";

// 3. Check State (Is this new?)
$last_sent_id = '';
if (file_exists($STATE_FILE)) {
    $last_sent_id = trim(file_get_contents($STATE_FILE));
}

if ($unique_id === $last_sent_id) {
    die("Result: Post already sent. Exiting.\n");
}

// 4. Prepare Email Content (Professional Template)
$subject = "New Post: " . $title;
$body_content = "<h1>New Blog Post Published!</h1>";
$body_content .= "<h2><a href='$link' style='text-decoration:none; color:#333;'>$title</a></h2>";
$body_content .= "<p style='font-size:16px; color:#555;'>$desc_clean</p>";
$body_content .= "<p><a href='$link' class='button' style='display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;'>Read Full Article</a></p>";

// 5. Send to All Subscribers
if (!file_exists($CSV_FILE))
    die("Error: Subscribers file not found.");

$count = 0;
if (($handle = fopen($CSV_FILE, "r")) !== FALSE) {
    while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
        // CSV Format: Date, Email, IP (Email is index 1)
        $email = trim($data[1] ?? '');

        if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
            // --- Template Logic (Copied from admin_send.php) ---
            $full_body = '<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { margin: 0; padding: 0; background-color: #f4f4f4; font-family: sans-serif; }
                    .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; }
                    .header { background: #1e1e1e; padding: 30px 20px; text-align: center; }
                    .header img { width: 60px; height: 60px; border-radius: 50%; border: 3px solid #ffffff; }
                    .header h1 { color: #ffffff; margin: 15px 0 5px 0; font-size: 24px; }
                    .header p { color: #aaaaaa; margin: 0; font-size: 14px; }
                    .content { padding: 30px; font-size: 16px; line-height: 1.6; color: #333333; }
                    .footer { background: #f9f9f9; padding: 20px; text-align: center; border-top: 1px solid #eeeeee; font-size: 12px; color: #888888; }
                    .footer a { color: #007bff; text-decoration: none; }
                </style>
            </head>
            <body>
                <div style="padding: 20px;">
                    <div class="container">
                        <div class="header">
                            <a href="https://blog.riteshrana.engineer"><img src="https://riteshrana.engineer/assets/RR.webp" alt="Ritesh Rana"></a>
                            <h1>Ritesh Rana Tech Blog</h1>
                            <p>Built by engineer, for engineers</p>
                        </div>
                        <div class="content">
                            ' . $body_content . '
                        </div>
                        <div class="footer">
                            <p>You received this because you subscribed to our newsletter.</p>
                            <p>
                                <a href="https://blog.riteshrana.engineer">Visit Blog</a> • 
                                <a href="https://riteshrana.engineer/unsubscribe.php?email=' . urlencode($email) . '">Unsubscribe</a>
                            </p>
                            <p style="margin-top: 10px; opacity: 0.7;">© ' . date("Y") . ' Ritesh Rana. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>';

            $headers = "MIME-Version: 1.0" . "\r\n";
            $headers .= "Content-Type: text/html; charset=UTF-8" . "\r\n";
            $headers .= "Content-Transfer-Encoding: base64" . "\r\n";
            $headers .= "From: Ritesh Rana <" . $SENDER_EMAIL . ">" . "\r\n";
            $headers .= "Reply-To: " . $SENDER_EMAIL . "\r\n";
            $headers .= "X-Mailer: PHP/" . phpversion();

            // Encode the body to base64 to avoid line length limits
            $encoded_body = chunk_split(base64_encode($full_body));

            // Send with base64 encoded subject and body
            if (mail($email, '=?UTF-8?B?' . base64_encode($subject) . '?=', $encoded_body, $headers, "-f" . $SENDER_EMAIL)) {
                $count++;
            }
        }
    }
    fclose($handle);
}

// 6. Update State
if ($count > 0) {
    file_put_contents($STATE_FILE, $unique_id);
    echo "Success: Sent '$title' to $count subscribers.\n";
} else {
    echo "Warning: No valid subscribers found or mail() failed.\n";
}
?>