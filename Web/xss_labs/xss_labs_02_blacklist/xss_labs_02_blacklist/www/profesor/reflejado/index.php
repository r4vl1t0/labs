<?php
// ============================================================
// LABORATORIO 1 — XSS REFLEJADO — VERSIÓN PROFESOR
// ------------------------------------------------------------
// VULNERABILIDAD: el parámetro GET "q" se refleja directamente
// dentro del HTML de respuesta SIN sanitizar (sin htmlspecialchars).
// Esto permite inyectar HTML/JS que el navegador de la víctima
// ejecutará al visitar una URL manipulada.
// ============================================================

if (!isset($_COOKIE['flag'])) {
    setcookie('flag', 'FLAG{reflected_xss_demo_2026}', time() + 3600, '/');
}

$q = isset($_GET['q']) ? $_GET['q'] : '';
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Buscador — Modo Profesor</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner profesor">MODO PROFESOR — XSS Reflejado (Lab 1/6)</div>
<div class="container">
  <p><a href="/">&larr; volver al índice</a></p>
  <h1>🔍 Buscador de productos</h1>
  <p class="hint">
    Objetivo de la demo: mostrar cómo un parámetro de la URL
    (<code>?q=</code>) se inserta sin escapar dentro del HTML de respuesta.
  </p>

  <form method="GET">
    <input type="text" name="q" placeholder="Buscar producto...">
    <button type="submit">Buscar</button>
  </form>

  <?php if ($q !== ''): ?>
    <!-- VULNERABLE: se imprime $q tal cual, sin htmlspecialchars() -->
    <p class="result">Resultados para: <?php echo $q; ?></p>
  <?php endif; ?>

  <div class="payload-box">
    <h3>▶ Payload de ejemplo para la demo en vivo</h3>
    <code>?q=&lt;script&gt;alert(document.cookie)&lt;/script&gt;</code>
    <p>Alternativa (cuando el navegador filtra &lt;script&gt; en la barra):</p>
    <code>?q=&lt;img src=x onerror=alert(document.cookie)&gt;</code>
    <p style="margin-top:10px;">
      <a class="btn" href="?q=%3Cimg+src%3Dx+onerror%3Dalert(document.cookie)%3E">
        Ejecutar demo ahora
      </a>
    </p>
  </div>

  <div class="fix-box">
    <h3>🔧 Corrección (mostrar al final de la demo)</h3>
    <pre>&lt;?php echo htmlspecialchars($q, ENT_QUOTES, 'UTF-8'); ?&gt;</pre>
    <p>También conviene aplicar una Content-Security-Policy y validar el
    tipo de dato esperado en el parámetro.</p>
  </div>
</div>
</body>
</html>
