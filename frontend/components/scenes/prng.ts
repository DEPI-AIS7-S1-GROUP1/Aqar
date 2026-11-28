/** Small deterministic PRNG so illustrations render the same on server and client. */
export function prng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hashString(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export interface Win {
  x: number;
  y: number;
  w: number;
  h: number;
  lit: boolean;
  flicker: boolean;
}

/** Window grid for a building rectangle. */
export function windows(
  seed: number,
  x: number,
  y: number,
  w: number,
  h: number,
  cols: number,
  rows: number,
  litRatio = 0.45
): Win[] {
  const r = prng(seed);
  const out: Win[] = [];
  const gx = w / cols;
  const gy = h / rows;
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      const v = r();
      out.push({
        x: x + i * gx + gx * 0.25,
        y: y + j * gy + gy * 0.25,
        w: gx * 0.5,
        h: gy * 0.5,
        lit: v < litRatio,
        flicker: v < 0.04,
      });
    }
  }
  return out;
}
