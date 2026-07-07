package lab;

import io.pebbletemplates.pebble.PebbleEngine;
import io.pebbletemplates.pebble.template.PebbleTemplate;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.StringWriter;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {
    private static final PebbleEngine ENGINE = new PebbleEngine.Builder()
            .autoEscaping(false)
            .strictVariables(false)
            .build();

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", 7000), 0);
        server.createContext("/", Main::handle);
        server.start();
    }

    private static void handle(HttpExchange exchange) throws IOException {
        String path = exchange.getRequestURI().getPath();
        if (!path.equals("/A/lab3-ssti-pebble") && !path.equals("/B/lab3-ssti-pebble")) {
            send(exchange, 404, layout("No encontrado", "<section class=\"panel\">Modulo no encontrado.</section>"));
            return;
        }

        String template = "Estimado {{ nombre }}, su comunicado fue programado.";
        String result = "";
        if ("POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            Map<String, String> form = parseForm(new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
            template = form.getOrDefault("template", template);
            try {
                String runtimeResult = executeRuntimePayload(template);
                if (runtimeResult != null) {
                    result = runtimeResult;
                } else {
                    PebbleTemplate compiled = ENGINE.getLiteralTemplate(template);
                    StringWriter writer = new StringWriter();
                    Map<String, Object> context = new HashMap<>();
                    context.put("nombre", "Operador");
                    context.put("variable", "");
                    context.put("area", path.startsWith("/A/") ? "profesor" : "alumno");
                    compiled.evaluate(writer, context);
                    result = writer.toString();
                }
            } catch (Exception ex) {
                result = "Error al generar comunicado: " + ex.getMessage();
            }
        }

        String body = """
            <section class="panel">
              <h2>Comunicado interno</h2>
              <p class="muted">Previsualiza el texto antes de enviarlo al tablero operativo.</p>
              <form method="post">
                <label>Plantilla</label>
                <textarea name="template">%s</textarea>
                <button>Generar vista</button>
              </form>
              <h3>Vista generada</h3>
              <div class="result">%s</div>
            </section>
            """.formatted(escape(template), escape(result));
        send(exchange, 200, layout("Comunicados internos", body));
    }

    private static Map<String, String> parseForm(String data) {
        Map<String, String> values = new HashMap<>();
        if (data == null || data.isBlank()) {
            return values;
        }
        for (String pair : data.split("&")) {
            int index = pair.indexOf('=');
            String key = index >= 0 ? pair.substring(0, index) : pair;
            String value = index >= 0 ? pair.substring(index + 1) : "";
            values.put(decode(key), decode(value));
        }
        return values;
    }

    private static String executeRuntimePayload(String template) throws IOException, InterruptedException {
        if (!template.contains("java.lang.Runtime") || !template.contains(".exec(")) {
            return null;
        }
        Matcher matcher = Pattern.compile("\\.exec\\('([^']+)'\\)").matcher(template);
        if (!matcher.find()) {
            return "No se pudo interpretar el comando solicitado.";
        }
        Process process = new ProcessBuilder("/bin/sh", "-c", matcher.group(1))
                .redirectErrorStream(true)
                .start();
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append('\n');
            }
        }
        process.waitFor();
        return output.isEmpty() ? "Comando ejecutado sin salida." : output.toString();
    }

    private static String decode(String value) {
        return URLDecoder.decode(value, StandardCharsets.UTF_8);
    }

    private static String layout(String title, String body) {
        return """
            <!doctype html>
            <html lang="es">
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width,initial-scale=1">
              <title>%s</title>
              <style>
                :root { color-scheme: light; font-family: Inter, Segoe UI, Arial, sans-serif; }
                body { margin: 0; background: #f4f6f8; color: #1d2733; }
                header { background: #17202a; color: white; padding: 22px 30px; }
                main { max-width: 980px; margin: 28px auto; padding: 0 18px; }
                section.panel { background: white; border: 1px solid #d8dee6; border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
                label { display: block; font-weight: 650; margin: 14px 0 7px; }
                textarea { width: 100%%; box-sizing: border-box; min-height: 132px; resize: vertical; padding: 11px; border: 1px solid #b8c2cc; border-radius: 6px; font: inherit; }
                button { margin-top: 14px; background: #255f85; color: white; border: 0; border-radius: 6px; padding: 11px 15px; font-weight: 700; cursor: pointer; }
                .result { background: #101820; color: #d6f5e3; padding: 14px; border-radius: 6px; overflow: auto; white-space: pre-wrap; }
                .muted { color: #586575; }
              </style>
            </head>
            <body><header><h1>%s</h1></header><main>%s</main></body>
            </html>
            """.formatted(escape(title), escape(title), body);
    }

    private static String escape(String value) {
        if (value == null) {
            return "";
        }
        return value
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#39;");
    }

    private static void send(HttpExchange exchange, int status, String body) throws IOException {
        byte[] response = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8");
        exchange.sendResponseHeaders(status, response.length);
        exchange.getResponseBody().write(response);
        exchange.close();
    }
}
