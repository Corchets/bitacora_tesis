#!/usr/bin/env python3
"""
presentacion_ui.py - Driver portable de UI con Chrome headless y CDP vía WebSocket.

Verifica la vista de presentación (Issue #111) sobre el servidor real de experiments/voip
en un puerto efímero aislado. Comprueba:
1. Navegación e inicio de conexión WebSocket.
2. Captura del comando iniciar desde la UI.
3. No-regresión: modo ASR no abre la vista de presentación.
4. Entrada visible a la presentación al confirmar llamada (sin depender de clases internas).
5. Roles fijos en ambos teléfonos (Otra persona a la izq, Persona protegida a la der).
6. Visibilidad observable y contraste de color del nombre de cada rol contra el fondo efectivo.
7. Actividad alternada por RMS en indicadores visuales de ambos teléfonos.
8. Transcripciones finales mostradas con rol correspondiente en el diálogo central.
9. Alternancia fluida entre panel y presentación sin comandos WebSocket espurios.
10. Captura del comando terminar desde la presentación.
11. Conservación de la escena y transcripciones tras el fin de la llamada.
12. Capturas de pantalla en resolución notebook (1366x768) y proyección (1920x1080).
13. Consola del navegador sin excepciones no controladas.
"""

import argparse
import asyncio
import base64
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
from types import SimpleNamespace


def resolver_voip_dir(repo_arg: str | None = None) -> Path:
    """Localiza el directorio experiments/voip de forma portable."""
    if repo_arg:
        p = Path(repo_arg).resolve()
        if (p / "experiments" / "voip" / "servidor.py").is_file():
            return p / "experiments" / "voip"
        if (p / "servidor.py").is_file():
            return p
        raise FileNotFoundError(f"No se encontró servidor.py a partir del argumento --repo: {repo_arg}")

    this_file = Path(__file__).resolve()
    # Si este script está en experiments/voip/tests/presentacion_ui.py:
    candidate = this_file.parent.parent
    if (candidate / "servidor.py").is_file():
        return candidate

    # Búsqueda hacia arriba en ancestros
    for parent in this_file.parents:
        cand = parent / "experiments" / "voip"
        if (cand / "servidor.py").is_file():
            return cand
        if (parent / "servidor.py").is_file():
            return parent

    raise FileNotFoundError("No se pudo localizar el directorio experiments/voip.")


