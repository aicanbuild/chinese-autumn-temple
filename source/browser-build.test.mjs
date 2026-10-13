import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';

test('browser builds invalidate the whole module graph when an asset changes, and keep one rollback',async()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'temple-build-'));
 try{
  for(const dir of ['source','dist/assets','dist/ambience','dist/vendor/three/addons/objects'])fs.mkdirSync(path.join(root,dir),{recursive:true});
  fs.writeFileSync(path.join(root,'package.json'),'{"type":"module"}');
  for(const file of ['source/build_browser.py','dist/asset-versions.js'])fs.copyFileSync(new URL('../'+file,import.meta.url),path.join(root,file));
  const write=(file,text)=>fs.writeFileSync(path.join(root,'dist',file),text);
  write('index.html','<link href="./style.css"><script type="importmap">{"imports":{}}</script><script type="module" src="./app.js"></script>');
  write('style.css','body{}');write('app.js',"import {versionAssetUrl} from './asset-versions.js';");write('vendor/three/addons/objects/Water2.js','// water');write('assets/model.glb','first');
  const build=()=>JSON.parse(execFileSync('python3',[path.join(root,'source/build_browser.py')],{encoding:'utf8'}));
  const first=build();assert.equal(build().runtime,first.runtime,'unchanged builds must be stable');
  const helper=await import(pathToFileURL(path.join(root,'dist/runtime',first.runtime,'asset-versions.js')));
  assert.match(helper.versionAssetUrl('./assets/model.glb'),/^\.\/assets\/model\.glb\?v=[0-9a-f]{12}$/);
  assert.match(helper.versionAssetUrl('./assets/model.glb?quality=full#mesh'),/\?quality=full&v=[0-9a-f]{12}#mesh$/);
  assert.equal(helper.versionAssetUrl('blob:local-id'),'blob:local-id');
  assert.equal(helper.versionAssetUrl('./assets/model.glb?v=existing'),'./assets/model.glb?v=existing');
  write('assets/model.glb','second');const second=build();assert.notEqual(second.runtime,first.runtime);assert.equal(second.previous,first.runtime);
  const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');assert.ok(html.includes(`./runtime/${second.runtime}/app.js`));assert.match(html,/Water2\.js\?v=[0-9a-f]{12}/);
  write('app.js','// changed module');const third=build();assert.notEqual(third.runtime,second.runtime);
  assert.ok(fs.existsSync(path.join(root,'dist/runtime',second.runtime)));assert.equal(fs.existsSync(path.join(root,'dist/runtime',first.runtime)),false);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});
