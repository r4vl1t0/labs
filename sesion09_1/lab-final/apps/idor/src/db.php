<?php
function get_conn() {
    $conn = new mysqli('mysql', 'root', 'rootpass123', 'intranet');
    if ($conn->connect_error) {
        die('Error de conexion');
    }
    return $conn;
}
