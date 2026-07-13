<?php
session_start();
require 'db.php';

if (!isset($_SESSION['usuario_id'])) {
    header('Location: /index.php');
    exit;
}

$conn = get_conn();
$uid = intval($_SESSION['usuario_id']);
$buscar = $_GET['buscar'] ?? '';

$resultados = [];
$error_sql = '';

if ($buscar !== '') {
    $query = "SELECT numero, concepto, monto, fecha FROM facturas WHERE usuario_id = $uid AND concepto LIKE '%$buscar%'";
    $res = $conn->query($query);
    if ($res) {
        while ($r = $res->fetch_assoc()) {
            $resultados[] = $r;
        }
    } else {
        $error_sql = 'La busqueda no pudo completarse';
    }
} else {
    $res = $conn->query("SELECT numero, concepto, monto, fecha FROM facturas WHERE usuario_id = $uid");
    while ($r = $res->fetch_assoc()) {
        $resultados[] = $r;
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Mis Facturas</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="topbar">
    <span>Portal de Clientes - <?php echo htmlspecialchars($_SESSION['nombre']); ?></span>
    <a href="/logout.php">Cerrar sesion</a>
</div>
<div class="contenido">
    <h2>Estado de cuenta</h2>
    <form method="GET" action="/facturas.php" class="buscador">
        <input type="text" name="buscar" placeholder="Buscar por concepto" value="<?php echo htmlspecialchars($buscar); ?>">
        <button type="submit">Buscar</button>
    </form>
    <?php if ($error_sql): ?>
        <p class="error"><?php echo $error_sql; ?></p>
    <?php endif; ?>
    <table>
        <tr><th>Numero</th><th>Concepto</th><th>Monto</th><th>Fecha</th></tr>
        <?php foreach ($resultados as $f): ?>
        <tr>
            <td><?php echo $f['numero']; ?></td>
            <td><?php echo $f['concepto']; ?></td>
            <td><?php echo $f['monto']; ?></td>
            <td><?php echo $f['fecha']; ?></td>
        </tr>
        <?php endforeach; ?>
    </table>
</div>
</body>
</html>
