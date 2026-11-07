// Navegador real con conversaciones ficticias. Requiere Playwright y Chrome instalados.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const os=require('node:os');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
let chromium;try{({chromium}=require('playwright'))}catch{}

test('ficha: guardado, validación, aislamiento, descarga y recuperación',async t=>{
 if(!chromium){t.skip('Requiere Playwright en NODE_PATH y Chrome.');return}
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'revision145-'));
 const data={version:1,muestra:'fixture-145',casos:Array.from({length:42},(_,i)=>({id:`Llamada ${String(i+1).padStart(2,'0')}`,turnos:[{hablante:'OTRA',texto:'<script>NO EJECUTAR</script>'},{hablante:'PROTEGIDA',texto:'No voy a hacer eso.'},{hablante:'OTRA',texto:'Fin.'}]}))};
 const template=await fs.readFile(path.join(__dirname,'../analisis/tablero/revision_145_plantilla.html'),'utf8');
 const html=template.replace('__DATOS_REVISION__',JSON.stringify(data).replaceAll('<','\\u003c'));
 const file=path.join(dir,'fichas.html');await fs.writeFile(file,html);
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage({acceptDownloads:true});const pageErrors=[];page.on('pageerror',e=>pageErrors.push(e.message));
  await page.goto(pathToFileURL(file).href);
  await page.locator('#reviewer').fill('Revisor de prueba');await page.locator('#start').click();
  assert.equal(await page.locator('.turn').count(),3);assert.equal(await page.locator('.turn script').count(),0);
  await page.locator('[name=completa]').click();assert.equal(await page.locator('[name=completa]').isChecked(),false);assert.match(await page.locator('#errors').textContent(),/Respondé/);
  for(const name of ['credibilidad','estafa','sospecha','pedido'])await page.locator(`[name=${name}][value=si]`).check();
  await page.locator('[name=cumplimiento][value=no]').check();
  for(const name of ['fundamento','motivo_sospecha','motivo_pedido'])await page.locator(`[name=${name}]`).fill('Fundamento ficticio, línea 1.');
  await page.locator('[data-line="1"]').click();await page.locator('#mark-target').selectOption('pedido');await page.locator('[data-line="1"]').click();
  await page.locator('[name=completa]').check();assert.match(await page.locator('#count').textContent(),/1 de 42/);
  await page.reload();await page.locator('#reviewer').fill('Revisor de prueba');await page.locator('#start').click();assert.equal(await page.locator('[name=completa]').isChecked(),true);
  await page.locator('[name=observaciones]').fill('Una corrección vuelve a pendiente.');assert.equal(await page.locator('[name=completa]').isChecked(),false);
  await page.locator('[name=completa]').check();await page.locator('#next').click();assert.equal(await page.locator('[name=estafa]:checked').count(),0);
  const downloading=page.waitForEvent('download');await page.locator('#export').click();const download=await downloading;const exported=JSON.parse(await fs.readFile(await download.path(),'utf8'));
  assert.equal(exported.respuestas['Llamada 01'].completa,true);assert.equal(exported.revisor,'Revisor de prueba');assert.equal(exported.muestra,'fixture-145');
  await page.locator('#change').click();await page.locator('#reviewer').fill('Otra persona');await page.locator('#start').click();assert.equal(await page.locator('[name=estafa]:checked').count(),0);assert.match(await page.locator('#count').textContent(),/0 de 42/);
  const other=await browser.newPage();await other.goto(pathToFileURL(file).href);await other.locator('#import').setInputFiles({name:'respuestas.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(exported))});assert.equal(await other.locator('#reviewer').inputValue(),'Revisor de prueba');
  await other.locator('#case-select').selectOption('0');assert.equal(await other.locator('[name=completa]').isChecked(),true);
  const wrong={...exported,muestra:'otra'};await other.locator('#import').setInputFiles({name:'otra.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(wrong))});assert.match(await other.locator('#status').textContent(),/otra muestra/);assert.equal(await other.locator('[name=completa]').isChecked(),true);
  await other.setViewportSize({width:390,height:844});assert.equal(await other.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  // Un número fuera de rango en una ficha pendiente no vuelve irrecuperable el resto.
  await other.locator('#case-select').selectOption('1');await other.locator('[name=sospecha][value=si]').check();await other.locator('[name=sospecha_linea]').fill('0');
  await other.reload();await other.locator('#reviewer').fill('Revisor de prueba');await other.locator('#start').click();assert.equal(await other.locator('[name=sospecha_linea]').inputValue(),'0');
  await other.locator('#case-select').selectOption('0');assert.equal(await other.locator('[name=completa]').isChecked(),true);
  assert.deepEqual(pageErrors,[]);
 }finally{await browser.close();await fs.rm(dir,{recursive:true,force:true})}
});
