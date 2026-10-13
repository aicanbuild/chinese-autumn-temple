// Reference shader from published 3eabe639 for controlled A/B verification.
export const waterProjectionGLSL=`
uniform float waterRefractionPass;
uniform float waterInterfaceY;
vec3 waterSurfaceExit(vec3 p,vec3 eye){
 float D=waterInterfaceY-p.y,H=eye.y-waterInterfaceY;
 vec2 delta=p.xz-eye.xz;float L=length(delta),n=1.333;
 if(D<=0.||H<=.001||L<.000001)return vec3(p.x,waterInterfaceY,p.z);
 float maximum=min(L/D,1./sqrt(n*n-1.));
 float u=min(maximum,L/sqrt(n*n*H*H+(n*n-1.)*L*L)),low=0.,high=maximum;
 for(int i=0;i<5;i++){
  float x=L-D*u,a=sqrt(x*x+H*H),b=sqrt(u*u+1.),f=x/a-n*u/b;
  if(f>0.)low=u;else high=u;
  float derivative=-D*H*H/(a*a*a)-n/(b*b*b);
  u=clamp(u-f/derivative,low,high);
 }
 float x=L-D*u,residual=x/sqrt(x*x+H*H)-n*u/sqrt(u*u+1.);
 if(abs(residual)*D>.00002*.38){
  for(int i=0;i<16;i++){float q=(low+high)*.5,air=L-D*q;if(air/sqrt(air*air+H*H)>n*q/sqrt(q*q+1.))low=q;else high=q;}
  u=(low+high)*.5;
 }
 x=L-D*u;
 return vec3(eye.x+delta.x*x/L,waterInterfaceY,eye.z+delta.y*x/L);
}`;
