'use strict';
// Усі суми зберігаються як BigInt з фіксованою точністю 8 знаків (1 = 100_000_000 одиниць).
// Жодних float у грошових розрахунках.
const SCALE = 100000000n;
const RE = /^\d{1,15}(\.\d{1,8})?$/;

function toUnits(v) {
  if (typeof v === 'number') {
    if (!Number.isFinite(v) || v < 0) return null;
    v = v.toFixed(8);
  }
  if (typeof v !== 'string') return null;
  v = v.trim();
  if (!RE.test(v)) return null;
  const [i, f = ''] = v.split('.');
  return BigInt(i) * SCALE + BigInt((f + '00000000').slice(0, 8));
}

function fmt(u) {
  if (u === null || u === undefined) return null;
  const neg = u < 0n;
  if (neg) u = -u;
  const f = (u % SCALE).toString().padStart(8, '0').replace(/0+$/, '');
  return (neg ? '-' : '') + (u / SCALE).toString() + (f ? '.' + f : '');
}

const min = (a, b) => (a < b ? a : b);

module.exports = { SCALE, toUnits, fmt, min };
