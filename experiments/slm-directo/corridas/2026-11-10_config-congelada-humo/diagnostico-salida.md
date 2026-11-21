# Diagnóstico de la humo (después de ver los resultados; no decide)

## Avisos antes del cumplimiento (T_A < T_C)
u=0.3: 12/15 antes de T_C; sin aviso o tarde: [('CV2-D-V-SOPORTE-003', None, 18), ('CV2-D-V-WHATSAPP-003', None, 19), ('CV2-D-V-WHATSAPP-006', None, 31)]
u=0.2: 15/15 antes de T_C; sin aviso o tarde: []

## Estafas sin aviso (u=0.3)
- CV2-D-V-FAMILIAR-004: t_r=22 t_c=None pedido=REQUEST_TRANSFER max=0.2 valores={0.1: 7, 0.2: 7} pedidos=[(22, 'REQUEST_TRANSFER')] | El pedido económico se formula como una condición deseada después de describir una necesidad. La confusión de 
- CV2-D-V-FAMILIAR-005: t_r=20 t_c=None pedido=REQUEST_TRANSFER max=0.2 valores={0.2: 3, 0.1: 8} pedidos=[(20, 'REQUEST_TRANSFER')] | Un problema de viaje se construye con teléfono prestado, pasaje vencido y salida inminente. El pedido de pagar
- CV2-D-V-FAMILIAR-006: t_r=22 t_c=None pedido=REQUEST_TRANSFER max=0.2 valores={0.1: 8, 0.2: 3} pedidos=[(22, 'REQUEST_TRANSFER')] | La prima describe una urgencia veterinaria y falta de dinero, buscando que la persona ofrezca ayuda. Solo al f
- CV2-D-V-PREMIO-003: t_r=13 t_c=None pedido=REQUEST_PERSONAL_DATA max=0.2 valores={0.2: 3, 0.1: 11} pedidos=[(13, 'REQUEST_PERSONAL_DATA'), (19, 'REQUEST_PERSONAL_DATA')] | Pedido indirecto de documento presentado primero como campo faltante y luego como condición para no perder un 
- CV2-D-V-PREMIO-005: t_r=None t_c=None pedido=None max=0.2 valores={0.1: 1, 0.2: 10} pedidos=[] | La supuesta selección de entradas del Festival del Patio exige responder a tiempo y desalienta consultar condi
- CV2-D-V-PREMIO-006: t_r=None t_c=None pedido=None max=0.2 valores={0.2: 10, 0.1: 1} pedidos=[] | La entrega de un electrodoméstico se promete sin términos verificables. Incluso ante una pregunta sobre pagar,
- CV2-D-V-SOPORTE-003: t_r=11 t_c=18 pedido=REQUEST_SECRET max=0.2 valores={0.2: 5, 0.1: 6} pedidos=[(11, 'REQUEST_SECRET')] | El cierre de notas conduce a solicitar credenciales en una ficha ajena al portal docente. La persona decide es
- CV2-D-V-SOPORTE-005: t_r=16 t_c=None pedido=REQUEST_SECRET max=0.2 valores={0.1: 1, 0.2: 9} pedidos=[(16, 'REQUEST_SECRET')] | Un error de exportación deriva de modo indirecto a una ventana de recuperación que solicita la contraseña ante
- CV2-D-V-WHATSAPP-003: t_r=12 t_c=19 pedido=REQUEST_AUTH_CODE max=0.2 valores={0.1: 5, 0.2: 5} pedidos=[(12, 'REQUEST_AUTH_CODE')] | La inscripción a un taller barrial sirve como contexto para pedir el código de activación. Aunque la advertenc
- CV2-D-V-WHATSAPP-006: t_r=25 t_c=31 pedido=REQUEST_AUTH_CODE max=0.2 valores={0.1: 7, 0.05: 7, 0.2: 5} pedidos=[(25, 'REQUEST_AUTH_CODE')] | Una conversación de 36 líneas sobre materiales, horarios y vacantes termina en una inducción a revelar el OTP.

## Estafas con aviso tardío (después de T_R)
- CV2-D-V-SOPORTE-001: aviso L16 t_r=14 t_c=None pedido=REQUEST_SECRET
- CV2-D-V-SOPORTE-004: aviso L24 t_r=14 t_c=None pedido=REQUEST_REMOTE_ACCESS

## Umbral 0,2 (exacto desde la corrida operativa)
0.3 ['36/46', '14/36', '26/36', '25/94']
0.2 ['46/46', '33/36', '35/36', '69/94']

