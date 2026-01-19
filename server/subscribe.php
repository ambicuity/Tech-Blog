<?php
// subscribe.php - Upload this to your Namecheap VPS public_html folder

// Configuration
$allowed_origins = [
    "https://blog.riteshrana.engineer",
    "http://localhost:4000" // For local testing
];
$csv_file = 'subscribers.csv'; // Must be writable by web server (chmod 666)

// CORS Headers
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins)) {
    header("Access-Control-Allow-Origin: $origin");
    header("Access-Control-Allow-Methods: POST, OPTIONS");
    header("Access-Control-Allow-Headers: Content-Type");
} else {
    // Optional: Log unauthorized access attempts
    // error_log("Unauthorized origin: $origin");
}

// Handle Preflight Request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Handle POST Request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Read JSON input
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);

    // Sanitize and Validate Email
    $email = filter_var($data['email'] ?? '', FILTER_SANITIZE_EMAIL);

    if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
        // Prevent duplicates (Optional - simplistic check for small lists)
        // Note: For large lists, use a database or hash map.
        $current_content = file_exists($csv_file) ? file_get_contents($csv_file) : '';
        if (strpos($current_content, $email) !== false) {
            echo json_encode(["status" => "success", "message" => "You're already subscribed!"]);
            exit;
        }

        // Append to CSV: Date, Email, IP (Optional for auditing)
        $entry = date('Y-m-d H:i:s') . "," . $email . "," . $_SERVER['REMOTE_ADDR'] . "\n";

        if (file_put_contents($csv_file, $entry, FILE_APPEND | LOCK_EX)) {
            echo json_encode(["status" => "success", "message" => "Subscribed successfully!"]);
        } else {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Server write error. Please check file permissions."]);
        }
    } else {
        http_response_code(400);
        echo json_encode(["status" => "error", "message" => "Invalid email format."]);
    }
} else {
    http_response_code(405); // Method Not Allowed
    echo json_encode(["status" => "error", "message" => "Method not allowed."]);
}
?>