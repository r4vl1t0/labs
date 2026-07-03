<?php
session_start();
if (!isset($_SESSION['usuario'])) {
    header('Location: login.php');
    exit;
}

$flag = ($_SESSION['saldo'] <= 0) ? 'FLAG{csrf_get_transfer_2026}' : null;
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
  <p><a href="/">Volver al indice</a> | <a href="logout.php">Cerrar sesion</a></p>
  <h1>Hola, <?php echo htmlspecialchars($_SESSION['usuario'], ENT_QUOTES, 'UTF-8'); ?></h1>
  <p>Cuenta: <?php echo htmlspecialchars($_SESSION['cuenta'], ENT_QUOTES, 'UTF-8'); ?></p>
  <p style="font-size:1.4rem;">Saldo: <strong>$<?php echo number_format($_SESSION['saldo'], 2); ?></strong></p>

  <?php if (!empty($_SESSION['ultimo_destino'])): ?>
    <p class="result">Ultima transferencia enviada a: <?php echo htmlspecialchars($_SESSION['ultimo_destino'], ENT_QUOTES, 'UTF-8'); ?></p>
  <?php endif; ?>

  <?php if ($flag): ?>
    <div class="challenge-box" style="border-color:#dc2626;background:#7f1d1d33;">
      <h3>Cuenta drenada</h3>
      <p>Lograste que el saldo llegara a cero. Flag: <code><?php echo $flag; ?></code></p>
    </div>
  <?php endif; ?>

  <h3 style="margin-top:24px;">Transferir fondos</h3>
  <form method="GET" action="transferir.php">
    <input type="text" name="destino" placeholder="Cuenta destino">
    <input type="number" name="monto" placeholder="Monto" min="1" max="<?php echo (int)$_SESSION['saldo']; ?>">
    <button type="submit">Transferir</button>
  </form>

  <form method="POST" action="reset.php" style="margin-top:16px;">
    <button type="submit" style="background:#dc2626;color:white;">Reiniciar saldo (1000)</button>
  </form>
</div>
</body>
</html>