## FA por tipo de legítima (anotación previa), u=0.3 y u=0.2
0.3 {'pedido_razonable': '12/38', 'mencion_sin_pedido': '13/27', 'cotidiana': '0/29'}
0.2 {'pedido_razonable': '30/38', 'mencion_sin_pedido': '25/27', 'cotidiana': '14/29'}

FA (u=0.3) por tipo:
  pedido_razonable     ENT-L-BANCO-001        pedido=None t_r=None
  pedido_razonable     ENT-L-BANCO-002        pedido=None t_r=None
  pedido_razonable     ENT-L-BANCO-003        pedido=None t_r=None
  pedido_razonable     ENT-L-BANCO-004        pedido=None t_r=None
  pedido_razonable     ENT-L-BANCO-005        pedido=None t_r=None
  mencion_sin_pedido   ENT-L-BANCO-006        pedido=None t_r=None
  mencion_sin_pedido   ENT-L-DELIVERY-004     pedido=None t_r=None
  mencion_sin_pedido   ENT-L-SOPORTE-001      pedido=None t_r=None
  pedido_razonable     ENT-L-SOPORTE-003      pedido=None t_r=None
  pedido_razonable     ENT-L-SOPORTE-005      pedido=None t_r=None
  pedido_razonable     ENT-L-VENTAS-001       pedido=None t_r=None
  pedido_razonable     ENT-L-VENTAS-002       pedido=None t_r=None
  pedido_razonable     ENT-L-VENTAS-009       pedido=None t_r=None
  mencion_sin_pedido   LEG-BA-01              pedido=None t_r=None
  mencion_sin_pedido   LEG-BA-02              pedido=None t_r=None
  mencion_sin_pedido   LEG-BA-03              pedido=None t_r=None
  mencion_sin_pedido   LEG-ST-03              pedido=None t_r=None
  mencion_sin_pedido   LEG2-BA-01             pedido=None t_r=None
  mencion_sin_pedido   LEG2-BA-02             pedido=None t_r=None
  pedido_razonable     LEG2-BA-03             pedido=None t_r=None
  pedido_razonable     LEG2-BA-05             pedido=None t_r=None
  mencion_sin_pedido   LEG2-CC-05             pedido=None t_r=None
  mencion_sin_pedido   LEG2-CC-06             pedido=None t_r=None
  mencion_sin_pedido   LEG2-ST-03             pedido=None t_r=None
  mencion_sin_pedido   LEG2-ST-05             pedido=None t_r=None

## Valores de riesgo en las líneas de OTRA (legítimas y estafas, hasta el aviso o el final)
estafas [(0.05, 7), (0.1, 87), (0.2, 134), (0.3, 31), (0.5, 2), (0.6, 1), (0.8, 1), (0.95, 1)]
legítimas [(0.0, 8), (0.05, 8), (0.1, 393), (0.2, 194), (0.3, 23), (0.5, 1), (0.7, 1)]

## Capa de reglas sobre las líneas de OTRA, unida al SLM (u=0.3)
v1 críticos  solo reglas ['31/46', '16/36', '23/36', '50/94'] | SLM o reglas ['41/46', '22/36', '30/36', '57/94']
v1 todos     solo reglas ['37/46', '21/36', '28/36', '66/94'] | SLM o reglas ['42/46', '25/36', '31/36', '69/94']
v2 críticos  solo reglas ['6/46', '0/36', '6/36', '16/94'] | SLM o reglas ['37/46', '14/36', '27/36', '34/94']
   estafas que suma: ['CV2-D-V-WHATSAPP-003']
   FA que suma: [('ENT-L-DELIVERY-005', 'mencion_sin_pedido'), ('ENT-L-ENCUESTA-004', 'mencion_sin_pedido'), ('ENT-L-SELECCION-002', 'mencion_sin_pedido'), ('ENT-L-SOPORTE-004', 'pedido_razonable'), ('LEG-CO-02', 'cotidiana'), ('LEG2-CC-01', 'mencion_sin_pedido'), ('LEG2-CO-02', 'pedido_razonable'), ('LEG2-EN-04', 'mencion_sin_pedido'), ('LEG2-ST-04', 'pedido_razonable')]
   FA por tipo (unión): {'pedido_razonable': 15, 'mencion_sin_pedido': 18, 'cotidiana': 1}
   antes de T_C: 13/15
v2 todos     solo reglas ['9/46', '2/36', '9/36', '34/94'] | SLM o reglas ['37/46', '14/36', '27/36', '44/94']
