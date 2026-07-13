<?php
session_start();
if (isset($_SESSION['usuario_id'])) {
    header('Location: /mis_tickets.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Mesa de Ayuda</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="caja">
    <h1>Mesa de Ayuda</h1>
    <p class="subtitulo">Sistema de tickets de soporte</p>
    <?php if (isset($_GET['error'])): ?><p class="error">Usuario o contrasena incorrectos</p><?php endif; ?>
    <form method="POST" action="/login.php">
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Ingresar</button>
    </form>
    <p class="ayuda">¿Primera vez? <a href="/registro.php">Crear cuenta</a></p>
</div>
</body>
</html>
