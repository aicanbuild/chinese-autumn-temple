// Decode existing web vertices without re-exporting/recompressing the bridge.
import fs from 'node:fs';import vm from 'node:vm';import {createRequire} from 'node:module';import * as T from '../dist/vendor/three/three.module.js';
const root=new URL('../',import.meta.url),dir=new URL('dist/vendor/three/addons/libs/draco/gltf/',root),module={exports:{}};
vm.runInNewContext(fs.readFileSync(new URL('draco_wasm_wrapper.js',dir),'utf8'),{module,exports:module.exports,require:createRequire(import.meta.url),__dirname:dir.pathname,console,process,Buffer,TextDecoder,setTimeout,clearTimeout});
const draco=await module.exports({wasmBinary:fs.readFileSync(new URL('draco_decoder.wasm',dir))});
const raw=fs.readFileSync(new URL('evidence/bridge-before-contact.glb',root)),len=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+len)),bin=raw.subarray(28+len),samples=[];
function walk(index,parent){const node=doc.nodes[index],matrix=new T.Matrix4();if(node.matrix)matrix.fromArray(node.matrix);else matrix.compose(new T.Vector3(...(node.translation||[0,0,0])),new T.Quaternion(...(node.rotation||[0,0,0,1])),new T.Vector3(...(node.scale||[1,1,1])));matrix.premultiply(parent);const nm=new T.Matrix3().getNormalMatrix(matrix);
 if(node.mesh!==undefined)for(let pi=0;pi<doc.meshes[node.mesh].primitives.length;pi++){
  const p=doc.meshes[node.mesh].primitives[pi],ext=p.extensions.KHR_draco_mesh_compression,view=doc.bufferViews[ext.bufferView],bytes=bin.subarray(view.byteOffset||0,(view.byteOffset||0)+view.byteLength),decoder=new draco.Decoder(),buffer=new draco.DecoderBuffer(),mesh=new draco.Mesh();buffer.Init(bytes,bytes.length);const status=decoder.DecodeBufferToMesh(buffer,mesh);if(!status.ok())throw Error(status.error_msg());
  function attr(name){const a=decoder.GetAttributeByUniqueId(mesh,ext.attributes[name]),out=new draco.DracoFloat32Array();decoder.GetAttributeFloatForAllPoints(mesh,a,out);const data=Array.from({length:out.size()},(_,i)=>out.GetValue(i));draco.destroy(out);return data;}
  const ps=attr('POSITION'),ns=attr('NORMAL'),uv=attr('TEXCOORD_0'),positions=[],normals=[];for(let i=0;i<ps.length;i+=3){const a=new T.Vector3(...ps.slice(i,i+3)).applyMatrix4(matrix),n=new T.Vector3(...ns.slice(i,i+3)).applyMatrix3(nm).normalize();positions.push(a.x,-a.z,a.y);normals.push(n.x,-n.z,n.y);}
  const indices=[],face=new draco.DracoInt32Array();for(let i=0;i<mesh.num_faces();i++){decoder.GetFaceFromMesh(mesh,i,face);for(let k=0;k<3;k++)indices.push(face.GetValue(k));}draco.destroy(face);
  samples.push({mesh:node.mesh,primitive:pi,material:doc.materials[p.material].name,positions,normals,indices,localPositions:ps,localNormals:ns,uv});for(const o of [mesh,buffer,decoder])draco.destroy(o);
 }for(const child of node.children||[])walk(child,matrix);
}
for(const n of doc.scenes[doc.scene||0].nodes)walk(n,new T.Matrix4());fs.writeFileSync(new URL('evidence/bridge-contact-coarse.json',root),JSON.stringify(samples));console.log(samples.map(s=>({material:s.material,vertices:s.positions.length/3})));
