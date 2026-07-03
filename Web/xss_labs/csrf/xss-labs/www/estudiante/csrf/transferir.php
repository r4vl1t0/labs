<?php
session_start();
if (!isset($_SESSION['usuario'])) {
    header('Location: login.php');
    exit;
}

// Vulnerable a CSRF: sin token, via GET, sin validar Origin/Referer.

$monto   = isset($_GET['monto']) ? (float)$_GET['monto'] : 0;
$destino = isset($_GET['destino']) ? $_GET['destino'] : '';

if ($monto > 0 && $monto <= $_SESSION['saldo'] && $destino !== '') {
    $_SESSION['saldo'] -= $monto;
    $_SESSION['ultimo_destino'] = $destino;
}

header('Location: banco.php');
exit;
