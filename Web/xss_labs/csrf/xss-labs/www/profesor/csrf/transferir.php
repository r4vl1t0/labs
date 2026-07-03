<?php
session_start();
if (!isset($_SESSION['usuario'])) {
    header('Location: login.php');
    exit;
}

// ============================================================
// VULNERABLE A CSRF
// ------------------------------------------------------------
// Esta accion cambia el estado (mueve dinero) pero:
//   1. Se ejecuta via GET (deberia ser POST).
//   2. No valida ningun token anti-CSRF.
//   3. No valida el header Origin/Referer.
// Cualquier pagina externa puede forzar esta peticion mientras
// la victima tenga una sesion activa en este sitio.
// ============================================================

$monto   = isset($_GET['monto']) ? (float)$_GET['monto'] : 0;
$destino = isset($_GET['destino']) ? $_GET['destino'] : '';

if ($monto > 0 && $monto <= $_SESSION['saldo'] && $destino !== '') {
    $_SESSION['saldo'] -= $monto;
    $_SESSION['ultimo_destino'] = $destino;
}

header('Location: banco.php');
exit;
