<?php
session_start();
require 'db.php';
if (isset($_SESSION['admin_id'])) { header('Location: /admin/tickets.php'); exit; }
$err = isset($_GET['error']);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $usuario = $_POST['usuario'] ?? '';
    $password = $_POST['password'] ?? '';
    $conn = get_conn();
    $stmt = $conn->prepare("SELECT id FROM administradores WHERE usuario = ? AND password = SHA2(?,256)");
    $stmt->bind_param('ss', $usuario, $password);
    $stmt->execute();
    $res = $stmt->get_result();
    if ($row = $res->fetch_assoc()) {
        $_SESSION['admin_id'] = $row['id'];
        header('Location: /admin/tickets.php');
        exit;
    } else {
        header('Location: /admin/login.php?error=1');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Acceso administrador</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="caja">
    <h1>Panel de administracion</h1>
    <p class="subtitulo">Mesa de ayuda - acceso de personal de soporte</p>
    <?php if ($err): ?><p class="error">Credenciales invalidas</p><?php endif; ?>
    <form method="POST" action="/admin/login.php">
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Ingresar</button>
    </form>
</div>
</body>
</html>
