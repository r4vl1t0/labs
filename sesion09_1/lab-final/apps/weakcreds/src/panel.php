<?php
session_start();
if (!isset($_SESSION['auth'])) {
    header('Location: /index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Panel de Gestion</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Sistema de Gestion Interna</span><a href="/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Panel principal</h2>
<p>Bienvenido, se han cargado 3 modulos disponibles: Inventario, Pedidos, Reportes.</p>
<div class="tarjeta">
    <h3>Aviso interno</h3>
    <p>LAB{admin_admin_credenciales_por_defecto}</p>
</div>
</div>
</body>
</html>
