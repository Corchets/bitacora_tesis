// App mínima para medir en un iPhone: corre el `llama-server` de llama.cpp dentro del proceso de la app.
//
// No tiene interfaz: una pantalla con una etiqueta. Al abrir,
//   - se para en Documents/ (ahí va el GGUF, copiado desde la Mac) y manda stdout y stderr a Documents/runtime.log;
//   - llama a `llama_server(argc, argv)` con los argumentos con que se lanzó la app (los de `llama-server`);
//   - cada 5 s anota memoria y estado térmico en Documents/recursos.log.
// La pantalla queda encendida: iOS suspende la app, y con ella el servidor, si pasa a segundo plano.

#import <UIKit/UIKit.h>

#include <mach/mach.h>
#include <os/proc.h>
#include <pthread.h>
#include <string>
#include <unistd.h>
#include <vector>

int llama_server(int argc, char ** argv);  // tools/server/server.cpp (biblioteca llama-server-impl)

static std::vector<std::string> g_args;
static UILabel * g_etiqueta;

static void mostrar(NSString * texto) {
    dispatch_async(dispatch_get_main_queue(), ^{ g_etiqueta.text = texto; });
}

static const char * termico() {
    switch (NSProcessInfo.processInfo.thermalState) {
        case NSProcessInfoThermalStateNominal: return "nominal";
        case NSProcessInfoThermalStateFair: return "fair";
        case NSProcessInfoThermalStateSerious: return "serious";
        case NSProcessInfoThermalStateCritical: return "critical";
    }
    return "?";
}

// footprint es lo que iOS cuenta contra el límite de memoria de la app (jetsam); residente incluye además las páginas
// del GGUF mapeado, y es lo más parecido al VmHWM de Android.
static void * muestrear(void *) {
    FILE * f = fopen("recursos.log", "w");
    NSISO8601DateFormatter * fecha = [NSISO8601DateFormatter new];
    fecha.timeZone = NSTimeZone.localTimeZone;
    while (f) {
        task_vm_info_data_t v = {};
        mach_msg_type_number_t n = TASK_VM_INFO_COUNT;
        task_info(mach_task_self(), TASK_VM_INFO, (task_info_t) &v, &n);
        fprintf(f, "%s footprint_kb=%llu footprint_pico_kb=%lld residente_kb=%llu residente_pico_kb=%llu "
                   "disponible_kb=%zu termico=%s bateria=%.2f cargando=%d bajo_consumo=%d\n",
                [fecha stringFromDate:NSDate.date].UTF8String, v.phys_footprint / 1024,
                (long long) v.ledger_phys_footprint_peak / 1024, v.resident_size / 1024, v.resident_size_peak / 1024,
                os_proc_available_memory() / 1024, termico(), UIDevice.currentDevice.batteryLevel,
                UIDevice.currentDevice.batteryState != UIDeviceBatteryStateUnplugged,
                NSProcessInfo.processInfo.lowPowerModeEnabled);
        fflush(f);
        sleep(5);
    }
    return nullptr;
}

static void * servir(void *) {
    std::vector<char *> argv;
    for (auto & a : g_args) argv.push_back(a.data());
    argv.push_back(nullptr);
    int salida = llama_server((int) g_args.size(), argv.data());
    fprintf(stderr, "llama_server terminó con %d\n", salida);
    mostrar([NSString stringWithFormat:@"llama_server terminó con %d", salida]);
    return nullptr;
}

@interface Escena : UIResponder <UIWindowSceneDelegate>
@property(nonatomic, strong) UIWindow * window;
@end

@implementation Escena
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session
      options:(UISceneConnectionOptions *)opciones {
    self.window = [[UIWindow alloc] initWithWindowScene:(UIWindowScene *) scene];
    UIViewController * vista = [UIViewController new];
    vista.view.backgroundColor = UIColor.systemBackgroundColor;
    g_etiqueta = [[UILabel alloc] initWithFrame:CGRectInset(vista.view.bounds, 24, 24)];
    g_etiqueta.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    g_etiqueta.numberOfLines = 0;
    g_etiqueta.textAlignment = NSTextAlignmentCenter;
    [vista.view addSubview:g_etiqueta];
    self.window.rootViewController = vista;
    [self.window makeKeyAndVisible];

    UIApplication.sharedApplication.idleTimerDisabled = YES;
    UIDevice.currentDevice.batteryMonitoringEnabled = YES;
    if (g_args.size() < 2) {
        g_etiqueta.text = @"Sin argumentos: lanzar desde la Mac con medir.py.";
        return;
    }
    g_etiqueta.text = @"llama-server corriendo.\nDejar esta pantalla abierta.";
    pthread_t hilo;
    pthread_create(&hilo, nullptr, muestrear, nullptr);
    pthread_attr_t atributos;  // 8 MiB de pila, como el hilo principal de un proceso de macOS
    pthread_attr_init(&atributos);
    pthread_attr_setstacksize(&atributos, 8 << 20);
    pthread_create(&hilo, &atributos, servir, nullptr);
}
@end

@interface Delegado : UIResponder <UIApplicationDelegate>
@end

@implementation Delegado
- (UISceneConfiguration *)application:(UIApplication *)application
    configurationForConnectingSceneSession:(UISceneSession *)sesion
                                   options:(UISceneConnectionOptions *)opciones {
    UISceneConfiguration * c = [[UISceneConfiguration alloc] initWithName:@"Default" sessionRole:sesion.role];
    c.delegateClass = Escena.class;
    return c;
}
@end

int main(int argc, char * argv[]) {
    @autoreleasepool {
        NSString * docs = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
        chdir(docs.fileSystemRepresentation);
        for (int i = 0; i < argc; i++) g_args.emplace_back(argv[i]);
        if (argc > 1) {
            freopen("runtime.log", "w", stdout);
            freopen("runtime.log", "a", stderr);
            setvbuf(stdout, nullptr, _IOLBF, 0);
            setvbuf(stderr, nullptr, _IONBF, 0);
        }
        return UIApplicationMain(argc, argv, nil, NSStringFromClass(Delegado.class));
    }
}
