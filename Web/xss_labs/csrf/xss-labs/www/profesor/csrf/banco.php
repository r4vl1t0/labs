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
<title>BancoWeb - Modo Profesor</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner profesor">MODO PROFESOR -- CSRF en transferencias (Lab 8/9)</div>
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
      <p>El saldo llego a cero mediante una transferencia forzada. Flag: <code><?php echo $flag; ?></code></p>
    </div>
  <?php endif; ?>

  <h3 style="margin-top:24px;">Transferir fondos</h3>
  <p class="hint">
    Nota para la demo: este formulario legitimo usa GET y no incluye
    ningun token anti-CSRF. Cualquier peticion GET con estos mismos
    parametros produce el mismo efecto, venga o no del formulario.
  </p>
  <form method="GET" action="transferir.php">
    <input type="text" name="destino" placeholder="Cuenta destino">
    <input type="number" name="monto" placeholder="Monto" min="1" max="<?php echo (int)$_SESSION['saldo']; ?>">
    <button type="submit">Transferir</button>
  </form>

  <div class="payload-box">
    <h3>URL vulnerable (para la demo)</h3>
    <code>/profesor/csrf/transferir.php?monto=1000&amp;destino=ATACANTE-9999</code>
    <p>Esta misma URL, cargada desde <code>exploit.html</code> mientras la
    victima tiene sesion activa, ejecuta la transferencia sin su
    consentimiento.</p>
  </div>

  <div class="fix-box">
    <h3>Correccion (mostrar al final de la demo)</h3>
    <pre>// 1. Usar POST para acciones que cambian estado (nunca GET)
// 2. Generar un token CSRF unico por sesion y validarlo en el servidor
if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'] ?? '')) {
    die('Token CSRF invalido');
}
// 3. Cookie de sesion con SameSite=Lax o Strict
session_set_cookie_params(['samesite' => 'Strict']);</pre>
  </div>

  <form method="POST" action="reset.php" style="margin-top:16px;">
    <button type="submit" style="background:#dc2626;color:white;">Reiniciar saldo (1000)</button>
  </form>
</div>
</body>
</html>
