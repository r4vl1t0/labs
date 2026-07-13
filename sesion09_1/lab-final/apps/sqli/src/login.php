<?php
session_start();
require 'db.php';

$usuario = $_POST['usuario'] ?? '';
$password = $_POST['password'] ?? '';

$conn = get_conn();
$stmt = $conn->prepare("SELECT id, nombre FROM usuarios WHERE usuario = ? AND password = SHA2(?, 256)");
$stmt->bind_param('ss', $usuario, $password);
$stmt->execute();
$res = $stmt->get_result();

if ($row = $res->fetch_assoc()) {
    $_SESSION['usuario_id'] = $row['id'];
    $_SESSION['nombre'] = $row['nombre'];
    header('Location: /facturas.php');
} else {
    header('Location: /index.php?error=1');
}
