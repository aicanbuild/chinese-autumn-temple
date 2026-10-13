// Track only geometry which reaches the AO normal pass. Color, lights and
// excluded wind/particle layers do not change its normal/depth inputs.
export class AOSceneState{
 constructor(){this.records=new Map();this.generation=0;this.count=0;this.animated=false;}
 changed(scene,camera,exclude=()=>false,animatedVisible=()=>true){
  const generation=++this.generation;let changed=false,count=0;this.animated=false;
  const visit=o=>{
   if(!o.visible||exclude(o)||o.isPoints||o.isLine||o.isLine2)return;
   if(o.isMesh&&o.layers.test(camera.layers)){
    count++;const g=o.geometry,position=g.attributes.position,normal=g.attributes.normal,index=g.index;
    const materials=Array.isArray(o.material)?o.material:[o.material];
    // Render-list visibility and sidedness still affect normal rendering.
    const layout=[g.id,position?.data?.version??position?.version,position?.count,normal?.data?.version??normal?.version,index?.version,index?.count,g.drawRange.start,g.drawRange.count,
     ...g.groups.flatMap(v=>[v.start,v.count,v.materialIndex]),...materials.flatMap(m=>[m.visible,m.side]),...(o.morphTargetInfluences??[])].join('/');
    let record=this.records.get(o);
    if(!record){record={matrix:new Float64Array(16)};this.records.set(o,record);changed=true;}
    if(record.seen!==generation-1||record.layout!==layout||record.position!==position||record.normal!==normal||record.index!==index)changed=true;
    const matrix=o.matrixWorld.elements;
    for(let i=0;i<16;i++){if(record.matrix[i]!==matrix[i])changed=true;record.matrix[i]=matrix[i];}
    Object.assign(record,{seen:generation,layout,position,normal,index});
    // Bone poses and custom normal-pass shader animation need a periodic fallback.
    if((o.isSkinnedMesh||o.userData.aoAnimated)&&animatedVisible(o))this.animated=true;
   }
   for(const child of o.children)visit(child);
  };
  visit(scene);
  if(count!==this.count)changed=true;this.count=count;
  for(const [object,record]of this.records)if(record.seen!==generation)this.records.delete(object);
  return changed;
 }
}
