<?php
session_start();
require 'db.php';
if (!isset($_SESSION['admin_id'])) { header('Location: /admin/login.php'); exit; }
$conn = get_conn();
$res = $conn->query("SELECT t.id, t.asunto, t.estado, t.revisado, t.fecha, u.nombre FROM tickets t JOIN usuarios u ON u.id = t.usuario_id ORDER BY t.fecha DESC");
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Tickets - Administracion</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Panel de administracion - Mesa de Ayuda</span><a href="/admin/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Tickets recibidos</h2>
<table>
<tr><th>ID</th><th>Cliente</th><th>Asunto</th><th>Estado</th><th>Revisado</th><th>Fecha</th></tr>
<?php while ($t = $res->fetch_assoc()): ?>
<tr>
    <td><a href="/admin/ticket.php?id=<?php echo $t['id']; ?>">#<?php echo $t['id']; ?></a></td>
    <td><?php echo htmlspecialchars($t['nombre']); ?></td>
    <td><?php echo htmlspecialchars($t['asunto']); ?></td>
    <td><?php echo htmlspecialchars($t['estado']); ?></td>
    <td><?php echo $t['revisado'] ? 'Si' : 'No'; ?></td>
    <td><?php echo htmlspecialchars($t['fecha']); ?></td>
</tr>
<?php endwhile; ?>
</table>
</div>
</body>
</html>
