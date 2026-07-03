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
<title>BancoWeb - Reto Estudiante</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner estudiante">RETO ESTUDIANTE -- CSRF en transferencias (Lab 9/9)</div>
<div class="container">
  <p><a href="/">Volver al indice</a></p>
  <h1>BancoWeb - Iniciar sesion</h1>

  <div class="challenge-box">
    <h3>Reto</h3>
    <p>Inicia sesion con las credenciales de la victima, luego construye
    una pagina HTML por tu cuenta (fuera de este contenedor, en tu propia
    computadora) que fuerce una transferencia sin que la victima la haya
    autorizado explicitamente desde el formulario del banco.</p>
    <p>Objetivo final: dejar el saldo de la cuenta en cero.</p>
    <p><strong>Credenciales:</strong> usuario <code>victima</code> /
    contrasena <code>victima123</code></p>
  </div>

  <?php if ($error): ?>
    <p class="result" style="border-left-color:#dc2626;"><?php echo htmlspecialchars($error, ENT_QUOTES, 'UTF-8'); ?></p>
  <?php endif; ?>

  <form method="POST">
    <input type="text" name="usuario" placeholder="Usuario">
    <input type="password" name="password" placeholder="Contrasena">
    <button type="submit">Iniciar sesion</button>
  </form>
</div>
</body>
</html>
