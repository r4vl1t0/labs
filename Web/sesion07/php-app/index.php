<?php
// Laboratorio profesor XXE: FLAG{A_XXE_BASE64_INDEX_DISCLOSURE}
// Laboratorio final: FLAG{FINAL_XXE_PHP_FILTER_INDEX_SOURCE}
session_start();

function h($value) {
    return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
}

function layout($title, $body) {
    echo '<!doctype html><html lang="es"><head><meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width,initial-scale=1">';
    echo '<title>' . h($title) . '</title>';
    echo '<style>
      :root { color-scheme: light; font-family: Inter, Segoe UI, Arial, sans-serif; }
      body { margin: 0; background: #f4f6f8; color: #1d2733; }
      header { background: #17202a; color: white; padding: 22px 30px; }
      main { max-width: 980px; margin: 28px auto; padding: 0 18px; }
      section.panel, .card { background: white; border: 1px solid #d8dee6; border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
      .tabs, .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 16px; }
      label { display: block; font-weight: 650; margin: 14px 0 7px; }
      input, textarea, select { width: 100%; box-sizing: border-box; padding: 11px; border: 1px solid #b8c2cc; border-radius: 6px; font: inherit; background: white; }
      textarea { min-height: 132px; resize: vertical; }
      button, .button { display: inline-block; margin-top: 14px; background: #255f85; color: white; border: 0; border-radius: 6px; padding: 11px 15px; font-weight: 700; cursor: pointer; text-decoration: none; }
      button.secondary { background: #536270; }
      pre, .result { background: #101820; color: #d6f5e3; padding: 14px; border-radius: 6px; overflow: auto; white-space: pre-wrap; }
      .muted { color: #586575; }
      .notice { border-left: 4px solid #255f85; background: #eef6fb; padding: 12px; margin-bottom: 14px; }
    </style></head><body><header><h1>' . h($title) . '</h1></header><main>';
    echo $body;
    echo '</main></body></html>';
}

function parse_xml_unsafe($xml) {
    $previous = libxml_use_internal_errors(true);
    $dom = new DOMDocument();
    $dom->resolveExternals = true;
    $dom->substituteEntities = true;
    $ok = $dom->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD | LIBXML_NONET);
    libxml_use_internal_errors($previous);
    if (!$ok) {
        return 'El documento no pudo procesarse.';
    }
    return $dom->textContent;
}

function parse_xml_safe($xml) {
    $previous = libxml_use_internal_errors(true);
    $dom = new DOMDocument();
    $ok = $dom->loadXML($xml, LIBXML_NONET);
    libxml_use_internal_errors($previous);
    if (!$ok) {
        return 'El documento no pudo procesarse.';
    }
    return $dom->textContent;
}

function simulate_support_browser($message) {
    if (stripos($message, 'document.cookie') === false || stripos($message, 'fetch') === false) {
        return '';
    }

    $admin_cookie = 'zorum_admin=admin-session-reportes-2026';
    $encoded_cookie = base64_encode($admin_cookie);
    $callback = '';

    if (preg_match("/fetch\\(['\"]([^'\"]+)/i", $message, $matches)) {
        $callback = $matches[1];
    }

    if ($callback === '') {
        return 'Mensaje enviado a soporte.';
    }

    if (str_contains($callback, '+')) {
        $callback = explode('+', $callback, 2)[0];
    }

    $target = $callback . $encoded_cookie;
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'timeout' => 3,
            'ignore_errors' => true,
        ],
    ]);
    @file_get_contents($target, false, $context);
    return 'Mensaje enviado a soporte.';
}

function has_support_xss($message) {
    return stripos($message, '<script') !== false
        || stripos($message, 'onerror') !== false
        || stripos($message, 'document.cookie') !== false;
}

function professor_xxe() {
    $xml = $_POST['xml'] ?? '<email><to>seguridad@empresa.local</to><company>Empresa</company><body>Revision mensual</body></email>';
    $result = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $result = parse_xml_unsafe($xml);
    }
    layout('Procesador de comunicados', '
      <section class="panel">
        <h2>Comunicado corporativo</h2>
        <p class="muted">Carga el XML enviado por el area de comunicaciones para generar una vista previa.</p>
        <form method="post">
          <label>Documento XML</label>
          <textarea name="xml">' . h($xml) . '</textarea>
          <button>Procesar comunicado</button>
        </form>
        <h3>Resultado</h3>
        <pre>' . h($result) . '</pre>
      </section>
    ');
}

function student_xxe() {
    $action = $_POST['action'] ?? 'report';
    $xml = $_POST['xml'] ?? '<ticket><usuario>operador</usuario><mensaje>Solicitud pendiente</mensaje></ticket>';
    $result = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        if ($action === 'user') {
            $result = parse_xml_unsafe($xml);
        } else {
            $result = parse_xml_safe($xml);
        }
    }
    layout('Centro de reportes', '
      <section class="panel">
        <h2>Solicitudes</h2>
        <form method="post">
          <label>Tipo de solicitud</label>
          <select name="action">
            <option value="report"' . ($action === 'report' ? ' selected' : '') . '>Mandar reporte</option>
            <option value="user"' . ($action === 'user' ? ' selected' : '') . '>Reportar usuario</option>
            <option value="admin"' . ($action === 'admin' ? ' selected' : '') . '>Comunicar al administrador</option>
          </select>
          <label>Contenido XML</label>
          <textarea name="xml">' . h($xml) . '</textarea>
          <button>Enviar solicitud</button>
        </form>
        <h3>Estado</h3>
        <pre>' . h($result) . '</pre>
      </section>
    ');
}

function zorum_login() {
    $error = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $user = $_POST['username'] ?? '';
        $pass = $_POST['password'] ?? '';
        if ($user === 'camilo_sesto' && $pass === 'Empresa2026@') {
            $_SESSION['zorum_user'] = $user;
            setcookie('zorum_session', 'usuario-camilo-2026', 0, '/zorum');
            header('Location: /zorum');
            exit;
        }
        $error = 'Credenciales invalidas.';
    }
    layout('Zorum', '
      <section class="panel">
        <div class="notice">En nuestro equipo de Red Team hemos identificado unas credenciales vulnerables para este panel camilo_sesto:Empresa2026@</div>
        <form method="post">
          <label>Usuario</label>
          <input name="username" autocomplete="username">
          <label>Contrasena</label>
          <input name="password" type="password" autocomplete="current-password">
          <button>Ingresar</button>
        </form>
        <p class="muted">' . h($error) . '</p>
      </section>
    ');
}

function zorum_panel() {
    if (!isset($_SESSION['zorum_user'])) {
        zorum_login();
        return;
    }

    $project_result = '';
    $support_result = '';
    $active = $_POST['panel_action'] ?? '';

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && $active === 'project') {
        $id = $_POST['project_id'] ?? '';
        if ($id === '1') {
            $project_result = "Proyecto 1: Migracion documental\nFLAG{CONTINUA_INVESTIGANDO_LA_PAGINA!}";
        } elseif (ctype_digit($id) && (int)$id >= 2 && (int)$id <= 10) {
            $project_result = "Proyecto $id: Registro reservado para el area solicitante.";
        } else {
            $project_result = 'Proyecto no encontrado.';
        }
    }

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && $active === 'support') {
        $message = $_POST['message'] ?? '';
        $support_result = '<div class="card"><strong>Vista previa enviada a soporte</strong><div>' . $message . '</div></div>';
        $exfiltration = simulate_support_browser($message);
        if ($exfiltration !== '') {
            $support_result .= '<pre>' . h($exfiltration) . '</pre>';
        } elseif (has_support_xss($message)) {
            $support_result .= '<pre>Mensaje enviado a soporte.</pre>';
        }
    }

    $has_admin = ($_COOKIE['zorum_admin'] ?? '') === 'admin-session-reportes-2026';

    $admin_button = '';
    if ($has_admin) {
        $admin_button = '
          <section class="panel">
            <h2>Acceso administrativo</h2>
            <p class="muted">Sesion administrativa detectada.</p>
            <a class="button" href="/zorum/rp7x-admin-914/reportes">Panel de admin</a>
          </section>';
    }

    layout('Zorum - Panel interno', '
      <div class="grid">
        <section class="panel">
          <h2>Listar Proyectos</h2>
          <form method="post">
            <input type="hidden" name="panel_action" value="project">
            <label>Identificador</label>
            <input name="project_id" value="' . h($_POST['project_id'] ?? '2') . '">
            <button>Consultar</button>
          </form>
          <pre>' . h($project_result) . '</pre>
        </section>
        <section class="panel">
          <h2>Enviar mensaje a soporte tecnico</h2>
          <form method="post">
            <input type="hidden" name="panel_action" value="support">
            <label>Mensaje</label>
            <textarea name="message">' . h($_POST['message'] ?? 'Revision solicitada por operaciones.') . '</textarea>
            <button>Enviar mensaje</button>
          </form>
          ' . $support_result . '
        </section>
      </div>
      ' . $admin_button . '
    ');
}

function zorum_admin_panel() {
    if (($_COOKIE['zorum_admin'] ?? '') !== 'admin-session-reportes-2026') {
        http_response_code(403);
        layout('Acceso restringido', '<section class="panel">No se encontro una sesion administrativa valida.</section>');
        return;
    }

    $default_xml = $_POST['xml'] ?? '<email><to>admin@zorum.local</to><company>Zorum</company><body>Nuevo reporte</body></email>';
    $report_result = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $report_result = parse_xml_unsafe($default_xml);
    }

    layout('Zorum - Panel de admin', '
      <section class="panel">
        <h2>Crear reporte</h2>
        <form method="post">
          <label>XML del reporte</label>
          <textarea name="xml">' . h($default_xml) . '</textarea>
          <button>Crear reporte</button>
        </form>
        <h3>Salida</h3>
        <pre>' . h($report_result) . '</pre>
      </section>
    ');
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($path === '/A/lab5-xxe') {
    professor_xxe();
} elseif ($path === '/B/lab5-xxe') {
    student_xxe();
} elseif ($path === '/zorum/rp7x-admin-914/reportes') {
    zorum_admin_panel();
} elseif ($path === '/zorum') {
    zorum_panel();
} else {
    http_response_code(404);
    layout('No encontrado', '<section class="panel">Modulo no encontrado.</section>');
}
?>
