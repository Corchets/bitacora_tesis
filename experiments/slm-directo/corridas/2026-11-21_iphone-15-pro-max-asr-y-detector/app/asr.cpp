// ASR del proyecto, `parakeet-filtro` (ADR 0001), sobre un WAV leído a ritmo real.
//
// Es la lógica de `MotorPorFrases`, `MotorSherpaParakeet` y `DetectorSilero` de experiments/asr-local/motores.py con
// la configuración de la demo VoIP (`servidor.py`: corte «auto» = 0,8 s, umbral RMS 0,008, Silero 0,5 en modo
// «filtro», 2 hilos, un reconocedor para los dos canales y un Silero por canal), pasada a C++ con sherpa-onnx v1.13.8:
// el reconocedor por la API en C y Silero por `sherpa_onnx::VadModel`, que es lo que usa `VadModel.is_speech` en Python.
// Sin los filtros de texto (otro idioma en los borradores, muletillas en los finales).
//
// El WAV es estéreo PCM16 a 16 kHz (izquierdo OTRA, derecho PROTEGIDA, como los ejemplos de la demo). A partir de la
// hora `inicio` (segundos Unix), cada bloque de 640 muestras se procesa cuando termina en el audio: primero OTRA y
// después PROTEGIDA, en un solo hilo, como `reproducir_ejemplo` de la demo. Cada transcripción va a `log` (JSONL) con
// el atraso: cuánto después del fin del bloque en el audio quedó lista.

#include "asr.h"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <deque>
#include <memory>
#include <string>
#include <sys/time.h>
#include <thread>
#include <vector>

#include "sherpa-onnx/c-api/c-api.h"
#include "sherpa-onnx/csrc/vad-model.h"

namespace {

constexpr int TASA = 16000;
constexpr int BLOQUE = 640;  // 40 ms, el bloque del panel
constexpr double CORTE_SILENCIO_S = 0.8, UMBRAL_RMS = 0.008, PREVIO_S = 0.3, MAX_FRASE_S = 10.0, MIN_VOZ_S = 0.3,
                 MIN_VOZ_PARCIAL_S = 1.0, PARCIALES_CADA_S = 0.5;
constexpr float UMBRAL_SILERO = 0.5f;
constexpr int VENTANA = 512;

using Reloj = std::chrono::steady_clock;
FILE * g_log;
Reloj::time_point g_cero;  // hora del inicio del audio, en el reloj monótono

double ahora_s() { return std::chrono::duration<double>(Reloj::now() - g_cero).count(); }

std::string reloj() {
    timeval tv;
    gettimeofday(&tv, nullptr);
    tm t;
    localtime_r(&tv.tv_sec, &t);
    char b[64];
    size_t n = strftime(b, sizeof b, "%Y-%m-%dT%H:%M:%S", &t);
    snprintf(b + n, sizeof b - n, ".%03d", (int) (tv.tv_usec / 1000));
    return b;
}

std::string json(const std::string & s) {
    std::string r = "\"";
    for (unsigned char c : s) {
        if (c == '"' || c == '\\') r += '\\', r += (char) c;
        else if (c < 0x20) { char e[8]; snprintf(e, sizeof e, "\\u%04x", c); r += e; }
        else r += (char) c;
    }
    return r + "\"";
}

std::string recortar(const char * t) {
    std::string s = t ? t : "";
    auto es = [](unsigned char c) { return std::isspace(c); };
    while (!s.empty() && es(s.back())) s.pop_back();
    size_t i = 0;
    while (i < s.size() && es(s[i])) i++;
    return s.substr(i);
}

const SherpaOnnxOfflineRecognizer * g_reconocedor;

std::string transcribir(const std::vector<float> & audio) {
    const SherpaOnnxOfflineStream * st = SherpaOnnxCreateOfflineStream(g_reconocedor);
    SherpaOnnxAcceptWaveformOffline(st, TASA, audio.data(), (int32_t) audio.size());
    SherpaOnnxDecodeOfflineStream(g_reconocedor, st);
    const SherpaOnnxOfflineRecognizerResult * r = SherpaOnnxGetOfflineStreamResult(st);
    std::string texto = recortar(r->text);
    SherpaOnnxDestroyOfflineRecognizerResult(r);
    SherpaOnnxDestroyOfflineStream(st);
    return texto;
}

// Un canal: MotorPorFrases con DetectorSilero en modo «filtro». Los nombres siguen a motores.py.
struct Canal {
    const char * rol;
    std::unique_ptr<sherpa_onnx::VadModel> vad;
    std::vector<float> pendiente;
    bool ultima = false;
    int segmento_actual = 1;
    std::vector<float> frase;
    std::deque<std::vector<float>> previo;
    double inicio_segmento_s = 0, inicio_previo_s = 0, silencio_acum_s = 0, desde_parcial_s = 0, voz_s = 0;
    std::string ultimo_texto_parcial;

