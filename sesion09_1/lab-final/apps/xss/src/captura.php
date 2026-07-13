<?php
$archivo = __DIR__ . '/logs/captura.log';
$contenido = file_exists($archivo) ? file_get_contents($archivo) : '(sin registros todavia)';
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Registros capturados</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="contenido">
<h2>Registros capturados en log.php</h2>
<pre style="background:#111;color:#0f0;padding:16px;overflow:auto;"><?php echo htmlspecialchars($contenido); ?></pre>
</div>
</body>
</html>
