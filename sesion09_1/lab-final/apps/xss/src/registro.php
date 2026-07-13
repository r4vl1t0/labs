<?php
session_start();
require 'db.php';
$err = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $usuario = trim($_POST['usuario'] ?? '');
    $password = $_POST['password'] ?? '';
    $nombre = trim($_POST['nombre'] ?? '');
    if ($usuario === '' || $password === '' || $nombre === '') {
        $err = 'Complete todos los campos';
    } else {
        $conn = get_conn();
        $stmt = $conn->prepare("INSERT INTO usuarios (usuario, password, nombre) VALUES (?, SHA2(?,256), ?)");
        $stmt->bind_param('sss', $usuario, $password, $nombre);
        if ($stmt->execute()) {
            header('Location: /index.php');
            exit;
        } else {
            $err = 'El usuario ya existe';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Crear cuenta</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="caja">
    <h1>Crear cuenta</h1>
    <?php if ($err): ?><p class="error"><?php echo htmlspecialchars($err); ?></p><?php endif; ?>
    <form method="POST" action="/registro.php">
        <label>Nombre</label>
        <input type="text" name="nombre" required>
        <label>Usuario</label>
        <input type="text" name="usuario" required>
        <label>Contrasena</label>
        <input type="password" name="password" required>
        <button type="submit">Registrarme</button>
    </form>
</div>
</body>
</html>
