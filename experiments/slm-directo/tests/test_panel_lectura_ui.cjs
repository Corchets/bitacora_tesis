// Ejecución del renderizador con DOM mínimo y casos ficticios, sin navegador ni corpus.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {resolve}=require('node:path');
const {gzipSync}=require('node:zlib');
const vm=require('node:vm');

test('corridas, grupos, lectura completa y ficha ambigua conservan sus datos',async()=>{
  const texto=['A: <pedido ficticio>','B: respuesta'];
  const caso=(id,clase,notas='')=>({id,clase,grupo:'fixture',texto,prueba:'Prueba ficticia',notas,tr:clase==='vishing'?1:null,tc:null});
  const casos=Object.fromEntries([caso('V1','vishing'),caso('V2','vishing','Caso límite: hay una duda.'),caso('L1','legitima'),caso('L2','legitima'),caso('L3','legitima')].map(c=>[c.id,c]));
  const resultado=(aviso,completo=true)=>({aviso,completo,motivo:aviso?'Motivo ficticio':'',evidencia:aviso?'<pedido ficticio>':'',filas:[[0.7,'válida',''],[0.3,'válida','']]});
  const corrida=(nombre,resultados)=>({nombre,resultados,carpeta:'corridas/fixture',modelo:'modelo-ficticio',fin:'2026-11-04T12:00:00',commit:'abcdef'});
  const d={casos,hasta:'2026-11-04T12:00:00',pendientes:[],lecturas_previas:{V1:'Antecedente'},corridas:[
    corrida('Condición A',{V1:resultado(1),V2:resultado(null),L1:resultado(1),L2:resultado(null),L3:resultado(null,false)}),
    corrida('Condición B',{V1:resultado(null),V2:resultado(1),L1:resultado(null),L2:resultado(null),L3:resultado(null)})
  ]};
  const paquete={actual:d,historico:{casos:[{id:'V1'}]}};
  const elementos=new Map();
  function elemento(id){if(!elementos.has(id))elementos.set(id,{value:id==='rev-buscar'?'':'0',innerHTML:'',textContent:'',eventos:{},addEventListener(evento,fn){this.eventos[evento]=fn}});return elementos.get(id)}
  elemento('rev-data').textContent=JSON.stringify({gzip:gzipSync(JSON.stringify(paquete)).toString('base64')});
  elemento('cmp-data').textContent=JSON.stringify({usar:'historico'});
  let iniciar;
  const contexto={document:{getElementById:elemento,addEventListener(_,fn){iniciar=fn}},Response,Blob,DecompressionStream,Uint8Array,atob};
  const plantilla=readFileSync(resolve(__dirname,'../analisis/tablero/lectura_corridas_plantilla.html'),'utf8');
  const script=[...plantilla.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1];
  vm.runInNewContext(script,contexto);
  await iniciar();
  assert.match(elemento('rev-saldo').textContent,/1\/2 estafas detectadas · 1 perdidas · 1\/3 falsas alarmas/);
  assert.match(elemento('rev-saldo').textContent,/1 evaluaciones incompletas/);
  assert.match(elemento('rev-count').textContent,/3 de 5 casos/);
  const filtrar=f=>elemento('lectura150').eventos.click({target:{closest(){return {dataset:{rFiltro:f}}}}});
  filtrar('perdida');assert.match(elemento('rev-count').textContent,/1 de 5 casos/);
  assert.match(elemento('rev-casos').innerHTML,/V2/);
  filtrar('fa');assert.match(elemento('rev-casos').innerHTML,/L1/);
  assert.ok(!elemento('rev-casos').innerHTML.includes('<code>L3</code>'));
  filtrar('dudas');assert.match(elemento('rev-casos').innerHTML,/Caso límite/);
  const contenido={innerHTML:''};
  elemento('rev-casos').eventos.toggle({target:{dataset:{rDialogo:'V2'},open:true,querySelector(){return contenido}}});
  assert.match(contenido.innerHTML,/&lt;pedido ficticio&gt;/);
  assert.match(contenido.innerHTML,/T_R/);
  elemento('rev-corrida').value='1';elemento('rev-corrida').onchange();
  filtrar('perdida');assert.match(elemento('rev-casos').innerHTML,/<code>V1<\/code>/);
  elemento('rev-buscar').value='NO EXISTE';elemento('rev-buscar').eventos.input();
  assert.match(elemento('rev-casos').innerHTML,/No hay casos/);
  const historico=await contexto.leerDatosComprimidos('cmp-data');
  assert.deepEqual(Array.from(historico.casos[0].texto),texto);
});
