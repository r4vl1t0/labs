<?php
$dir = __DIR__ . '/documentos';
$archivos = array_diff(scandir($dir), ['.', '..']);
$log = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion']) && $_POST['accion'] === 'duplicar') {
    $origen = $_POST['origen'] ?? '';
    $destino = $_POST['destino'] ?? '';
    if ($origen !== '' && $destino !== '') {
        $cmd = "cd documentos && cp " . $origen . " " . $destino . " 2>&1";
        $salida = shell_exec($cmd);
        $log = $salida !== null ? $salida : 'Operacion completada';
        $archivos = array_diff(scandir($dir), ['.', '..']);
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Panel de Documentos</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Gestion Documental - Copiado, duplicado y backup</span></div>
<div class="contenido">
<h2>Documentos disponibles</h2>
<table>
<tr><th>Archivo</th></tr>
<?php foreach ($archivos as $a): ?>
<tr><td><?php echo htmlspecialchars($a); ?></td></tr>
<?php endforeach; ?>
</table>

<h2>Duplicar documento</h2>
<p class="ayuda">Genera una copia de un documento existente con un nuevo nombre dentro del repositorio.</p>
<form method="POST" action="/index.php">
    <input type="hidden" name="accion" value="duplicar">
    <label>Documento origen</label>
    <select name="origen">
        <?php foreach ($archivos as $a): ?>
        <option value="<?php echo htmlspecialchars($a); ?>"><?php echo htmlspecialchars($a); ?></option>
        <?php endforeach; ?>
    </select>
    <label>Nombre del nuevo documento</label>
    <input type="text" name="destino" placeholder="copia_documento.txt" required>
    <button type="submit" style="margin-top:12px;">Duplicar</button>
</form>

<?php if ($log !== ''): ?>
<h3>Log de la operacion</h3>
<pre style="background:#111;color:#0f0;padding:16px;overflow:auto;"><?php echo htmlspecialchars($log); ?></pre>
<?php endif; ?>
</div>
</body>
</html>
