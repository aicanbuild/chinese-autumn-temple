// Recover fine detail after entering a cheaper view. Separate thresholds and a
// cooldown prevent resolution pumping when performance sits near a boundary.
export function createRenderQuality(maxPixelRatio){
 const ceiling=Math.max(.5,Math.min(maxPixelRatio,1.6));
 const levels=[...new Set([Math.min(1.1,ceiling),Math.min(1.35,ceiling),ceiling])];
 let index=levels.length-1,fastWindows=0,changedAt=-Infinity;
 return {
  get pixelRatio(){return levels[index];},
  sample(frameMs,nowSeconds){
   if(!Number.isFinite(frameMs)||frameMs<=0)return null;
   if(nowSeconds-changedAt<12){fastWindows=0;return null;}
   if(frameMs>40&&index>0){index--;fastWindows=0;changedAt=nowSeconds;return levels[index];}
   fastWindows=frameMs<25?fastWindows+1:0;
   if(fastWindows>=2&&index<levels.length-1){index++;fastWindows=0;changedAt=nowSeconds;return levels[index];}
   return null;
  }
 };
}
