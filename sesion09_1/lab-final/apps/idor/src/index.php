<?php
session_start();
if (isset($_SESSION['empleado_id'])) {
    header('Location: /legajo.php?id=' . $_SESSION['empleado_id']);
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Intranet Corporativa</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="caja">
    <h1>Intranet Corporativa</h1>
    <?php if (isset($_GET['error'])): ?><p class="error">Credenciales invalidas</p><?php endif; ?>
    <form method="POST" action="/login.php">
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Ingresar</button>
    </form>
    <p class="ayuda">¿Nuevo empleado? <a href="/registro.php">Crear cuenta</a></p>
</div>
</body>
</html>