    void limpiar() {
        frase.clear();
        previo.clear();
        inicio_segmento_s = inicio_previo_s = silencio_acum_s = desde_parcial_s = voz_s = 0;
        ultimo_texto_parcial.clear();
    }

    bool es_voz_silero(const std::vector<float> & m) {
        std::vector<float> datos = pendiente;
        datos.insert(datos.end(), m.begin(), m.end());
        size_t completas = datos.size() / VENTANA * VENTANA;
        if (completas) {
            bool alguna = false;  // todas las ventanas pasan por el modelo: el estado tiene que avanzar
            for (size_t i = 0; i < completas; i += VENTANA) alguna = vad->IsSpeech(datos.data() + i, VENTANA) || alguna;
            ultima = alguna;
        }
        pendiente.assign(datos.begin() + completas, datos.end());
        return ultima;
    }

    void evento(const char * tipo, const std::string & texto, double fin_s, Reloj::time_point t0) {
        double proceso_ms = std::chrono::duration<double, std::milli>(Reloj::now() - t0).count();
        fprintf(g_log,
                "{\"tipo\":\"%s\",\"canal\":\"%s\",\"segmento\":%d,\"inicio_audio_s\":%.3f,\"fin_audio_s\":%.3f,"
                "\"reloj\":\"%s\",\"proceso_ms\":%.1f,\"atraso_s\":%.3f,\"texto\":%s}\n",
                tipo, rol, segmento_actual, inicio_segmento_s, fin_s, reloj().c_str(), proceso_ms, ahora_s() - fin_s,
                json(texto).c_str());
        fflush(g_log);
    }

    void cerrar_frase(double fin_s, Reloj::time_point t0) {
        std::string texto = voz_s >= MIN_VOZ_S ? transcribir(frase) : "";
        if (!texto.empty()) evento("final", texto, fin_s, t0);
        int segmento = segmento_actual + (texto.empty() ? 0 : 1);
        limpiar();
        segmento_actual = segmento;
    }

