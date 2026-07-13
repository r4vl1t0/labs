<?php
require 'data.php';
$id = intval($_GET['id'] ?? 0);
$p = $PRODUCTOS[$id] ?? null;
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Detalle de producto</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Distribuidora Andina - Catalogo de productos</span></div>
<div class="contenido">
<?php if (!$p): ?>
    <p>Producto no encontrado.</p>
<?php else: ?>
    <h2><?php echo htmlspecialchars($p['nombre']); ?></h2>
    <p class="precio">S/ <?php echo number_format($p['precio'], 2); ?></p>
    <p><?php echo htmlspecialchars($p['descripcion']); ?></p>
    <p>Categoria: <?php echo htmlspecialchars($p['categoria']); ?></p>
    <p>Stock disponible: <?php echo $p['stock']; ?> unidades</p>
    <?php if ($id === 173): ?>
    <!-- nota interna equipo catalogo: pendiente revisar precio, referencia ticket LAB{scraping_html_comment_pag_173} -->
    <?php endif; ?>
<?php endif; ?>
<p><a href="/productos.php">Volver al catalogo</a></p>
</div>
</body>
</html>
