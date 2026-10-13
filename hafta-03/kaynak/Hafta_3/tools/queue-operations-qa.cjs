const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
const path=require('path'),fs=require('fs'),assert=require('node:assert/strict'),{pathToFileURL}=require('url');
(async()=>{
 const root=path.resolve(__dirname,'..'),browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:960}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'ders-03.html')).href);
 const i=await page.evaluate(()=>SLIDES.findIndex(s=>s.body.includes('id="queueOperations"')));await page.evaluate(i=>show(i),i);
 const order=()=>page.locator('#qOrder').textContent();
 async function action(id){await page.click('#'+id);await page.waitForFunction(()=>document.querySelector('#queueOperations').getAttribute('aria-busy')==='false');}
 async function send(value,id){await page.fill('#qValue',String(value));await action(id);}
 await action('qReceive');assert.match(await page.locator('#qCode').textContent(),/errQUEUE_EMPTY/);assert.equal(await page.locator('#qOut').textContent(),'—');
 await send(10,'qBack');await send(20,'qBack');await send(99,'qFront');assert.equal(await order(),'[ 99 → 10 → 20 ]');
 await action('qPeek');assert.equal(await order(),'[ 99 → 10 → 20 ]');assert.equal(await page.locator('#qOut').textContent(),'99');
 await action('qReceive');assert.equal(await order(),'[ 10 → 20 ]');assert.equal(await page.locator('#qOut').textContent(),'99');
 await send(30,'qBack');await send(40,'qBack');await send(50,'qBack');await send(60,'qBack');const full=await order();await send(88,'qFront');assert.equal(await order(),full);assert.match(await page.locator('#qCode').textContent(),/errQUEUE_FULL/);
 await action('qReset');await send(10,'qFront');await send(20,'qFront');assert.equal(await order(),'[ 20 → 10 ]');
 await action('qReset');for(let j=0;j<6;j++)await action('qDemo');assert.equal(await order(),'[ 20 ]');
 await action('qDemo');assert.equal(await order(),'[ 10 ]');
 await send(20,'qBack');await send(99,'qFront');await action('qPeek');
 await page.screenshot({path:path.join(root,'validation/queue-operations-desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await page.screenshot({path:path.join(root,'validation/queue-operations-mobile.png'),fullPage:true});
 // Reset and navigation must cancel ongoing animations without stale mutations.
 await page.setViewportSize({width:1440,height:960});await action('qReset');await page.click('#qBack');await page.click('#qReset');await page.waitForTimeout(900);assert.equal(await order(),'[ boş ]');
 await page.click('#qBack');await page.evaluate(()=>show(0));await page.waitForTimeout(900);assert.match(await page.locator('#counter').textContent(),/^1 \/ /);
 await page.emulateMedia({reducedMotion:'reduce'});await page.evaluate(i=>show(i),i);await send(42,'qBack');assert.equal(await order(),'[ 42 ]');
 assert.deepEqual(errors,[]);const result={passed:true,slide:i+1,errors,cases:['front/back order','front-front reverses insertion order','receive removes head','peek preserves head','full does not overwrite','empty preserves output','guided demo','reset/navigation during animation','reduced motion','mobile no page overflow']};
 fs.writeFileSync(path.join(root,'validation/queue-operations-qa.json'),JSON.stringify(result,null,2));console.log(result);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
