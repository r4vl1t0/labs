<?php
session_start();
require 'db.php';
if (!isset($_SESSION['admin_id'])) { header('Location: /admin/login.php'); exit; }
$id = intval($_GET['id'] ?? 0);
$conn = get_conn();
$stmt = $conn->prepare("SELECT t.id, t.asunto, t.mensaje, t.estado, t.fecha, u.nombre FROM tickets t JOIN usuarios u ON u.id = t.usuario_id WHERE t.id = ?");
$stmt->bind_param('i', $id);
$stmt->execute();
$t = $stmt->get_result()->fetch_assoc();
if ($t) {
    $upd = $conn->prepare("UPDATE tickets SET revisado = 1 WHERE id = ?");
    $upd->bind_param('i', $id);
    $upd->execute();
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Detalle de ticket</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Panel de administracion - Mesa de Ayuda</span><a href="/admin/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<?php if (!$t): ?>
    <p>Ticket no encontrado.</p>
<?php else: ?>
    <h2>Ticket #<?php echo $t['id']; ?> - <?php echo htmlspecialchars($t['asunto']); ?></h2>
    <p>Cliente: <?php echo htmlspecialchars($t['nombre']); ?> | Fecha: <?php echo htmlspecialchars($t['fecha']); ?></p>
    <div class="tarjeta">
        <?php echo $t['mensaje']; ?>
    </div>
<?php endif; ?>
<p><a href="/admin/tickets.php">Volver al listado</a></p>
</div>
</body>
</html>
