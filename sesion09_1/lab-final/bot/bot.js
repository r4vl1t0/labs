const puppeteer = require('puppeteer-core');

const BASE = 'http://xss-app';
const ADMIN_USER = 'soporte.admin';
const ADMIN_PASS = 'R3visionM3sa2024!';
const INTERVALO_MS = 25000;

async function revisarTickets() {
    let browser;
    try {
        browser = await puppeteer.launch({
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
        });
        const page = await browser.newPage();

        await page.goto(`${BASE}/admin/login.php`, { waitUntil: 'networkidle2' });
        await page.type('input[name=usuario]', ADMIN_USER);
        await page.type('input[name=password]', ADMIN_PASS);
        await Promise.all([
            page.waitForNavigation({ waitUntil: 'networkidle2' }),
            page.click('button[type=submit]'),
        ]);

        await page.goto(`${BASE}/admin/tickets.php`, { waitUntil: 'networkidle2' });
        const enlaces = await page.$$eval('td a', (els) => els.map((e) => e.getAttribute('href')));

        for (const href of enlaces) {
            if (!href) continue;
            console.log(`[bot] revisando ${href}`);
            await page.goto(`${BASE}${href}`, { waitUntil: 'networkidle2' });
            await new Promise((r) => setTimeout(r, 2000));
        }

        await browser.close();
    } catch (err) {
        console.error('[bot] error en ciclo de revision:', err.message);
        if (browser) await browser.close();
    }
}

async function loop() {
    while (true) {
        console.log('[bot] iniciando ciclo de revision de tickets');
        await revisarTickets();
        await new Promise((r) => setTimeout(r, INTERVALO_MS));
    }
}

setTimeout(loop, 8000);
