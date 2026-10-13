// Filled in the generated runtime; source modules remain directly inspectable.
const assetVersions = {};
export function versionAssetUrl(url){
 const key=url.split(/[?#]/)[0].replace(/^\.\//,'');
 const version=assetVersions[key];
 if(!version||/[?&]v=/.test(url))return url;
 const [path,fragment]=url.split('#');
 return path+(path.includes('?')?'&':'?')+'v='+version+(fragment?'#'+fragment:'');
}
