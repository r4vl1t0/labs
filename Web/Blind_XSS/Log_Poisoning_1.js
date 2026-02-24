const express = require('express');
const puppeteer = require('puppeteer');
const app = express();
const adminApp = express(); 

app.use(express.json());

let reports = []; // Base de datos de reportes (Vulnerable al ser renderizada)

// --- CONFIGURACIÓN DE PLANTILLA PÚBLICA ---
const layout = (title, content) => `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>${title}</title>
</head>
<body class="bg-gray-50 text-gray-800">
    <nav class="bg-indigo-700 p-4 shadow-md text-white">
        <div class="container mx-auto flex justify-between items-center">
            <span class="font-bold text-xl tracking-tight">VULN-SYSTEM v3.0</span>
            <div class="space-x-6">
                <a href="/" class="hover:text-indigo-200">Inicio</a>
                <a href="/servicios" class="hover:text-indigo-200">Servicios</a>
                <a href="/contacto" class="hover:text-indigo-200">Contacto</a>
            </div>
        </div>
    </nav>
    <main class="container mx-auto mt-12 p-8 bg-white rounded-lg shadow-sm border border-gray-200 max-w-4xl">
        ${content}
    </main>

    <div id="reportBtn" class="fixed bottom-6 right-6 w-16 h-16 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-[10px] font-black cursor-pointer shadow-xl transition-all hover:scale-110 text-center uppercase p-2 leading-tight z-50">
        Reportar Página
    </div>

    <script>
        document.getElementById('reportBtn').addEventListener('click', () => {
            const data = { url: window.location.href };
            fetch('/report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            }).then(() => {
                alert("El administrador ha sido notificado del error en: " + data.url);
            });
        });
    </script>
</body>
</html>`;

// --- RUTA 1: INICIO ---
app.get('/', (req, res) => {
    res.send(layout("Inicio", `
        <h1 class="text-3xl font-bold text-indigo-900">Bienvenido al Portal Corporativo</h1>
        <p class="mt-4 text-lg">Explora nuestros recursos internos. Todas las páginas son monitoreadas por seguridad.</p>
        <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="p-6 bg-indigo-50 rounded-lg border border-indigo-100">
                <h3 class="font-bold text-indigo-800">Estado del Servidor</h3>
                <p class="text-sm text-indigo-600">Operativo - 99.9% Uptime</p>
            </div>
            <div class="p-6 bg-green-50 rounded-lg border border-green-100">
                <h3 class="font-bold text-green-800">Seguridad</h3>
                <p class="text-sm text-green-600">Firewall Activo (Puerto 3000)</p>
            </div>
        </div>
    `));
});

// --- RUTA 2: SERVICIOS ---
app.get('/servicios', (req, res) => {
    res.send(layout("Servicios", `
        <h1 class="text-3xl font-bold text-indigo-900">Nuestros Servicios</h1>
        <ul class="mt-6 space-y-4">
            <li class="p-4 bg-white border rounded shadow-sm hover:shadow-md transition">
                <h4 class="font-bold">Auditoría de Sistemas</h4>
                <p class="text-gray-500 text-sm">Análisis profundo de infraestructura.</p>
            </li>
            <li class="p-4 bg-white border rounded shadow-sm hover:shadow-md transition">
                <h4 class="font-bold">Pentesting Web</h4>
                <p class="text-gray-500 text-sm">Simulación de ataques controlados.</p>
            </li>
        </ul>
    `));
});

// --- RUTA 3: CONTACTO ---
app.get('/contacto', (req, res) => {
    res.send(layout("Contacto", `
        <h1 class="text-3xl font-bold text-indigo-900">Contacto Interno</h1>
        <p class="mt-2 text-gray-600">Si necesitas asistencia inmediata, utiliza el botón rojo de reporte.</p>
        <div class="mt-6">
            <p><b>Email:</b> admin@vulnman.io</p>
            <p><b>Interno:</b> Ext. 404</p>
        </div>
    `));
});

// --- PROCESADOR DE REPORTES (ENDPOINT SSRF/XSS) ---
app.post('/report', (req, res) => {
    const { url } = req.body;
    if (url) {
        reports.push({ id: reports.length + 1, url: url, time: new Date().toLocaleTimeString() });
        console.log(`[!] Reporte guardado: ${url}`);
        triggerAdminBot(); 
        return res.json({ status: "success" });
    }
    res.status(400).send("Falta parámetro URL");
});

// --- PANEL PRIVADO (PUERTO 5000) ---
adminApp.get('/admin/reports', (req, res) => {
    let rows = reports.map(r => `
        <tr class="border-b border-gray-700 hover:bg-gray-800">
            <td class="p-3 text-blue-400 font-mono text-sm">${r.id}</td>
            <td class="p-3 text-gray-300 font-mono text-sm">${r.url}</td> <td class="p-3 text-gray-500 text-xs">${r.time}</td>
        </tr>
    `).join('');

    res.send(`
        <html>
        <head><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-gray-950 text-gray-200 p-10 font-sans">
            <div class="max-w-5xl mx-auto">
                <header class="flex justify-between items-center border-b border-gray-800 pb-5 mb-8">
                    <h1 class="text-2xl font-black tracking-tighter text-red-500">ADMIN LOG MONITOR v1.0</h1>
                    <span class="bg-red-900 text-red-200 text-xs px-2 py-1 rounded">ACCESO RESTRINGIDO</span>
                </header>
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-gray-500 uppercase text-xs border-b border-gray-800">
                            <th class="p-3">ID</th><th class="p-3">URL Reportada</th><th class="p-3">Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
                <div class="mt-12 p-6 bg-gray-900 border border-gray-800 rounded-lg">
                    <h2 class="text-sm font-bold text-gray-500 mb-2">SISTEMA DE CRIPTOGRAFÍA</h2>
                    <p class="text-xl font-mono text-yellow-500">FLAG: <span class="select-all">CTF{BL1ND_L0G_P01S0N1NG_V4LIDATED}</span></p>
                </div>
            </div>
        </body>
        </html>
    `);
});

// --- BOT ADMIN ---
async function triggerAdminBot() {
    let browser;
    try {
        browser = await puppeteer.launch({ headless: "new", args: ['--no-sandbox'] });
        const page = await browser.newPage();
        // El admin abre su panel interno para ver los reportes acumulados
        await page.goto('http://127.0.0.1:5000/admin/reports', { waitUntil: 'networkidle2', timeout: 5000 });
        await new Promise(r => setTimeout(r, 4000)); 
    } catch (e) { console.log("Bot error o panel offline"); }
    finally { if(browser) await browser.close(); }
}

app.listen(3000, () => console.log(">> Web Pública: http://localhost:3000"));
adminApp.listen(5000, "127.0.0.1", () => console.log(">> Admin Interno: http://127.0.0.1:5000 (Oculto)"));
