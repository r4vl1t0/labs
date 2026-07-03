<?php
// ============================================================
// LABORATORIO 7 -- XSS REFLEJADO CON BLACKLIST -- ESTUDIANTE
// ------------------------------------------------------------
// El parametro "q" se refleja en la pagina, pero antes pasa por
// un filtro de blacklist que bloquea ciertas etiquetas y eventos
// HTML considerados "peligrosos". El filtro NO cubre todos los
// casos posibles: hay que fuzzear distintas etiquetas y atributos
// de evento hasta encontrar una combinacion que el filtro no
// detecte.
// ============================================================

if (!isset($_COOKIE['flag'])) {
    setcookie('flag', 'FLAG{blacklist_bypass_2026}', time() + 3600, '/');
}

// Blacklist de patrones bloqueados (coincidencia exacta de subcadena,
// sensible a mayusculas/minusculas).
$blacklist = [
    '<script', '<img', '<iframe', '<svg', '<body',
    '<object', '<embed', '<form', '<input', '<video', '<audio',
    'onerror', 'onload', 'onclick',
    'javascript:', 'eval(', 'document.write',
];

$q = isset($_GET['q']) ? $_GET['q'] : '';
$bloqueado = false;
$patron = '';

if ($q !== '') {
    foreach ($blacklist as $malo) {
        if (strpos($q, $malo) !== false) {
            $bloqueado = true;
            $patron = $malo;
            break;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Comentarios del producto - Reto Estudiante</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner estudiante">RETO ESTUDIANTE -- XSS Reflejado con Blacklist (Lab 7)</div>
<div class="container">
  <p><a href="/">Volver al indice</a></p>
  <h1>Buscar comentarios de producto</h1>

  <div class="challenge-box">
    <h3>Reto</h3>
    <p>Este buscador filtra el parametro <code>q</code> contra una lista
    negra de etiquetas y atributos antes de mostrarlo en la pagina. Tu
    objetivo es lograr que el navegador ejecute JavaScript y muestre en
    un <code>alert()</code> el valor de la cookie <code>flag</code>.</p>
    <p>Metodologia sugerida: prueba una etiqueta HTML a la vez
    (por ejemplo <code>&lt;svg&gt;</code>, <code>&lt;img&gt;</code>,
    <code>&lt;body&gt;</code>, <code>&lt;details&gt;</code>,
    <code>&lt;marquee&gt;</code>, <code>&lt;select&gt;</code>...) y observa
    si el filtro la bloquea o no. El sistema te indica exactamente que
    patron detecto, usa esa informacion para mapear la blacklist completa.
    Una vez que encuentres una etiqueta que no este bloqueada, busca un
    atributo de evento que tampoco lo este.</p>
  </div>

  <form method="GET">
    <input type="text" name="q" placeholder="Buscar comentarios...">
    <button type="submit">Buscar</button>
  </form>

  <?php if ($q !== '' && $bloqueado): ?>
    <p class="result" style="border-left-color:#dc2626;">
      Entrada bloqueada por el filtro de seguridad.<br>
      Patron detectado: <code><?php echo htmlspecialchars($patron, ENT_QUOTES, 'UTF-8'); ?></code>
    </p>
  <?php elseif ($q !== ''): ?>
    <p class="result">Resultados para: <?php echo $q; ?></p>
  <?php endif; ?>
</div>
</body>
</html>
