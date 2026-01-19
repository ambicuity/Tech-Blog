<?php
// server/admin_send.php
session_start();
require_once __DIR__ . '/utils.php';

// Configuration
$CSV_FILE = __DIR__ . '/subscribers.csv';
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
        // Regenerate session ID to prevent fixation
        session_regenerate_id(true);
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
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, system-ui, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f0f2f5;
                margin: 0;
            }

            .login-box {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
            }

            input {
                display: block;
                width: 100%;
                margin: 10px 0;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }

            button {
                width: 100%;
                padding: 12px;
                background: #0070f3;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
            }

            button:hover {
                background: #0051a2;
            }

            .error {
                color: #d32f2f;
                margin-bottom: 15px;
                padding: 10px;
                background: #ffebee;
                border-radius: 4px;
                font-size: 14px;
            }
        </style>
    </head>

    <body>
        <div class="login-box">
            <h2 style="text-align:center; margin-top:0;">Newsletter Login</h2>
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

// Handle Load Latest Posts (AJAX)
if (isset($_GET['action']) && $_GET['action'] == 'get_latest_posts') {
    header('Content-Type: application/json');
    $posts = getLatestPostsFromFeed('https://blog.riteshrana.engineer/feed.xml');

    if (empty($posts)) {
        echo json_encode(['error' => 'Failed to fetch posts']);
        exit;
    }

    $latest_post = $posts[0];

    // Generate HTML content for the body
    $content_html = "<h2>Here is what I've been writing about lately:</h2>";
    foreach ($posts as $post) {
        $content_html .= '<div class="post-preview">';
        $content_html .= '<a href="' . $post['link'] . '" class="post-title">' . $post['title'] . '</a>';
        $content_html .= '<div class="post-meta">New Post</div>';
        $content_html .= '<p>' . $post['description'] . '</p>';
        $content_html .= '<a href="' . $post['link'] . '" class="btn">Read Article</a>';
        $content_html .= '</div>';
    }

    echo json_encode([
        'subject' => "New on the Blog: " . $latest_post['title'],
        'body' => $content_html
    ]);
    exit;
}

// Handle Email Sending
$msg = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['send_email'])) {
    $subject = trim($_POST['subject']);
    $content = trim($_POST['body']); // Now this is just the inner content, not full HTML

    if (empty($subject) || empty($content)) {
        $msg = "<div class='error'>Subject and Body are required.</div>";
    } else {
        $emails = getSubscribers($CSV_FILE);
        $count = 0;

        foreach ($emails as $email) {
            $unsubscribe_link = "https://riteshrana.engineer/unsubscribe.php?email=" . urlencode($email);
            // Use shared template generator
            $full_body = generateEmailTemplate($content, $unsubscribe_link);

            if (sendNewsletter($email, $subject, $full_body, $SENDER_EMAIL)) {
                $count++;
            }
        }
        $msg = "<div class='success'>✅ Newsletter queued for $count subscribers.</div>";
    }
}
?>
<!DOCTYPE html>
<html>

<head>
    <title>Newsletter Admin Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, system-ui, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        h2 {
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 15px;
            margin-top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logout {
            font-size: 14px;
            color: #d32f2f;
            text-decoration: none;
            padding: 5px 10px;
            border: 1px solid #d32f2f;
            border-radius: 4px;
        }

        .logout:hover {
            background: #fee2e2;
        }

        input,
        textarea {
            width: 100%;
            margin: 10px 0 20px;
            padding: 12px;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            font-family: inherit;
            box-sizing: border-box;
        }

        textarea {
            height: 300px;
            resize: vertical;
            line-height: 1.5;
        }

        label {
            font-weight: 600;
            color: #24292e;
            display: block;
            margin-top: 20px;
        }

        button {
            padding: 12px 25px;
            background: #0070f3;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.2s;
        }

        button:hover {
            background: #0051a2;
        }

        #load-posts-btn {
            background: #2ea44f;
            margin-right: 10px;
        }

        #load-posts-btn:hover {
            background: #2c974b;
        }

        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }

        .helper-text {
            font-size: 12px;
            color: #666;
            margin-top: -15px;
            margin-bottom: 15px;
        }

        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
    </style>
</head>

<body>
    <div class="container">
        <h2>
            Admin Dashboard
            <a href="?action=logout" class="logout">Logout</a>
        </h2>

        <div class="stats">
            <strong>Subscribers:</strong> <?php echo count(getSubscribers($CSV_FILE)); ?>
        </div>

        <?php echo $msg; ?>

        <form method="post">
            <div style="display: flex; gap: 10px;">
                <button type="button" id="load-posts-btn" onclick="loadLatestPosts()">✨ Auto-Fill from Blog</button>
                <div id="loading" style="display:none; align-self: center; color: #666;">Loading...</div>
            </div>

            <label for="subject">Email Subject</label>
            <input type="text" id="subject" name="subject" placeholder="e.g., New Post: Kubernetes Best Practices"
                required>

            <label for="body">Email Content (HTML)</label>
            <p class="helper-text">This will be wrapped in the standard header/footer. Use &lt;h2&gt;, &lt;p&gt;, etc.
            </p>
            <textarea id="body" name="body" placeholder="Write your newsletter content here..." required></textarea>

            <button type="submit" name="send_email">🚀 Send Newsletter</button>
        </form>
    </div>

    <script>
        function loadLatestPosts() {
            const btn = document.getElementById('load-posts-btn');
            const loading = document.getElementById('loading');

            btn.disabled = true;
            loading.style.display = 'block';

            fetch('admin_send.php?action=get_latest_posts')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        document.getElementById('subject').value = data.subject;
                        document.getElementById('body').value = data.body;
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('Failed to load posts.');
                })
                .finally(() => {
                    btn.disabled = false;
                    loading.style.display = 'none';
                });
        }
    </script>
</body>

</html>