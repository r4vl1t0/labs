<?php
require 'data.php';

$porPagina = 10;
$totalPaginas = ceil(count($PRODUCTOS) / $porPagina);
$pagina = max(1, min($totalPaginas, intval($_GET['pagina'] ?? 1)));
$inicio = ($pagina - 1) * $porPagina;
$items = array_slice($PRODUCTOS, $inicio, $porPagina, true);
?>
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Catalogo - Distribuidora Andina</title><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="topbar"><span>Distribuidora Andina - Catalogo de productos</span></div>
<div class="contenido">
<h2>Productos (pagina <?php echo $pagina; ?> de <?php echo $totalPaginas; ?>)</h2>
<div class="grilla">
<?php foreach ($items as $id => $p): ?>
    <div class="tarjeta-producto">
        <h3><?php echo htmlspecialchars($p['nombre']); ?></h3>
        <p class="precio">S/ <?php echo number_format($p['precio'], 2); ?></p>
        <a href="/producto.php?id=<?php echo $id; ?>">Ver detalle</a>
    </div>
<?php endforeach; ?>
</div>
<div class="paginador">
    <?php if ($pagina > 1): ?><a href="/productos.php?pagina=<?php echo $pagina-1; ?>">Anterior</a><?php endif; ?>
    <span>Pagina <?php echo $pagina; ?> / <?php echo $totalPaginas; ?></span>
    <?php if ($pagina < $totalPaginas): ?><a href="/productos.php?pagina=<?php echo $pagina+1; ?>">Siguiente</a><?php endif; ?>
</div>
</div>
</body>
</html>
