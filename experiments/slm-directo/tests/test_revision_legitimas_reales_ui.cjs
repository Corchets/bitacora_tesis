// Navegador real con conversaciones ficticias. Requiere Playwright y Chrome instalados.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const os=require('node:os');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
let chromium;try{({chromium}=require('playwright'))}catch{}

test('ficha de legítimas reales: validación, guardado y descarga',async t=>{
 if(!chromium){t.skip('Requiere Playwright en NODE_PATH y Chrome.');return}
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'revision-legitimas-'));
 const data={issue:'52-legitimas-reales',version:1,muestra:'fixture',casos:Array.from({length:3},(_,i)=>({id:`Llamada 0${i+1}`,turnos:[{hablante:'OTRA',texto:'<script>NO EJECUTAR</script>'},{hablante:'PROTEGIDA',texto:'Sí, dígame.'},{hablante:'OTRA',texto:'Necesito el PIN de la cuenta.'}]}))};
 const template=await fs.readFile(path.join(__dirname,'../analisis/tablero/revision_legitimas_reales_plantilla.html'),'utf8');
 const file=path.join(dir,'fichas.html');await fs.writeFile(file,template.replace('__DATOS_REVISION__',JSON.stringify(data).replaceAll('<','\\u003c')));
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage({acceptDownloads:true});const pageErrors=[];page.on('pageerror',e=>pageErrors.push(e.message));
  await page.goto(pathToFileURL(file).href);
  assert.match(await page.locator('#welcome-title').textContent(),/^3 llamadas/);
  await page.locator('#reviewer').fill('Revisor de prueba');await page.locator('#start').click();
  assert.equal(await page.locator('.turn').count(),3);assert.equal(await page.locator('.turn script').count(),0);
  await page.locator('[name=completa]').click();assert.equal(await page.locator('[name=completa]').isChecked(),false);assert.match(await page.locator('#errors').textContent(),/Respondé/);
  await page.locator('[name=roles][value=si]').check();await page.locator('[name=legitima][value=si]').check();
  await page.locator('[name=intencion][value=gestion_propia]').check();await page.locator('[name=pide][value=codigo_clave]').check();
  await page.locator('[name=etiqueta][value=avisar]').check();await page.locator('[name=razon]').fill('Pide el PIN (l. 3).');
  await page.locator('[name=completa]').click();assert.equal(await page.locator('[name=completa]').isChecked(),false);assert.match(await page.locator('#errors').textContent(),/línea del pedido/);
  await page.locator('[data-line="3"]').click();assert.equal(await page.locator('[name=etiqueta_linea]').inputValue(),'3');
  await page.locator('[name=completa]').check();assert.equal(await page.locator('[name=completa]').isChecked(),true);assert.match(await page.locator('#count').textContent(),/1 de 3 respondidas · 1 confirmadas/);
  await page.reload();await page.locator('#reviewer').fill('Revisor de prueba');await page.locator('#start').click();
  assert.equal(await page.locator('[name=completa]').isChecked(),true);assert.equal(await page.locator('[name=pide][value=codigo_clave]').isChecked(),true);
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#export').click()]);
  const packet=JSON.parse(await fs.readFile(await download.path(),'utf8'));
  assert.equal(packet.issue,'52-legitimas-reales');assert.deepEqual(packet.respuestas['Llamada 01'].pide,['codigo_clave']);assert.equal(packet.respuestas['Llamada 01'].etiqueta_linea,'3');
  assert.deepEqual(pageErrors,[]);
 }finally{await browser.close()}
});
