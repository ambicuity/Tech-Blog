<?php
session_start();

// Configuration
$CSV_FILE = __DIR__ . '/subscribers.csv'; // Use absolute path for safety
// ⚠️ SECURITY: Use generate_hash.php to get this value!
$ADMIN_PASSWORD_HASH = '$2y$10$YourGeneratedHashGoesHere...'; // Replace with your actual hash
$SENDER_EMAIL = 'newsletter@riteshrana.engineer';

// Handle Logout
if (isset($_GET['action']) && $_GET['action'] == 'logout') {
    session_destroy();
    header("Location: admin_send.php");
    exit;
}

// Handle Login
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    if (password_verify($_POST['password'], $ADMIN_PASSWORD_HASH)) {
        $_SESSION['logged_in'] = true;
    } else {
        $error = "Invalid password";
    }
}

// Require Login
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    ?>
    <!DOCTYPE html>
    <html>

    <head>
        <title>Newsletter Admin Login</title>
        <style>
            body {
                font-family: sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f0f2f5;
            }

            .login-box {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            input {
                display: block;
                width: 100%;
                margin: 10px 0;
                padding: 10px;
            }

            button {
                width: 100%;
                padding: 10px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }

            button:hover {
                background: #0056b3;
            }

            .error {
                color: red;
                margin-bottom: 10px;
            }
        </style>
    </head>

    <body>
        <div class="login-box">
            <h2>Newsletter Login</h2>
            <?php if ($error)
                echo "<div class='error'>$error</div>"; ?>
            <form method="post">
                <input type="password" name="password" placeholder="Enter Password" required>
                <button type="submit" name="login">Login</button>
            </form>
        </div>
    </body>

    </html>
    <?php
    exit;
}

// Read Subscribers Helper
function getSubscribers($csv_file)
{
    $emails = [];
    if (file_exists($csv_file) && ($handle = fopen($csv_file, "r")) !== FALSE) {
        while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
            // Format is: Date, Email, IP
            // So Email is at index 1
            $email = trim($data[1] ?? '');
            if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
                // Return full data for display
                $emails[] = ['date' => $data[0] ?? '', 'email' => $email, 'ip' => $data[2] ?? ''];
            }
        }
        fclose($handle);
    }
    return $emails;
}

// Helper: Fetch RSS Feed
function getLatestPosts($limit = 3) {
    $feed_url = 'https://blog.riteshrana.engineer/feed.xml';
    $html = '';
    
    // Attempt to fetch feed
    $content = @file_get_contents($feed_url);
    if ($content) {
        $xml = @simplexml_load_string($content);
        if ($xml) {
            $count = 0;
            // Handle Atom feed (Jekyll default) or RSS 2.0
            $items = isset($xml->entry) ? $xml->entry : (isset($xml->channel->item) ? $xml->channel->item : []);
            
            $html .= "<h2>🔥 Latest Updates from the Blog</h2>";
            
            foreach ($items as $item) {
                if ($count >= $limit) break;
                
                // Extract fields (handle namespaces if needed, but basic access usually works)
                $title = (string)$item->title;
                $link = isset($item->link['href']) ? (string)$item->link['href'] : (string)$item->link;
                // Try summary, then content, then description
                $desc = (string)($item->summary ?? $item->content ?? $item->description ?? ''); 
                
                // Clean up description (strip tags, limit length)
                $desc_clean = strip_tags($desc);
                if (strlen($desc_clean) > 200) $desc_clean = substr($desc_clean, 0, 200) . '...';
                
                $html .= '<div style="margin-bottom: 25px; padding-bottom: 25px; border-bottom: 1px solid #eee;">';
                $html .= '<h3 style="margin-top: 0;"><a href="' . $link . '" style="color: #1e1e1e; text-decoration: none;">' . $title . '</a></h3>';
                $html .= '<p style="color: #555;">' . $desc_clean . '</p>';
                $html .= '<a href="' . $link . '" style="display: inline-block; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; font-size: 14px;">Read Article &rarr;</a>';
                $html .= '</div>';
                
                $count++;
            }
        } else {
            return "<p>Error parsing feed.</p>";
        }
    } else {
        return "<p>Could not fetch feed: $feed_url</p>";
    }
    return $html;
}

// Handle Sending
$message_status = '';
$prefill_body = '';

