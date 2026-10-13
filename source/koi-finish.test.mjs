import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const b=fs.readFileSync(new URL('../dist/assets/koi/koi.glb',import.meta.url)),d=JSON.parse(b.subarray(20,20+b.readUInt32LE(12)));
test('four skins retain pigment while sharing refined normal and roughness images',()=>{
 const skins=d.materials.filter(m=>/^Koi (kohaku|sanke|yamabuki|platinum)$/.test(m.name));assert.equal(skins.length,4);const maps=[];
 for(const m of skins){const p=m.pbrMetallicRoughness;assert.equal(p.metallicFactor,0);assert.equal(p.roughnessFactor??1,1);assert.ok(p.metallicRoughnessTexture);assert.ok(m.normalTexture);assert.equal(m.normalTexture.scale??1,1);maps.push(d.textures[p.metallicRoughnessTexture.index].source);assert.ok(Math.abs(m.extensions.KHR_materials_clearcoat.clearcoatFactor-.18)<1e-6);}
 assert.equal(new Set(maps).size,1);assert.equal(d.images[maps[0]].name,'scales-rough');assert.ok(b.length<4*1024*1024);
});
test('all four bodies keep dense topology and scene fish remain sixteen',()=>{
 const bodies=d.meshes.filter(m=>m.name.startsWith('Body'));assert.equal(bodies.length,4);for(const m of bodies){const p=m.primitives[0];assert.equal(d.accessors[p.attributes.POSITION].count,3577);assert.equal(d.accessors[p.indices].count,20736);}
 const layout=JSON.parse(fs.readFileSync(new URL('./koi-flock-reference.json',import.meta.url)));assert.equal(layout.length,16);
});
