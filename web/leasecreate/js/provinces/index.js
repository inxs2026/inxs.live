// Province registry — all Canadian provinces
import { ontario } from './ontario.js';
import { bc } from './bc.js';
import { alberta } from './alberta.js';
import { quebec } from './quebec.js';
import { manitoba } from './manitoba.js';
import { saskatchewan } from './saskatchewan.js';
import { novaScotia } from './nova-scotia.js';
import { newBrunswick } from './new-brunswick.js';
import { pei } from './pei.js';
import { newfoundland } from './newfoundland.js';

export const provinces = {
  ON: ontario,
  BC: bc,
  AB: alberta,
  QC: quebec,
  MB: manitoba,
  SK: saskatchewan,
  NS: novaScotia,
  NB: newBrunswick,
  PE: pei,
  NL: newfoundland,
};

// Sorted for dropdown
export const provinceList = Object.values(provinces).sort((a, b) => a.name.localeCompare(b.name));
