// ASR `parakeet-filtro` sobre un WAV a ritmo real (asr.cpp). Bloquea hasta terminar el audio; 0 si terminó bien.
//   wav: PCM16 estéreo a 16 kHz (izquierdo OTRA, derecho PROTEGIDA)
//   modelos: carpeta con parakeet/{encoder,decoder,joiner}.int8.onnx, parakeet/tokens.txt y silero_vad.onnx
//   inicio: hora de reloj (segundos Unix) en que empieza el audio; el modelo se carga antes
//   log: JSONL con la carga, cada transcripción, el atraso cada 5 s de audio y el resumen final
#pragma once
#ifdef __cplusplus
extern "C" {
#endif
int asr_correr(const char * wav, const char * modelos, double inicio, const char * log);
#ifdef __cplusplus
}
#endif
