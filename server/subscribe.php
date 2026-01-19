<?php
// subscribe.php - Upload this to your Namecheap VPS public_html folder

// Convert to a comma-separated list of allowed domains (CORS)
$allowed_origins = [
    "https://blog.riteshrana.engineer",
    "http://localhost:4000" // For local testing
];

$origin = $_SERVER['HTTP_ORIGIN'] ?? '';

if (in_array($origin, $allowed_origins)) {
    header("Access-Control-Allow-Origin: $origin");
    header("Access-Control-Allow-Methods: POST");
    header("Access-Control-Allow-Headers: Content-Type");
}

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $email = filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL);

    if ($email) {
        // Appending to a secure file outside public_html is best, but for simplicity:
        // Make sure 'subscribers.csv' is writable by the web server (chmod 666)
        $file = 'subscribers.csv';
        $entry = date('Y-m-d H:i:s') . "," . $email . "\n";
        
        if (file_put_contents($file, $entry, FILE_APPEND | LOCK_EX)) {
            echo json_encode(["status" => "success", "message" => "Subscribed successfully!"]);
        } else {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Server write error."]);
        }
    } else {
        http_response_code(400);
        echo json_encode(["status" => "error", "message" => "Invalid email address."]);
    }
}
?>
