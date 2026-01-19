<?php
$CSV_FILE = 'subscribers.csv';
$email_to_remove = $_GET['email'] ?? '';

$message = '';

if ($email_to_remove && filter_var($email_to_remove, FILTER_VALIDATE_EMAIL)) {
    if (file_exists($CSV_FILE)) {
        $temp_csv = [];
        $found = false;

        if (($handle = fopen($CSV_FILE, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                // If this is NOT the email to remove, keep it
                if ($data[0] !== $email_to_remove) {
                    $temp_csv[] = $data;
                } else {
                    $found = true;
                }
            }
            fclose($handle);
        }

        if ($found) {
            // Rewrite the file
            $fp = fopen($CSV_FILE, 'w');
            foreach ($temp_csv as $fields) {
                fputcsv($fp, $fields);
            }
            fclose($fp);
            $message = "You have been successfully unsubscribed.";
        } else {
            $message = "Email not found in our list.";
        }
    } else {
        $message = "Subscriber list not found.";
    }
} elseif ($email_to_remove) {
    $message = "Invalid email address.";
} else {
    $message = "No email provided.";
}
?>

<!DOCTYPE html>
<html>

<head>
    <title>Unsubscribe</title>
    <style>
        body {
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            color: #333;
        }

        .box {
            padding: 40px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
    </style>
</head>

<body>
    <div class="box">
        <h2>Unsubscribe</h2>
        <p>
            <?= htmlspecialchars($message) ?>
        </p>
        <p><a href="https://blog.riteshrana.engineer">Return to Blog</a></p>
    </div>
</body>

</html>