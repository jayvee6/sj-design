// VizEnv — attack/release envelope followers for any time-driven signal.
// A one-pole exponential filter with independent attack and release time
// constants plus optional per-phase curve shaping. Gives more musical
// onset response than ad-hoc EMAs: parameters snap up on transients but
// tail down smoothly.
//
// General-purpose — use it for:
//   • audio-reactive viz (bass/mid/treble smoothing)
//   • synthetic pulse smoothing in motion demos (computePulse(t) → follow)
//   • cursor-following parallax (targetX → smoothed position per frame)
//   • scroll-driven animation (scrollY → eased progress)
//   • hover state transitions with distinct enter/leave speeds
//   • any "snap up, ease down" or "ease up, snap down" behavior
//
// Pattern inspired by Sebastian Lague's Audio-Experiments `EnvelopeADR.cs`
// (MIT — https://github.com/SebLague/Audio-Experiments).
// Ported to sj-design from musicplayer-viz where it ships as an audio utility.
//
// Two ways to use:
//
// 1. Stateless function — caller keeps the running value:
//      let smoothed = 0;
//      // in render loop:
//      smoothed = window.VizEnv.follow(smoothed, target, dt, { attack: 0.02, release: 0.2 });
//
// 2. Stateful class — encapsulates current value + params:
//      const pulseEnv = new window.VizEnv.Envelope({ attack: 0.015, release: 0.25 });
//      // in render loop:
//      const v = pulseEnv.follow(target, dt);
//
// Typical parameter choices:
//   kick/pulse punch:  attack 0.010 release 0.25   (punchy rise, long tail)
//   cursor trailing:   attack 0.080 release 0.08   (symmetric, natural drag)
//   hi-hat / flash:    attack 0.005 release 0.08   (snap up, snap down)
//   scene breathing:   attack 0.25  release 1.5    (slow ambient drift)
//   hover state:       attack 0.15  release 0.35   (enter quicker than exit)
//
// `attackCurve` / `releaseCurve` shape the transient:
//   curve = 1.0  → linear-in-time one-pole (default, fine for most cases)
//   curve < 1.0  → ease-out (fast start, soft settle — feels "snappy")
//   curve > 1.0  → ease-in (soft start, hard finish — feels "reluctant")

(() => {
  const DEFAULT_ATTACK  = 0.02;
  const DEFAULT_RELEASE = 0.15;

  // One-pole exponential follower. k = 1 - exp(-dt / tau) gives the fraction
  // of remaining gap we close per frame; choosing tau as the attack or
  // release time constant means ~63% of the gap closes in one tau.
  function follow(cur, target, dt, opts) {
    const o = opts || {};
    const attack       = o.attack       != null ? o.attack       : DEFAULT_ATTACK;
    const release      = o.release      != null ? o.release      : DEFAULT_RELEASE;
    const attackCurve  = o.attackCurve  != null ? o.attackCurve  : 1.0;
    const releaseCurve = o.releaseCurve != null ? o.releaseCurve : 1.0;

    const rising = target > cur;
    const tau    = rising ? attack : release;
    if (tau <= 0) return target; // zero time-constant → instant follow
    let k = 1 - Math.exp(-dt / tau);
    const curve = rising ? attackCurve : releaseCurve;
    if (curve !== 1.0) k = Math.pow(k, curve);
    return cur + (target - cur) * k;
  }

  class Envelope {
    constructor(opts) {
      const o = opts || {};
      this.attack       = o.attack       != null ? o.attack       : DEFAULT_ATTACK;
      this.release      = o.release      != null ? o.release      : DEFAULT_RELEASE;
      this.attackCurve  = o.attackCurve  != null ? o.attackCurve  : 1.0;
      this.releaseCurve = o.releaseCurve != null ? o.releaseCurve : 1.0;
      this.value = o.initial != null ? o.initial : 0;
    }
    follow(target, dt) {
      this.value = follow(this.value, target, dt, this);
      return this.value;
    }
    reset(v) { this.value = v != null ? v : 0; }
  }

  // Apply an envelope follower element-wise over a typed array. `state` and
  // `target` must be the same length. Mutates `state` in place. Useful for
  // smoothing any N-dimensional target (spectrum bins, vertex positions,
  // color channels) across frames so per-element jitter doesn't leak into
  // the render.
  function followArray(state, target, dt, opts) {
    const o = opts || {};
    const attack       = o.attack       != null ? o.attack       : DEFAULT_ATTACK;
    const release      = o.release      != null ? o.release      : DEFAULT_RELEASE;
    const attackCurve  = o.attackCurve  != null ? o.attackCurve  : 1.0;
    const releaseCurve = o.releaseCurve != null ? o.releaseCurve : 1.0;
    const n = Math.min(state.length, target.length);
    for (let i = 0; i < n; i++) {
      const cur = state[i];
      const tgt = target[i];
      const rising = tgt > cur;
      const tau = rising ? attack : release;
      if (tau <= 0) { state[i] = tgt; continue; }
      let k = 1 - Math.exp(-dt / tau);
      const curve = rising ? attackCurve : releaseCurve;
      if (curve !== 1.0) k = Math.pow(k, curve);
      state[i] = cur + (tgt - cur) * k;
    }
  }

  window.VizEnv = { follow, followArray, Envelope };
})();