// Handle "Load Feed" Action
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['load_feed'])) {
    $prefill_body = getLatestPosts();
    $message_status = "<div class='success'>✅ Loaded latest posts!</div>";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['send'])) {
    $subject = $_POST['subject'] ?? '';
    $body_content = $_POST['body'] ?? '';

    if ($subject && $body_content) {
        if (!file_exists($CSV_FILE)) {
            $message_status = "<div class='error'>Subscribers file not found at: $CSV_FILE</div>";
        } else {
            $count = 0;
            $subscribers = getSubscribers($CSV_FILE);

            foreach ($subscribers as $sub) {
                $email = $sub['email'];

                // --- Professional Email Template ---
                $full_body = '<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body { margin: 0; padding: 0; background-color: #f4f4f4; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
                        .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
                        .header { background: #1e1e1e; padding: 30px 20px; text-align: center; }
                        .header img { width: 60px; height: 60px; border-radius: 50%; border: 3px solid #ffffff; vertical-align: middle; }
                        .header h1 { color: #ffffff; margin: 15px 0 5px 0; font-size: 24px; font-weight: 700; }
                        .header p { color: #aaaaaa; margin: 0; font-size: 14px; }
                        .content { padding: 30px; font-size: 16px; line-height: 1.6; color: #333333; }
                        .content h1, .content h2, .content h3 { color: #1e1e1e; margin-top: 0; }
                        .content img { max-width: 100%; border-radius: 4px; }
                        .footer { background: #f9f9f9; padding: 20px; text-align: center; border-top: 1px solid #eeeeee; font-size: 12px; color: #888888; }
                        .footer a { color: #007bff; text-decoration: none; }
                        .button { display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff !important; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 10px; }
                    </style>
                </head>
                <body>
                    <div style="padding: 20px;">
                        <div class="container">
                            <!-- Header -->
                            <div class="header">
                                <a href="https://blog.riteshrana.engineer" target="_blank">
                                    <img src="https://riteshrana.engineer/assets/RR.webp" alt="Ritesh Rana">
                                </a>
                                <h1>Ritesh Rana Tech Blog</h1>
                                <p>Built by engineer, for engineers</p>
                            </div>

                            <!-- Body Content -->
                            <div class="content">
                                ' . $body_content . '
                            </div>

                            <!-- Footer -->
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
                $headers .= "Content-type: text/html; charset=UTF-8" . "\r\n";
                $headers .= "From: Ritesh Rana <" . $SENDER_EMAIL . ">" . "\r\n";
                $headers .= "Reply-To: " . $SENDER_EMAIL . "\r\n";
                $headers .= "X-Mailer: PHP/" . phpversion();

                // '-f' parameter sets the Return-Path envelope address (critical for spam filters)
                if (mail($email, $subject, $full_body, $headers, "-f" . $SENDER_EMAIL)) {
                    $count++;
                }
            }
            $message_status = "<div class='success'>✅ Sent to $count subscribers!</div>";
        }
    } else {
        $message_status = "<div class='error'>Subject and Body are required.</div>";
    }
}

// Get list for viewing
$subscriber_list = getSubscribers($CSV_FILE);
?>

<!DOCTYPE html>
<html>

<head>
    <title>Send Newsletter</title>
    <style>
        body {
            font-family: sans-serif;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            background: #f9f9f9;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }

        h1,
        h2 {
            margin-top: 0;
        }

        label {
            font-weight: bold;
            display: block;
            margin-top: 15px;
        }

        input[type="text"],
        textarea {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }

        textarea {
            height: 300px;
            font-family: monospace;
        }

        button {
            margin-top: 20px;
            padding: 12px 24px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #218838;
        }

        .logout {
            float: right;
            color: #666;
            text-decoration: none;
        }

        .success {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        /* Tab/Section styling */
        .section {
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th,
        td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
            font-size: 0.9em;
        }

        th {
            background-color: #f2f2f2;
        }
    </style>
</head>

<body>
    <div class="container">
        <a href="?action=logout" class="logout">Logout</a>
        <h1>📨 Newsletter Dashboard</h1>

        <?= $message_status ?>

        <div class="section">
            <h2>Compose Email</h2>
            <div style="margin-bottom: 20px; text-align: right;">
                <form method="post" style="display: inline;">
                    <button type="submit" name="load_feed"
                        style="background: #17a2b8; width: auto; font-size: 14px; padding: 8px 16px; margin-top: 0;">🔄
                        Load Latest Posts from Blog</button>
                </form>
            </div>

            <form method="post"
                onsubmit="return confirm('Are you sure you want to send this to ALL <?= count($subscriber_list) ?> subscribers?');">
                <label for="subject">Subject:</label>
                <input type="text" name="subject" id="subject" placeholder="e.g., Weekly Roundup"
                    value="<?= isset($_POST['subject']) ? htmlspecialchars($_POST['subject']) : '' ?>" required>

                <label for="body">Email Body (HTML):</label>
                <textarea name="body" id="body" required placeholder="<h1>Hello!</h1>"
                    style="height: 400px;"><?= htmlspecialchars($prefill_body ?: ($_POST['body'] ?? '')) ?></textarea>

                <button type="submit" name="send">🚀 Send to <?= count($subscriber_list) ?> Subscribers</button>
            </form>
        </div>

        <div class="section">
            <h2>Current Subscribers (<?= count($subscriber_list) ?>)</h2>
            <?php if (empty($subscriber_list)): ?>
                <p>No subscribers found. (Checking file: <?= $CSV_FILE ?>)</p>
            <?php else: ?>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Email</th>
                        <th>IP (Partial)</th>
                    </tr>
                    <?php foreach ($subscriber_list as $sub): ?>
                        <tr>
                            <td><?= htmlspecialchars($sub['date']) ?></td>
                            <td><?= htmlspecialchars($sub['email']) ?></td>
                            <td><?= htmlspecialchars(substr($sub['ip'], 0, 7)) . '...' ?></td>
                        </tr>
                    <?php endforeach; ?>
                </table>
            <?php endif; ?>
        </div>
    </div>
</body>

</html>