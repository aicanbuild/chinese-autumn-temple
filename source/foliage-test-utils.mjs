import fs from 'node:fs';import * as THREE from '../dist/vendor/three/three.module.js';
const code=fs.readFileSync(new URL('../dist/foliage-wind.js',import.meta.url),'utf8').replace(/^import.*;$/gm,'').replaceAll('export function','function');
export const {applyCanopyWind,applyWoodlandWind,createWindShadows}=new Function('THREE',code+';return {applyCanopyWind,applyWoodlandWind,createWindShadows}')(THREE);
