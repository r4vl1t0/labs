<?php
session_start();
if (isset($_SESSION['usuario_id'])) {
    header('Location: /facturas.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Portal de Clientes</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="caja-login">
    <h1>Portal de Clientes</h1>
    <p class="subtitulo">Acceso a facturacion y estado de cuenta</p>
    <?php if (isset($_GET['error'])): ?>
        <p class="error">Usuario o contrasena incorrectos</p>
    <?php endif; ?>
    <form method="POST" action="/login.php">
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Ingresar</button>
    </form>
    <p class="ayuda">Si no cuenta con acceso, comuniquese con su ejecutivo de cuenta.</p>
</div>
</body>
</html>
