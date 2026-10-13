const path=require('path'),fs=require('fs'),assert=require('assert/strict');
const {pathToFileURL}=require('url');
const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
(async()=>{
const root=path.resolve(__dirname,'..');
const browser=await chromium.launch({headless:true,channel:'msedge'});
const page=await browser.newPage({viewport:{width:1440,height:960},reducedMotion:'reduce'});
const errors=[],overflow=[];page.on('pageerror',e=>errors.push(e.message));
for(const file of ['ders-03.html','odev-03.html']){
 await page.goto(pathToFileURL(path.join(root,file)).href);
 const n=await page.evaluate(()=>SLIDES.length);
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:960});
  for(let i=0;i<n;i++){await page.evaluate(i=>show(i),i);if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))overflow.push(file+':'+(i+1)+'@'+width);}
 }
 await page.setViewportSize({width:1440,height:960});await page.evaluate(()=>show(0));await page.screenshot({path:path.join(root,'validation',file+'.png'),fullPage:true});
 await page.click('#notes');assert.equal(await page.locator('.note').isVisible(),true);await page.click('#toc');await page.locator('[data-slide="1"]').click();assert.equal(await page.locator('#counter').textContent(),`2 / ${n}`);
}
await page.goto(pathToFileURL(path.join(root,'ders-03.html')).href);
await page.evaluate(()=>show(SLIDES.findIndex(s=>s.body.includes('id="copyValue"'))));await page.click('#copySend');await page.click('#copyChange');assert.equal(await page.locator('#queueValue').textContent(),'42');assert.equal(await page.locator('#copyValue').textContent(),'99');
await page.goto(pathToFileURL(path.join(root,'interface/index.html')).href);
const files=fs.readdirSync(path.join(root,'measurements/hardware')).filter(n=>n.endsWith('.txt'));
for(const file of files)await page.locator('#import').setInputFiles(path.join(root,'measurements/hardware',file));
await page.waitForFunction(n=>document.querySelectorAll('.result').length===n,files.length);
assert.equal(await page.locator('.result').count(),files.length);
const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('button',{name:'.SVDat indir',exact:true}).first().click()]);
const downloadPath=await download.path();assert.ok(fs.statSync(downloadPath).size>10000);
await page.screenshot({path:path.join(root,'validation/recording-desk.png'),fullPage:true});
await page.setViewportSize({width:390,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))overflow.push('interface@390');
for(const file of ['index.html','docs/SystemView_Kurulum.html','docs/Dogrulama.html']){
 await page.goto(pathToFileURL(path.join(root,file)).href);if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))overflow.push(file+'@390');
}
const report={errors,overflow,imported_hardware_sessions:files.length,downloads:'SVDat passed',interactions:'copy, notes, contents passed; queue scenarios covered by dedicated QA'};
fs.writeFileSync(path.join(root,'validation/browser-qa.json'),JSON.stringify(report,null,2));console.log(report);
assert.equal(errors.length,0);assert.equal(overflow.length,0);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