    void procesar_bloque(const std::vector<float> & m, double inicio_bloque_s, double fin_bloque_s) {
        auto t0 = Reloj::now();
        double dur_s = fin_bloque_s - inicio_bloque_s;
        bool silero = es_voz_silero(m);
        double suma = 0;
        for (float x : m) suma += (double) x * x;
        bool voz = std::sqrt(suma / m.size()) >= UMBRAL_RMS;
        bool cuenta = voz && silero;

        if (frase.empty()) {
            if (!voz) {
                previo.push_back(m);
                size_t total = 0;
                for (auto & b : previo) total += b.size();
                while (total > PREVIO_S * TASA) {
                    total -= previo.front().size();
                    inicio_previo_s += (double) previo.front().size() / TASA;
                    previo.pop_front();
                }
                if (previo.size() == 1) inicio_previo_s = inicio_bloque_s;
                return;
            }
            inicio_segmento_s = previo.empty() ? inicio_bloque_s : inicio_previo_s;
            for (auto & b : previo) frase.insert(frase.end(), b.begin(), b.end());
            frase.insert(frase.end(), m.begin(), m.end());
            previo.clear();
            silencio_acum_s = 0;
            desde_parcial_s = dur_s;
            voz_s = cuenta ? dur_s : 0;
            return;
        }
        frase.insert(frase.end(), m.begin(), m.end());
        silencio_acum_s = voz ? 0 : silencio_acum_s + dur_s;
        desde_parcial_s += dur_s;
        voz_s += cuenta ? dur_s : 0;
        if (silencio_acum_s >= CORTE_SILENCIO_S || fin_bloque_s - inicio_segmento_s >= MAX_FRASE_S) {
            cerrar_frase(fin_bloque_s, t0);
            return;
        }
        if (cuenta && voz_s >= MIN_VOZ_PARCIAL_S && desde_parcial_s >= PARCIALES_CADA_S) {
            desde_parcial_s = 0;
            std::string texto = transcribir(frase);
            if (!texto.empty() && texto != ultimo_texto_parcial) {
                ultimo_texto_parcial = texto;
                evento("parcial", texto, fin_bloque_s, t0);
            }
        }
    }
};

// Lee el encabezado de un WAV PCM16 estéreo a 16 kHz y deja el archivo en el comienzo de los datos.
long abrir_wav(FILE * f) {
    char id[4];
    uint32_t largo;
    if (fread(id, 1, 4, f) != 4 || memcmp(id, "RIFF", 4) || fseek(f, 12, SEEK_SET)) return -1;
    uint16_t formato = 0, canales = 0, bits = 0;
    uint32_t tasa = 0;
    while (fread(id, 1, 4, f) == 4 && fread(&largo, 4, 1, f) == 1) {
        if (!memcmp(id, "fmt ", 4)) {
            long resto = ftell(f) + largo;
            fread(&formato, 2, 1, f);
            fread(&canales, 2, 1, f);
            fread(&tasa, 4, 1, f);
            fseek(f, 6, SEEK_CUR);
            fread(&bits, 2, 1, f);
            fseek(f, resto, SEEK_SET);
        } else if (!memcmp(id, "data", 4)) {
            return formato == 1 && canales == 2 && tasa == TASA && bits == 16 ? (long) largo / 4 : -1;
        } else {
            fseek(f, largo + (largo & 1), SEEK_CUR);
        }
    }
    return -1;
}

}  // namespace

