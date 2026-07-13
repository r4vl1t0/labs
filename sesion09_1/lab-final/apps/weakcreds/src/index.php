<?php
session_start();
if (isset($_SESSION['auth'])) {
    header('Location: /panel.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Sistema de Gestion</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="caja">
    <h1>Sistema de Gestion Interna</h1>
    <p class="subtitulo">Acceso restringido a personal autorizado</p>
    <?php if (isset($_GET['error'])): ?><p class="error">Usuario o contrasena incorrectos</p><?php endif; ?>
    <form method="POST" action="/login.php">
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Ingresar</button>
    </form>
</div>
</body>
</html>
