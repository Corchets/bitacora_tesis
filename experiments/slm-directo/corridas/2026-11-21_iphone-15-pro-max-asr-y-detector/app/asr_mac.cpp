// Prueba en seco en la Mac: el mismo asr.cpp, fuera de la app.
//   asr-mac AUDIO.wav CARPETA_MODELOS INICIO LOG.jsonl
// INICIO es la hora de reloj en segundos Unix, o +N para N segundos desde ahora.
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include "asr.h"

int main(int argc, char ** argv) {
    if (argc != 5) {
        fprintf(stderr, "uso: %s AUDIO.wav CARPETA_MODELOS INICIO LOG.jsonl\n", argv[0]);
        return 2;
    }
    double inicio = argv[3][0] == '+' ? time(nullptr) + atof(argv[3] + 1) : atof(argv[3]);
    return asr_correr(argv[1], argv[2], inicio, argv[4]);
}
