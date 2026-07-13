<?php
session_start();
$usuario = $_POST['usuario'] ?? '';
$password = $_POST['password'] ?? '';
if ($usuario === 'admin' && $password === 'admin') {
    $_SESSION['auth'] = true;
    header('Location: /panel.php');
} else {
    header('Location: /index.php?error=1');
}
