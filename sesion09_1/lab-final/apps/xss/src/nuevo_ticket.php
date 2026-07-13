<?php
session_start();
require 'db.php';
if (!isset($_SESSION['usuario_id'])) { header('Location: /index.php'); exit; }
$err = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $asunto = trim($_POST['asunto'] ?? '');
    $mensaje = $_POST['mensaje'] ?? '';
    if ($asunto === '' || $mensaje === '') {
        $err = 'Complete todos los campos';
    } else {
        $conn = get_conn();
        $stmt = $conn->prepare("INSERT INTO tickets (usuario_id, asunto, mensaje) VALUES (?, ?, ?)");
        $stmt->bind_param('iss', $_SESSION['usuario_id'], $asunto, $mensaje);
        $stmt->execute();
        header('Location: /mis_tickets.php');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Nuevo ticket</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Mesa de Ayuda</span><a href="/logout.php">Cerrar sesion</a></div>
<div class="contenido">
<h2>Crear nuevo ticket</h2>
<?php if ($err): ?><p class="error"><?php echo htmlspecialchars($err); ?></p><?php endif; ?>
<form method="POST" action="/nuevo_ticket.php">
    <label>Asunto</label>
    <input type="text" name="asunto" required style="width:100%;padding:8px;box-sizing:border-box;">
    <label>Mensaje</label>
    <textarea name="mensaje" rows="6" required style="width:100%;padding:8px;box-sizing:border-box;"></textarea>
    <button type="submit" style="margin-top:12px;">Enviar ticket</button>
</form>
<p class="ayuda">Los tickets son revisados por el equipo de soporte en un plazo de minutos.</p>
<p><a href="/mis_tickets.php">Volver a mis tickets</a></p>
</div>
</body>
</html>
