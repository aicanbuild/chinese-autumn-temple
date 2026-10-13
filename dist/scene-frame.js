// All animation runs before this boundary. Water and AO render the same world
// repeatedly; share its matrices while allowing each virtual camera to update.
// Do not use for scenes whose render callbacks change Object3D transforms.
export function renderSceneFrame(scene,render){
 const auto=scene.matrixWorldAutoUpdate;
 if(auto)scene.updateMatrixWorld();
 scene.matrixWorldAutoUpdate=false;
 try{return render();}finally{scene.matrixWorldAutoUpdate=auto;}
}
