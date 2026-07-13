<?php
session_start();
if (!isset($_SESSION['admin_id'])) { header('Location: /admin/login.php'); exit; }
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Panel principal</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Panel de administracion - Mesa de Ayuda</span><a href="/admin/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Panel del administrador</h2>
<p>Sesion activa como administrador de soporte.</p>
<div class="tarjeta">
    <h3>Informacion sensible</h3>
    <p>LAB{stored_xss_roba_cookie_de_admin_bot}</p>
</div>
</div>
</body>
</html>
