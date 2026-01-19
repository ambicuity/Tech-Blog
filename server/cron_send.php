<?php
// server/cron_send.php

// Run via Cron Job (e.g., every hour): php /path/to/server/cron_send.php YOUR_SECRET_KEY
require_once __DIR__ . '/utils.php';

$SECRET_KEY = 'CHANGE_ME_ON_SERVER'; // ⚠️ CHANGE THIS on your server file manager!

// State file to track last sent post
$STATE_FILE = __DIR__ . '/last_sent_post.txt';
$CSV_FILE = __DIR__ . '/subscribers.csv';

// Security Check
if (php_sapi_name() !== 'cli') {
    // Also allow GET request with key for testing if not CLI
    $provided_key = $_GET['key'] ?? '';
    if ($provided_key !== $SECRET_KEY) {
        die("Error: Access Denied. Only CLI or valid Key allowed.");
    }
} else {
    // CLI Argument Check
    $provided_key = $argv[1] ?? '';
    if ($provided_key !== $SECRET_KEY) {
        die("Error: Access Denied. Invalid Key.");
    }
}

// 1. Get Latest Post
$posts = getLatestPostsFromFeed('https://blog.riteshrana.engineer/feed.xml');
if (empty($posts)) {
    die("No posts found in RSS feed.\n");
}

$latest_post = $posts[0];
$latest_guid = $latest_post['guid']; // Unique ID

// 2. Check State (Avoid Duplicates)
$last_sent_guid = '';
if (file_exists($STATE_FILE)) {
    $last_sent_guid = trim(file_get_contents($STATE_FILE));
}

if ($latest_guid === $last_sent_guid) {
    die("Skipping: Newsletter for this post ('$latest_guid') already sent.\n");
}

echo "New post detected: " . $latest_post['title'] . "\n";

// 3. Prepare Email
$subject = "New on the Blog: " . $latest_post['title'];

// Generate HTML Content (Intro Only)
$content_html = "<h2>Fresh off the press!</h2>";
$content_html .= '<div class="post-preview">';
$content_html .= '<a href="' . $latest_post['link'] . '" class="post-title">' . $latest_post['title'] . '</a>';
$content_html .= '<div class="post-meta">New Post</div>';
// Use the description we already cleaned in utils.php
$content_html .= '<p>' . $latest_post['description'] . '</p>';
$content_html .= '<a href="' . $latest_post['link'] . '" class="btn">Read Full Article</a>';
$content_html .= '</div>';

// 4. Send to Subscribers
$emails = getSubscribers($CSV_FILE);
$count = 0;

foreach ($emails as $email) {
    $unsubscribe_link = "https://riteshrana.engineer/unsubscribe.php?email=" . urlencode($email);
    // Use shared template generator
    $full_body = generateEmailTemplate($content_html, $unsubscribe_link);

    if (sendNewsletter($email, $subject, $full_body, 'newsletter@riteshrana.engineer')) {
        $count++;
        // Polite delay to avoid rate limits
        usleep(200000); // 0.2 seconds
    }
}

// 5. Update State
if ($count > 0) {
    file_put_contents($STATE_FILE, $latest_guid);
    echo "Success: Sent newsletter to $count subscribers.\n";
} else {
    echo "Warning: Attempted to send but 0 emails were successful (or no subscribers).\n";
}
?>