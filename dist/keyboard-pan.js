// Move the eye and its look-at point together, without tilting or zooming.
export function panWithArrowKeys(camera,controls,keys,dt,inside=false){
 const forward=Number(!!keys.ArrowUp)-Number(!!keys.ArrowDown);
 const right=Number(!!keys.ArrowRight)-Number(!!keys.ArrowLeft);
 const inputLength=Math.hypot(forward,right);
 if(!inputLength||dt<=0)return;
 let fx=controls.target.x-camera.position.x,fz=controls.target.z-camera.position.z;
 const horizontalLength=Math.hypot(fx,fz);
 if(horizontalLength>1e-6){fx/=horizontalLength;fz/=horizontalLength;}
 else{
  // Retain a stable heading even when looking straight up or down.
  const q=camera.quaternion,rx=1-2*(q.y*q.y+q.z*q.z),rz=2*(q.x*q.z-q.w*q.y);
  const length=Math.hypot(rx,rz)||1;fx=rz/length;fz=-rx/length;
 }
 const speed=inside?1.35:Math.min(6,Math.max(1.55,camera.position.distanceTo(controls.target)*.16));
 const step=speed*dt/inputLength;
 const dx=(fx*forward-fz*right)*step,dz=(fz*forward+fx*right)*step;
 camera.position.x+=dx;camera.position.z+=dz;
 controls.target.x+=dx;controls.target.z+=dz;
}
