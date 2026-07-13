<?php
$resultado = null;
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $xml = '';
    if (isset($_FILES['archivo']) && $_FILES['archivo']['error'] === UPLOAD_ERR_OK) {
        $xml = file_get_contents($_FILES['archivo']['tmp_name']);
    } elseif (!empty($_POST['xml'])) {
        $xml = $_POST['xml'];
    }

    if ($xml !== '') {
        libxml_use_internal_errors(true);
        $dom = new DOMDocument();
        $ok = $dom->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD | LIBXML_DTDATTLOAD);
        if ($ok) {
            $proveedor = $dom->getElementsByTagName('proveedor')->item(0)?->nodeValue ?? '';
            $concepto = $dom->getElementsByTagName('concepto')->item(0)?->nodeValue ?? '';
            $monto = $dom->getElementsByTagName('monto')->item(0)?->nodeValue ?? '';
            $resultado = compact('proveedor', 'concepto', 'monto');
        } else {
            $error = 'El documento XML no pudo ser procesado, verifique el formato';
        }
    } else {
        $error = 'Debe adjuntar un archivo o pegar el contenido XML';
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Generador de Reportes</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Sistema de Reportes - Importacion XML</span></div>
<div class="contenido">
<h2>Importar reporte de proveedor</h2>
<p class="ayuda">Cargue un archivo XML con el formato esperado o pegue el contenido directamente.</p>
<div class="tarjeta">
<h3>Formato esperado</h3>
<pre style="background:#111;color:#0f0;padding:12px;overflow:auto;">&lt;reporte&gt;
  &lt;proveedor&gt;Nombre del proveedor&lt;/proveedor&gt;
  &lt;concepto&gt;Detalle del servicio&lt;/concepto&gt;
  &lt;monto&gt;150.00&lt;/monto&gt;
&lt;/reporte&gt;</pre>
</div>

<form method="POST" action="/index.php" enctype="multipart/form-data">
    <label>Archivo XML</label>
    <input type="file" name="archivo" accept=".xml">
    <label>O pegue el contenido XML</label>
    <textarea name="xml" rows="8" style="width:100%;padding:8px;box-sizing:border-box;"></textarea>
    <button type="submit" style="margin-top:12px;">Procesar reporte</button>
</form>

<?php if ($error): ?>
<p class="error"><?php echo htmlspecialchars($error); ?></p>
<?php endif; ?>

<?php if ($resultado): ?>
<h3>Reporte procesado</h3>
<table>
<tr><th>Proveedor</th><td><?php echo htmlspecialchars($resultado['proveedor']); ?></td></tr>
<tr><th>Concepto</th><td><?php echo htmlspecialchars($resultado['concepto']); ?></td></tr>
<tr><th>Monto</th><td><?php echo htmlspecialchars($resultado['monto']); ?></td></tr>
</table>
<?php endif; ?>
</div>
</body>
</html>
