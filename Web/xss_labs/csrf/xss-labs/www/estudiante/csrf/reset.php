<?php
session_start();
if (isset($_SESSION['usuario'])) {
    $_SESSION['saldo'] = 1000;
    unset($_SESSION['ultimo_destino']);
}
header('Location: banco.php');
exit;