def find_chrome() -> str:
    """Detecta el binario de Chrome o Chromium sin depender de rutas rígidas."""
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin and Path(env_bin).is_file():
        return env_bin

    candidates = [
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for cand in candidates:
        if cand and Path(cand).is_file():
            return cand

    raise RuntimeError("No se encontró ejecutable de Google Chrome o Chromium en el sistema.")


def get_free_port() -> int:
    """Obtiene un puerto efímero disponible en loopback (evita colisión con 8765)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def fetch_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class CDPSession:
    """Sesión CDP asíncrona sobre WebSocket."""
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self.req_id = 0
        self.console_logs = []
        self._listener_task = None
        self._pending_responses = {}

    async def connect(self):
        import websockets
        self.ws = await websockets.connect(self.ws_url, max_size=2**24)
        self._listener_task = asyncio.create_task(self._listen())
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("Console.enable")

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                if "id" in msg:
                    req_id = msg["id"]
                    if req_id in self._pending_responses:
                        fut = self._pending_responses.pop(req_id)
                        if not fut.done():
                            fut.set_result(msg)
                else:
                    method = msg.get("method")
                    if method == "Runtime.consoleAPICalled":
                        args = [a.get("value") or a.get("description") for a in msg.get("params", {}).get("args", [])]
                        self.console_logs.append({
                            "type": msg.get("params", {}).get("type"),
                            "text": " ".join(str(a) for a in args)
                        })
                    elif method == "Runtime.exceptionThrown":
                        details = msg.get("params", {}).get("exceptionDetails", {})
                        text = details.get("text", "")
                        desc = details.get("exception", {}).get("description", "")
                        self.console_logs.append({"type": "error", "text": f"{text}: {desc}"})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.console_logs.append({"type": "internal_error", "text": str(e)})

    async def send(self, method: str, params: dict | None = None, timeout: float = 10.0) -> dict:
        self.req_id += 1
        curr_id = self.req_id
        fut = asyncio.get_running_loop().create_future()
        self._pending_responses[curr_id] = fut
        payload = {"id": curr_id, "method": method}
        if params is not None:
            payload["params"] = params
        await self.ws.send(json.dumps(payload))
        resp = await asyncio.wait_for(fut, timeout=timeout)
        if "error" in resp:
            raise RuntimeError(f"CDP Error in {method}: {resp['error']}")
        return resp.get("result", {})

    async def eval(self, expression: str, timeout: float = 5.0):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        }, timeout=timeout)
        return result.get("result", {}).get("value")

    async def set_viewport(self, width: int, height: int):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False
        })

    async def capture_screenshot(self, output_path: str):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(res["data"])
        with open(output_path, "wb") as f:
            f.write(data)

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
        if self.ws:
            await self.ws.close()


class UIDriver:
    def __init__(self, voip_dir: Path, chrome_bin: str | None = None):
        self.voip_dir = voip_dir
        self.chrome_bin = chrome_bin or find_chrome()
        self.server_port = get_free_port()
        self.chrome_port = get_free_port()
        self.server = None
        self.chrome_proc = None
        self.chrome_tmpdir = None
        self.panel_ws = None
        self.panel_connected_event = asyncio.Event()
        self.received_messages = []
        self.cdp = None
        self.check_results = []

    def record_check(self, name: str, passed: bool, detail: str = ""):
        self.check_results.append({"name": name, "passed": passed, "detail": detail})
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name} - {detail}")

    async def start_server(self):
        # Importar dinámicamente servidor.servir_panel
        if str(self.voip_dir) not in sys.path:
            sys.path.insert(0, str(self.voip_dir))
        from servidor import servir_panel
        from websockets.asyncio.server import serve

        args = SimpleNamespace(detector="reglas", modelo=None)

        async def ws_handler(ws):
            if ws.request.path == "/panel":
                self.panel_ws = ws
                self.panel_connected_event.set()
                try:
                    async for raw in ws:
                        msg = json.loads(raw)
                        self.received_messages.append(msg)
                except Exception:
                    pass

        self.server = await serve(
            ws_handler,
            "127.0.0.1",
            self.server_port,
            process_request=lambda conn, req: servir_panel(conn, req, args)
        )

    async def start_chrome(self):
        self.chrome_tmpdir = tempfile.mkdtemp(prefix="tesis-chrome-ui-")
        cmd = [
            self.chrome_bin,
            "--headless=new",
            f"--remote-debugging-port={self.chrome_port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={self.chrome_tmpdir}",
            "about:blank"
        ]
        self.chrome_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        page_ws_url = None
        for _ in range(40):
            await asyncio.sleep(0.1)
            try:
                pages = await asyncio.to_thread(fetch_json, f"http://127.0.0.1:{self.chrome_port}/json/list", 2.0)
                for page in pages:
                    if page.get("type") == "page":
                        page_ws_url = page.get("webSocketDebuggerUrl")
                        break
                if page_ws_url:
                    break
            except Exception:
                pass
        if not page_ws_url:
            raise RuntimeError("No se pudo obtener webSocketDebuggerUrl de Chrome headless.")
        self.cdp = CDPSession(page_ws_url)
        await self.cdp.connect()

    async def cleanup(self):
        if self.cdp:
            try:
                await self.cdp.close()
            except Exception:
                pass
        if self.chrome_proc:
            self.chrome_proc.terminate()
            try:
                self.chrome_proc.wait(timeout=3)
            except Exception:
                self.chrome_proc.kill()
        if self.chrome_tmpdir:
            shutil.rmtree(self.chrome_tmpdir, ignore_errors=True)
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def run_scenario(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Iniciando servidor de pruebas en puerto efímero {self.server_port}...")
        await self.start_server()
        print(f"Iniciando Chrome headless ({self.chrome_bin}) en puerto {self.chrome_port}...")
        await self.start_chrome()

        try:
            # 1. Navegación a panel.html y conexión WebSocket
            panel_url = f"http://127.0.0.1:{self.server_port}/"
            await self.cdp.send("Page.navigate", {"url": panel_url})
            await asyncio.wait_for(self.panel_connected_event.wait(), timeout=5.0)

            # Esperar a que la UI esté interactiva
            for _ in range(25):
                ready = await self.cdp.eval("!document.getElementById('iniciar').disabled")
                if ready:
                    break
                await asyncio.sleep(0.1)

            servidor_ok = await self.cdp.eval("""
                (() => {
                    const btn = document.getElementById('iniciar');
                    const estado = document.getElementById('estado')?.textContent;
                    return Boolean(btn && !btn.disabled);
                })()
            """)
            self.record_check("Servidor y Browser", bool(servidor_ok), "panel.html cargado y conectado vía WebSocket")

            # 2. Iniciar llamada desde UI
            await self.cdp.eval("document.getElementById('iniciar').click()")
            await asyncio.sleep(0.2)
            init_cmd = next((m for m in self.received_messages if m.get("tipo") == "iniciar"), None)
            cmd_ok = init_cmd is not None and init_cmd.get("modo") == "llamada"
            self.record_check("Captura iniciar", cmd_ok, f"Comando recibido: {init_cmd}")

            # 3. No-regresión: modo ASR no abre vista de presentación
            await self.panel_ws.send(json.dumps({
                "tipo": "inicio",
                "llamada_id": "test-asr-previa",
                "modo": "asr",
                "corte_silencio_s": 0.8,
                "umbral_rms_silencio": 0.008
            }))
            await asyncio.sleep(0.15)
            # Verificación observable: sección de presentación NO debe ser visible
            pres_visible_asr = await self.cdp.eval("""
                (() => {
                    const sec = document.getElementById('presentacion');
                    if (!sec) return false;
                    const style = window.getComputedStyle(sec);
                    return !sec.hidden && style.display !== 'none' && sec.offsetHeight > 0;
                })()
            """)
            self.record_check("ASR no entra a Presentación", not pres_visible_asr, "Modo ASR no hizo visible la sección de presentación")

            # 4. Entrada observable a Presentación tras confirmación de llamada real
            await self.panel_ws.send(json.dumps({
                "tipo": "inicio",
                "llamada_id": "llamada-demo-111",
                "modo": "llamada",
                "corte_silencio_s": 0.8,
                "asr": "zipformer"
            }))
            await asyncio.sleep(0.25)
            # Verificación observable: sección de presentación visible con título y acciones
            pres_estado = await self.cdp.eval("""
                (() => {
                    const sec = document.getElementById('presentacion');
                    if (!sec) return { visible: false };
                    const style = window.getComputedStyle(sec);
                    const visible = !sec.hidden && style.display !== 'none' && sec.offsetHeight > 0;
                    const titulo = sec.querySelector('.pres-titulo')?.textContent.trim();
                    const volverBtn = sec.querySelector('#volver-panel');
                    const terminarBtn = sec.querySelector('#pres-terminar');
                    return {
                        visible,
                        titulo,
                        tieneVolver: Boolean(volverBtn && volverBtn.offsetHeight > 0),
                        tieneTerminar: Boolean(terminarBtn && terminarBtn.offsetHeight > 0)
                    };
                })()
            """)
            entrada_ok = pres_estado.get("visible") and pres_estado.get("tieneVolver") and pres_estado.get("tieneTerminar")
            self.record_check(
                "Entrada visible a Presentación tras confirmación inicio",
                bool(entrada_ok),
                f"Presentación visible (título: '{pres_estado.get('titulo')}', controles disponibles)"
            )

            # 5. Roles fijos en teléfonos
            roles_obs = await self.cdp.eval("""
                (() => {
                    const otra = document.getElementById('pres-telefono-otra');
                    const prot = document.getElementById('pres-telefono-protegida');
                    const nombreOtra = document.getElementById('pres-nombre-otra')?.textContent.trim();
                    const nombreProt = document.getElementById('pres-nombre-protegida')?.textContent.trim();
                    return {
                        otraVisible: Boolean(otra && otra.offsetHeight > 0),
                        protVisible: Boolean(prot && prot.offsetHeight > 0),
                        nombreOtra,
                        nombreProt
                    };
                })()
            """)
            roles_ok = (
                roles_obs.get("otraVisible") and roles_obs.get("protVisible") and
                roles_obs.get("nombreOtra") == "Otra persona" and
                roles_obs.get("nombreProt") == "Persona protegida"
            )
            self.record_check("Roles fijos en teléfonos", bool(roles_ok), f"Izquierda: '{roles_obs.get('nombreOtra')}', Derecha: '{roles_obs.get('nombreProt')}'")

            # 6. Comprobación observable de visibilidad y contraste del color del nombre de cada rol
            # Revisa que el texto del nombre no quede mimetizado o invisible sobre el fondo efectivo de su cabecera.
            analisis_visual = await self.cdp.eval("""
                (() => {
                    function parseRgb(colorStr) {
                        if (!colorStr) return null;
                        const m = colorStr.match(/rgba?\\(\\s*([\\d.]+)\\s*,\\s*([\\d.]+)\\s*,\\s*([\\d.]+)(?:\\s*,\\s*([\\d.]+))?\\s*\\)/);
                        if (!m) return null;
                        return {
                            r: parseFloat(m[1]),
                            g: parseFloat(m[2]),
                            b: parseFloat(m[3]),
                            a: m[4] !== undefined ? parseFloat(m[4]) : 1.0
                        };
                    }

                    function getEffectiveBg(el) {
                        let curr = el;
                        while (curr && curr !== document.documentElement) {
                            const style = window.getComputedStyle(curr);
                            const bg = style.backgroundColor;
                            const parsed = parseRgb(bg);
                            if (parsed && parsed.a > 0.08) {
                                return {
                                    tag: curr.tagName.toLowerCase() + (curr.className ? '.' + String(curr.className).replace(/\\s+/g, '.') : '') + (curr.id ? '#' + curr.id : ''),
                                    color: bg,
                                    parsed
                                };
                            }
                            curr = curr.parentElement;
                        }
                        return { tag: 'html/body', color: 'rgb(255, 255, 255)', parsed: {r: 255, g: 255, b: 255, a: 1} };
                    }

                    function luminance(r, g, b) {
                        const a = [r, g, b].map(v => {
                            v /= 255;
                            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                        });
                        return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                    }

                    function contrastRatio(rgb1, rgb2) {
                        const l1 = luminance(rgb1.r, rgb1.g, rgb1.b);
                        const l2 = luminance(rgb2.r, rgb2.g, rgb2.b);
                        const bright = Math.max(l1, l2);
                        const dark = Math.min(l1, l2);
                        return (bright + 0.05) / (dark + 0.05);
                    }

                    function inspectRole(id) {
                        const el = document.getElementById(id);
                        if (!el) return { found: false };
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        const textColor = style.color;
                        const parsedText = parseRgb(textColor);
                        const effBg = getEffectiveBg(el);
                        let ratio = 1.0;
                        if (parsedText && effBg.parsed) {
                            ratio = contrastRatio(parsedText, effBg.parsed);
                        }
                        const isWhiteOnWhite = parsedText && effBg.parsed &&
                            (parsedText.r > 230 && parsedText.g > 230 && parsedText.b > 230) &&
                            (effBg.parsed.r > 230 && effBg.parsed.g > 230 && effBg.parsed.b > 230);

                        return {
                            found: true,
                            text: el.textContent.trim(),
                            visibleDimensions: rect.width > 0 && rect.height > 0,
                            display: style.display,
                            visibility: style.visibility,
                            textColor,
                            effectiveBgColor: effBg.color,
                            effectiveBgSource: effBg.tag,
                            contrastRatio: Math.round(ratio * 100) / 100,
                            isWhiteOnWhite,
                            contrastOk: ratio >= 3.0 && !isWhiteOnWhite
                        };
                    }

                    return {
                        otra: inspectRole('pres-nombre-otra'),
                        protegida: inspectRole('pres-nombre-protegida')
                    };
                })()
            """)
            otra_vis = analisis_visual.get("otra", {})
            prot_vis = analisis_visual.get("protegida", {})
            contraste_ok = (
                otra_vis.get("contrastOk") and prot_vis.get("contrastOk") and
                otra_vis.get("visibleDimensions") and prot_vis.get("visibleDimensions")
            )
            detalle_contraste = (
                f"Otra: texto={otra_vis.get('textColor')} sobre {otra_vis.get('effectiveBgColor')} ({otra_vis.get('effectiveBgSource')}), ratio={otra_vis.get('contrastRatio')}; "
                f"Protegida: texto={prot_vis.get('textColor')} sobre {prot_vis.get('effectiveBgColor')} ({prot_vis.get('effectiveBgSource')}), ratio={prot_vis.get('contrastRatio')}"
            )
            self.record_check("Visibilidad y contraste de nombres de roles", bool(contraste_ok), detalle_contraste)

            # 7. Actividad real de ambos canales (niveles)
            # Primero Otra persona habla
            await self.panel_ws.send(json.dumps({
                "tipo": "niveles",
                "llamada_id": "llamada-demo-111",
                "t_s": 1.0,
                "canales": {
                    "otra": {"rms": 0.045, "umbral_rms_silencio": 0.003},
                    "protegida": {"rms": 0.0005, "umbral_rms_silencio": 0.003}
                }
            }))
            await asyncio.sleep(0.12)
            otra_hablando = await self.cdp.eval("""
                (() => {
                    const vOtra = document.getElementById('pres-voz-txt-otra')?.textContent.trim();
                    const vProt = document.getElementById('pres-voz-txt-protegida')?.textContent.trim();
                    const mOtra = document.getElementById('pres-nivel-otra')?.value || 0;
                    const mProt = document.getElementById('pres-nivel-protegida')?.value || 0;
                    return vOtra === 'Hablando ahora' && vProt === 'En silencio' &&
                           mOtra > 0.01 && mProt <= 0.005;
                })()
            """)

            # Luego Persona protegida habla
            await self.panel_ws.send(json.dumps({
                "tipo": "niveles",
                "llamada_id": "llamada-demo-111",
                "t_s": 2.0,
                "canales": {
                    "otra": {"rms": 0.0005, "umbral_rms_silencio": 0.003},
                    "protegida": {"rms": 0.038, "umbral_rms_silencio": 0.003}
                }
            }))
            await asyncio.sleep(0.12)
            prot_hablando = await self.cdp.eval("""
                (() => {
                    const vOtra = document.getElementById('pres-voz-txt-otra')?.textContent.trim();
                    const vProt = document.getElementById('pres-voz-txt-protegida')?.textContent.trim();
                    const mOtra = document.getElementById('pres-nivel-otra')?.value || 0;
                    const mProt = document.getElementById('pres-nivel-protegida')?.value || 0;
                    return vOtra === 'En silencio' && vProt === 'Hablando ahora' &&
                           mOtra <= 0.005 && mProt > 0.01;
                })()
            """)
            actividad_ok = bool(otra_hablando and prot_hablando)
            self.record_check(
                "Actividad real de ambos canales",
                actividad_ok,
                "Texto observable ('Hablando ahora' / 'En silencio') y medidores de nivel activos alternados por RMS sin clases internas"
            )

            # 8. Transcripción final de ambos roles en diálogo central
            await self.panel_ws.send(json.dumps({
                "tipo": "asr",
                "entrega": "final",
                "segmento": 1,
                "rol": "otra",
                "texto": "Hola, nos comunicamos del departamento de soporte de la entidad.",
                "fin_audio_s": 2.8
            }))
            await self.panel_ws.send(json.dumps({
                "tipo": "asr",
                "entrega": "final",
                "segmento": 2,
                "rol": "protegida",
                "texto": "¿Qué problema ocurrió con la cuenta?",
                "fin_audio_s": 4.5
            }))
            await asyncio.sleep(0.18)
            dialogo_ok = await self.cdp.eval("""
                (() => {
                    const lineas = [...document.querySelectorAll('#pres-charla .linea')];
                    if (lineas.length !== 2) return false;
                    const l1 = lineas[0];
                    const l2 = lineas[1];
                    const r1 = l1.dataset.rol === 'otra' && l1.textContent.includes('soporte');
                    const r2 = l2.dataset.rol === 'protegida' && l2.textContent.includes('cuenta');
                    return r1 && r2;
                })()
            """)
            self.record_check("Texto final y roles en diálogo central", bool(dialogo_ok), "2 intervenciones mostradas con roles y textos correctos en #pres-charla")

            # 9. Ida y vuelta a consola sin comandos duplicados
            cmds_antes = len(self.received_messages)
            await self.cdp.eval("document.getElementById('volver-panel').click()")
            await asyncio.sleep(0.12)
            en_consola = await self.cdp.eval("""
                (() => {
                    const sec = document.getElementById('presentacion');
                    const verPres = document.getElementById('ver-presentacion');
                    const secOculta = !sec || sec.hidden || sec.offsetHeight === 0;
                    const verPresVisible = Boolean(verPres && !verPres.hidden && verPres.offsetHeight > 0);
                    return secOculta && verPresVisible;
                })()
            """)

            await self.cdp.eval("document.getElementById('ver-presentacion').click()")
            await asyncio.sleep(0.12)
            de_nuevo_pres = await self.cdp.eval("""
                (() => {
                    const sec = document.getElementById('presentacion');
                    return Boolean(sec && !sec.hidden && sec.offsetHeight > 0);
                })()
            """)
            cmds_despues = len(self.received_messages)
            sin_duplicados = (cmds_despues == cmds_antes)
            alternancia_ok = bool(en_consola and de_nuevo_pres and sin_duplicados)
            self.record_check(
                "Ida y vuelta a consola sin comandos duplicados",
                alternancia_ok,
                f"Consola reabierta, presentación recuperada, comandos emitidos en transición: {cmds_despues - cmds_antes}"
            )

            # 10. Captura de Terminar análisis desde Presentación
            await self.cdp.eval("document.getElementById('pres-terminar').click()")
            await asyncio.sleep(0.2)
            term_cmd = next((m for m in self.received_messages[cmds_antes:] if m.get("tipo") == "terminar"), None)
            self.record_check("Captura terminar", term_cmd is not None, f"Comando recibido: {term_cmd}")

            # 11. Servidor confirma fin y escena conservada
            await self.panel_ws.send(json.dumps({
                "tipo": "fin",
                "llamada_id": "llamada-demo-111",
                "dir": "corridas/20261030-prueba"
            }))
            await asyncio.sleep(0.2)
            escena_conservada = await self.cdp.eval("""
                (() => {
                    const sec = document.getElementById('presentacion');
                    const esVisible = Boolean(sec && !sec.hidden && sec.offsetHeight > 0);
                    const estado = document.getElementById('pres-estado')?.textContent.trim();
                    const sub = document.getElementById('pres-dialogo-sub')?.textContent.trim();
                    const lineas = document.querySelectorAll('#pres-charla .linea').length;
                    return esVisible && estado === 'Análisis finalizado' && sub.includes('conservada') && lineas === 2;
                })()
            """)
            self.record_check("Fin conserva la escena", bool(escena_conservada), "Estado 'Análisis finalizado', subtítulo conservado y 2 líneas de diálogo intactas")

            # 12. Capturas de pantalla
            # Notebook 1366x768
            await self.cdp.set_viewport(1366, 768)
            await asyncio.sleep(0.2)
            png_notebook = output_dir / "tesis-presentacion-ui-notebook-1366x768.png"
            await self.cdp.capture_screenshot(str(png_notebook))
            print(f"Captura notebook guardada: {png_notebook}")

            # Proyección 1920x1080
            await self.cdp.set_viewport(1920, 1080)
            await asyncio.sleep(0.2)
            png_proy = output_dir / "tesis-presentacion-ui-proyeccion-1920x1080.png"
            await self.cdp.capture_screenshot(str(png_proy))
            print(f"Captura proyección guardada: {png_proy}")

            # 13. Logs de errores de consola
            errores_consola = [log for log in self.cdp.console_logs if log.get("type") in ("error", "internal_error")]
            log_path = output_dir / "tesis-presentacion-ui-consola.log"
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(self.cdp.console_logs, f, indent=2, ensure_ascii=False)
            sin_errores = (len(errores_consola) == 0)
            self.record_check(
                "Logs de consola sin excepciones no controladas",
                sin_errores,
                f"{len(errores_consola)} errores detectados en runtime"
            )

        finally:
            await self.cleanup()

        return self.check_results


def generar_reporte(resultados, report_path: Path, output_dir: Path):
    lineas = [
        "# Reporte de verificación de UI: Vista de presentación (#111)",
        "",
        "## Resumen",
        "Driver automatizado y portable con Chrome headless y CDP vía WebSocket nativo sobre el servidor real de `experiments/voip` en puerto efímero aislado.",
        "",
        "## Criterios de Aceptación Evaluados",
        ""
    ]
    for r in resultados:
        icono = "✅" if r["passed"] else "❌"
        lineas.append(f"- {icono} **{r['name']}**: {r['detail']}")

    lineas.extend([
        "",
        "## Capturas de pantalla generadas",
        f"- Notebook (1366x768): `{output_dir / 'tesis-presentacion-ui-notebook-1366x768.png'}`",
        f"- Proyección (1920x1080): `{output_dir / 'tesis-presentacion-ui-proyeccion-1920x1080.png'}`",
        f"- Logs de consola: `{output_dir / 'tesis-presentacion-ui-consola.log'}`",
        "",
        "## Reproducibilidad",
        "Comando para ejecutar el driver completo desde cualquier entorno con Python y websockets:",
        "```sh",
        "python3 experiments/voip/tests/presentacion_ui.py --outdir /tmp/tesis-presentacion-ui-portable --report /tmp/tesis-presentacion-ui-portable-report.md",
        "```",
        ""
    ])
    report_path.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Reporte generado en: {report_path}")


async def main():
    parser = argparse.ArgumentParser(description="Driver portable de UI con Chrome headless para Issue #111")
    parser.add_argument("--repo", default=None, help="Ruta al repositorio o experiments/voip (opcional, auto-detectado)")
    parser.add_argument("--outdir", default="/tmp/tesis-presentacion-ui-portable", help="Directorio para capturas y logs")
    parser.add_argument("--report", default="/tmp/tesis-presentacion-ui-portable-report.md", help="Ruta del reporte Markdown")
    args = parser.parse_args()

    voip_dir = resolver_voip_dir(args.repo)
    print(f"Directorio voip resuelto: {voip_dir}")

    driver = UIDriver(voip_dir=voip_dir)
    outdir = Path(args.outdir)
    report_path = Path(args.report)

    resultados = await driver.run_scenario(outdir)
    generar_reporte(resultados, report_path, outdir)

    todo_ok = all(r["passed"] for r in resultados)
    sys.exit(0 if todo_ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
