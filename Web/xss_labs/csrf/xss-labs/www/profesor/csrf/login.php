<?php
session_start();

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $usuario  = $_POST['usuario']  ?? '';
    $password = $_POST['password'] ?? '';
    if ($usuario === 'victima' && $password === 'victima123') {
        $_SESSION['usuario'] = 'victima';
        $_SESSION['cuenta']  = '1111-2222';
        $_SESSION['saldo']   = 1000;
        header('Location: banco.php');
        exit;
    } else {
        $error = 'Usuario o contrasena incorrectos.';
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>BancoWeb - Modo Profesor</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner profesor">MODO PROFESOR -- CSRF en transferencias (Lab 8/9)</div>
<div class="container">
  <p><a href="/">Volver al indice</a></p>
  <h1>BancoWeb - Iniciar sesion</h1>
  <p class="hint">
    Esta cuenta representa a la "victima". Inicia sesion para dejar activa
    su sesion, luego abre <code>exploit.html</code> en otra pestana para
    mostrar el ataque.
  </p>

  <?php if ($error): ?>
    <p class="result" style="border-left-color:#dc2626;"><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></p>
  <?php endif; ?>

  <form method="POST">
    <input type="text" name="usuario" placeholder="Usuario" value="victima">
    <input type="password" name="password" placeholder="Contrasena" value="victima123">
    <button type="submit">Iniciar sesion</button>
  </form>

  <div class="payload-box">
    <h3>Credenciales de la demo</h3>
    <code>usuario: victima / contrasena: victima123</code>
    <p style="margin-top:10px;">
      Una vez dentro, abre en otra pestana:
      <a href="exploit.html">exploit.html</a> (simula un sitio malicioso
      externo) y luego vuelve a <a href="banco.php">banco.php</a> para ver
      el saldo afectado.
    </p>
  </div>
</div>
</body>
</html>
