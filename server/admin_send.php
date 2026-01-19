<?php
session_start();

// Configuration
$CSV_FILE = 'subscribers.csv';
// ⚠️ SECURITY: Use generate_hash.php to get this value!
// Default for 'admin123' is NOT provided here for security. You must generate it.
$ADMIN_PASSWORD_HASH = '$2y$10$YourGeneratedHashGoesHere...';
$SENDER_EMAIL = 'newsletter@riteshrana.engineer'; // Update this to your sending email

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
                box-sizing: border-box;
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

// Handle Sending
$message_status = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['send'])) {
    $subject = $_POST['subject'] ?? '';
    // Use the raw HTML from the textarea
    $body_content = $_POST['body'] ?? '';

    if ($subject && $body_content) {
        if (!file_exists($CSV_FILE)) {
            $message_status = "<div class='error'>Subscribers file not found!</div>";
        } else {
            $count = 0;
            if (($handle = fopen($CSV_FILE, "r")) !== FALSE) {
                while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                    $email = $data[0]; // Assuming email is the first column
                    if (filter_var($email, FILTER_VALIDATE_EMAIL)) {

                        // Construct the email with an unsubscribe footer
                        // Note: In a real system, unsubscribe should be a unique link.
                        // For this simple version, we just add a text footer.
                        $full_body = "<html><body>";
                        $full_body .= $body_content;
                        $full_body .= "<hr><small>You are receiving this because you subscribed to riteshrana.engineer. <a href='https://riteshrana.engineer/unsubscribe.php?email=" . urlencode($email) . "'>Unsubscribe</a></small>";
                        $full_body .= "</body></html>";

                        $headers = "MIME-Version: 1.0" . "\r\n";
                        $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
                        $headers .= "From: " . $SENDER_EMAIL . "\r\n";

                        // Send
                        if (mail($email, $subject, $full_body, $headers)) {
                            $count++;
                        }
                    }
                }
                fclose($handle);
            }
            $message_status = "<div class='success'>✅ Sent to $count subscribers!</div>";
        }
    } else {
        $message_status = "<div class='error'>Subject and Body are required.</div>";
    }
}
?>

<!DOCTYPE html>
<html>

<head>
    <title>Send Newsletter</title>
    <style>
        body {
            font-family: sans-serif;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            background: #f9f9f9;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }

        h1 {
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

        .preview-hint {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>

<body>
    <div class="container">
        <a href="?action=logout" class="logout">Logout</a>
        <h1>📨 Send Newsletter</h1>

        <?= $message_status ?>

        <form method="post" onsubmit="return confirm('Are you sure you want to send this to ALL subscribers?');">
            <label for="subject">Subject:</label>
            <input type="text" name="subject" id="subject" placeholder="e.g., New Post: Automated Canary Deploys"
                required>

            <label for="body">Email Body (HTML):</label>
            <p class="preview-hint">You can use standard HTML tags like &lt;h1&gt;, &lt;p&gt;, &lt;a href="..."&gt;,
                &lt;img src="..."&gt;.</p>
            <textarea name="body" id="body" required
                placeholder="<h1>Hello Subscriber!</h1><p>Check out my new post...</p>"></textarea>

            <button type="submit" name="send">🚀 Send Newsletter</button>
        </form>
    </div>
</body>

</html>