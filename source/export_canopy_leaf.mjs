import fs from 'node:fs';
import {canopyLeafProfile} from '../dist/canopy-leaf-profile.js';
fs.writeFileSync(new URL('./canopy-leaf-profile.json',import.meta.url),JSON.stringify(canopyLeafProfile()));
