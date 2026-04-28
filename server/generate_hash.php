<?php
// Generates a secure hash for a password
$password = $_POST['password'] ?? 'ChangeMe123!';
$hash = password_hash($password, PASSWORD_DEFAULT);
?>
<!DOCTYPE html>
<html>

<head>
    <title>Hash Generator</title>
</head>

<body>
    <h2>Password Hashing Tool</h2>
    <p><strong>Password:</strong>
        <?= htmlspecialchars($password) ?>
    </p>
    <p><strong>Hash:</strong> <code style="background:#eee;padding:5px;"><?= $hash ?></code></p>
    <p><em>Copy the hash above and paste it into <code>$ADMIN_PASSWORD_HASH</code> in <code>admin_send.php</code>.</em>
    </p>
    <hr>
    <form method="post">
        <input type="text" name="password" placeholder="Enter new password" required>
        <button type="submit">Generate Hash</button>
    </form>
</body>

</html>