int asr_correr(const char * wav, const char * modelos, double inicio, const char * log) {
    g_log = fopen(log, "w");
    if (!g_log) return 1;
    auto falla = [](const char * motivo) {
        fprintf(g_log, "{\"tipo\":\"error\",\"reloj\":\"%s\",\"motivo\":%s}\n", reloj().c_str(), json(motivo).c_str());
        fflush(g_log);
        return 1;
    };
    FILE * f = fopen(wav, "rb");
    if (!f) return falla("no se pudo abrir el WAV");
    long cuadros = abrir_wav(f);
    if (cuadros < 0) return falla("el WAV no es PCM16 estéreo a 16 kHz");

    auto t_carga = Reloj::now();
    std::string dir = std::string(modelos) + "/parakeet/";
    std::string enc = dir + "encoder.int8.onnx", dec = dir + "decoder.int8.onnx", joi = dir + "joiner.int8.onnx",
                tok = dir + "tokens.txt";
    SherpaOnnxOfflineRecognizerConfig c;
    memset(&c, 0, sizeof c);
    c.feat_config.sample_rate = TASA;
    c.feat_config.feature_dim = 80;
    c.model_config.transducer.encoder = enc.c_str();
    c.model_config.transducer.decoder = dec.c_str();
    c.model_config.transducer.joiner = joi.c_str();
    c.model_config.tokens = tok.c_str();
    c.model_config.num_threads = 2;
    c.model_config.provider = "cpu";
    c.model_config.model_type = "nemo_transducer";
    c.decoding_method = "greedy_search";
    c.max_active_paths = 4;
    g_reconocedor = SherpaOnnxCreateOfflineRecognizer(&c);
    if (!g_reconocedor) return falla("no se pudo crear el reconocedor");

    sherpa_onnx::VadModelConfig v;
    v.silero_vad.model = std::string(modelos) + "/silero_vad.onnx";
    v.silero_vad.threshold = UMBRAL_SILERO;
    v.silero_vad.min_silence_duration = 0;
    v.silero_vad.min_speech_duration = 0;
    v.silero_vad.window_size = VENTANA;
    v.sample_rate = TASA;
    v.num_threads = 1;
    Canal canales[2] = {{"OTRA"}, {"PROTEGIDA"}};
    for (auto & k : canales) k.vad = sherpa_onnx::VadModel::Create(v);

    // Calentamiento: la primera pasada de onnxruntime tarda más; la demo carga los motores antes de la llamada.
    transcribir(std::vector<float>(TASA, 0.0f));
    double carga_ms = std::chrono::duration<double, std::milli>(Reloj::now() - t_carga).count();

    timeval tv;
    gettimeofday(&tv, nullptr);
    double falta = inicio - (tv.tv_sec + tv.tv_usec / 1e6);
    g_cero = Reloj::now() + std::chrono::microseconds((long long) (falta * 1e6));
    fprintf(g_log, "{\"tipo\":\"carga\",\"reloj\":\"%s\",\"carga_ms\":%.0f,\"faltan_s\":%.3f,\"cuadros\":%ld}\n",
            reloj().c_str(), carga_ms, falta, cuadros);
    fflush(g_log);

    std::vector<int16_t> pcm(2 * BLOQUE);
    std::vector<float> m[2] = {std::vector<float>(BLOQUE), std::vector<float>(BLOQUE)};
    std::vector<double> atrasos;
    double max_ventana = 0, max_total = 0;
    long hechos = 0;
    while (hechos < cuadros) {
        long n = std::min<long>(BLOQUE, cuadros - hechos);
        if (fread(pcm.data(), 4, n, f) != (size_t) n) break;
        double ini = (double) hechos / TASA, fin = (double) (hechos + n) / TASA;
        std::this_thread::sleep_until(g_cero + std::chrono::microseconds((long long) (fin * 1e6)));
        for (int k = 0; k < 2; k++) {
            m[k].resize(n);
            for (long i = 0; i < n; i++) m[k][i] = pcm[2 * i + k] / 32768.0f;
            canales[k].procesar_bloque(m[k], ini, fin);
        }
        hechos += n;
        double atraso = ahora_s() - fin;
        atrasos.push_back(atraso);
        max_ventana = std::max(max_ventana, atraso);
        max_total = std::max(max_total, atraso);
        if (hechos % (5 * TASA) == 0) {  // cada 5 s de audio
            fprintf(g_log, "{\"tipo\":\"atraso\",\"reloj\":\"%s\",\"audio_s\":%.2f,\"atraso_s\":%.3f,\"max_5s\":%.3f}\n",
                    reloj().c_str(), fin, atraso, max_ventana);
            fflush(g_log);
            max_ventana = 0;
        }
    }
    double fin_s = (double) hechos / TASA;
    auto t0 = Reloj::now();
    for (auto & k : canales) if (!k.frase.empty()) k.cerrar_frase(fin_s, t0);
    std::sort(atrasos.begin(), atrasos.end());
    auto q = [&](double p) { return atrasos.empty() ? 0 : atrasos[std::min(atrasos.size() - 1, (size_t) std::ceil(p * atrasos.size()) - 1)]; };
    long mas_1s = std::count_if(atrasos.begin(), atrasos.end(), [](double a) { return a > 1.0; });
    fprintf(g_log,
            "{\"tipo\":\"fin\",\"reloj\":\"%s\",\"audio_s\":%.2f,\"bloques\":%zu,\"atraso_mediana_s\":%.3f,"
            "\"atraso_p95_s\":%.3f,\"atraso_max_s\":%.3f,\"bloques_mas_de_1s\":%ld}\n",
            reloj().c_str(), fin_s, atrasos.size(), q(0.5), q(0.95), max_total, mas_1s);
    fflush(g_log);
    fclose(f);
    return 0;
}
