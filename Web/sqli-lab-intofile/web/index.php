<?php
// ============================================================
// LABORATORIO SQLi - INTO OUTFILE / LOAD_FILE
// Esta aplicación es INTENCIONALMENTE vulnerable. Solo con fines
// educativos, en un entorno aislado (docker-compose).
// ============================================================

$mysqli = new mysqli('db', 'labuser', 'labpass', 'labdb');
if ($mysqli->connect_errno) {
    die('Error de conexión: ' . $mysqli->connect_error);
}

$id = isset($_GET['id']) ? $_GET['id'] : '1';

// VULNERABLE A PROPÓSITO: concatenación directa del parámetro
// de usuario dentro de la consulta SQL, sin prepared statements
// ni sanitización.
$query = "SELECT id, name, description FROM products WHERE id = $id";

$result = $mysqli->query($query);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Tienda vulnerable - Laboratorio SQLi</title>
    <style>
        body { font-family: sans-serif; margin: 40px; background: #f4f4f4; }
        table { border-collapse: collapse; width: 100%; background: #fff; }
        th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
        th { background: #333; color: #fff; }
        .box { background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 6px; }
        code { background: #eee; padding: 2px 5px; }
    </style>
</head>
<body>
    <h1>Catálogo de productos</h1>

    <div class="box">
        <form method="GET">
            <label>Buscar producto por ID:
                <input type="text" name="id" value="<?php echo htmlspecialchars($id); ?>">
            </label>
            <button type="submit">Buscar</button>
        </form>
        <p>Consulta ejecutada: <code><?php echo htmlspecialchars($query); ?></code></p>
    </div>

    <table>
        <tr><th>ID</th><th>Nombre</th><th>Descripción</th></tr>
        <?php if ($result && $result->num_rows > 0): ?>
            <?php while ($row = $result->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['id']); ?></td>
                    <td><?php echo htmlspecialchars($row['name']); ?></td>
                    <td><?php echo htmlspecialchars($row['description']); ?></td>
                </tr>
            <?php endwhile; ?>
        <?php else: ?>
            <tr><td colspan="3">Sin resultados (o la consulta falló).</td></tr>
        <?php endif; ?>
    </table>

    <p style="margin-top:30px;color:#888;">Laboratorio SQLi con fines educativos.</p>
</body>
</html>
