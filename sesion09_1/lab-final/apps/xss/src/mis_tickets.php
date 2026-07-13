<?php
session_start();
require 'db.php';
if (!isset($_SESSION['usuario_id'])) { header('Location: /index.php'); exit; }
$conn = get_conn();
$stmt = $conn->prepare("SELECT id, asunto, estado, fecha FROM tickets WHERE usuario_id = ? ORDER BY fecha DESC");
$stmt->bind_param('i', $_SESSION['usuario_id']);
$stmt->execute();
$res = $stmt->get_result();
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Mis tickets</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Mesa de Ayuda - <?php echo htmlspecialchars($_SESSION['nombre']); ?></span><a href="/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Mis tickets</h2>
<p><a href="/nuevo_ticket.php">Crear nuevo ticket</a></p>
<table>
<tr><th>ID</th><th>Asunto</th><th>Estado</th><th>Fecha</th></tr>
<?php while ($t = $res->fetch_assoc()): ?>
<tr>
    <td>#<?php echo $t['id']; ?></td>
    <td><?php echo htmlspecialchars($t['asunto']); ?></td>
    <td><?php echo htmlspecialchars($t['estado']); ?></td>
    <td><?php echo htmlspecialchars($t['fecha']); ?></td>
</tr>
<?php endwhile; ?>
</table>
</div>
</body>
</html>
