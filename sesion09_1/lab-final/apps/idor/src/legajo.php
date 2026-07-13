<?php
session_start();
require 'db.php';
if (!isset($_SESSION['empleado_id'])) {
    header('Location: /index.php');
    exit;
}
$id = intval($_GET['id'] ?? $_SESSION['empleado_id']);
$conn = get_conn();
$stmt = $conn->prepare("SELECT nombre_completo, puesto, salario, nota_confidencial FROM empleados WHERE id = ?");
$stmt->bind_param('i', $id);
$stmt->execute();
$res = $stmt->get_result();
$emp = $res->fetch_assoc();
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Legajo</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Intranet Corporativa</span><a href="/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Legajo del empleado</h2>
<?php if (!$emp): ?>
    <p>No se encontro el legajo solicitado.</p>
<?php else: ?>
    <table>
        <tr><th>Nombre</th><td><?php echo htmlspecialchars($emp['nombre_completo']); ?></td></tr>
        <tr><th>Puesto</th><td><?php echo htmlspecialchars($emp['puesto']); ?></td></tr>
        <tr><th>Salario</th><td><?php echo $emp['salario'] !== null ? htmlspecialchars($emp['salario']) : 'No disponible'; ?></td></tr>
        <tr><th>Nota confidencial RRHH</th><td><?php echo $emp['nota_confidencial'] !== null ? htmlspecialchars($emp['nota_confidencial']) : '-'; ?></td></tr>
    </table>
<?php endif; ?>
<p class="ayuda">ID de legajo consultado: <?php echo $id; ?></p>
</div>
</body>
</html>
