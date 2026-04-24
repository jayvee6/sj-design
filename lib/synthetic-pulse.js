// SJPulse — synthetic time-driven pulse generators.
//
// Every motion demo in sj-design has an optional audio-reactive hook; for
// the standalone case we drive the visual from deterministic math instead.
// This module is the shared source of "feels-like-music" signals so demos
// don't each reinvent their own sine stack.
//
// Three flavors, all pure functions of `t` (seconds):
//
//   SJPulse.kick(t)     — punchy bass-style pulse. Half-wave rectified sine
//                         squared, plus a ghost-note overtone. Output [0,1].
//                         Best for: ring expansions, size pops, color flashes.
//
//   SJPulse.wave(t)     — slow rolling mid-range drift. Single low-freq sine
//                         centered around `mid`. Output [mid-amp, mid+amp].
//                         Best for: tunnel rotation, ambient breathing.
//
//   SJPulse.flicker(t)  — fast treble-style sparkle. |sin(t·rate)|. Output
//                         [0, 1] with frequent rapid peaks.
//                         Best for: edge glow, trail opacity, high-freq detail.
//
// Each takes an `opts` object to override the defaults. All defaults are
// tuned to feel musical at 60fps without any audio input.
//
// Usage:
//   const t = (performance.now() - t0) / 1000;
//   const bass = window.SJPulse.kick(t);
//   const mid  = window.SJPulse.wave(t);
//   const high = window.SJPulse.flicker(t);
//
// To wire back to real audio, replace these calls with reads from your
// audio frame:
//   const bass = audioFrame.bass;
//   const mid  = audioFrame.mid;
//   const high = audioFrame.treble;

(() => {
  function kick(t, opts) {
    const o = opts || {};
    const kickRate  = o.kickRate  != null ? o.kickRate  : 2.2;   // Hz of primary pulse
    const ghostRate = o.ghostRate != null ? o.ghostRate : 5.1;   // Hz of ghost overtone
    const ghostAmp  = o.ghostAmp  != null ? o.ghostAmp  : 0.35;
    const k = Math.max(0, Math.sin(t * kickRate));
    const g = Math.max(0, Math.sin(t * ghostRate + 1.3)) * ghostAmp;
    return Math.min(1, Math.pow(k, 2) * 0.9 + g);
  }

  function wave(t, opts) {
    const o = opts || {};
    const rate = o.rate != null ? o.rate : 0.55;
    const mid  = o.mid  != null ? o.mid  : 0.35;
    const amp  = o.amp  != null ? o.amp  : 0.25;
    return mid + amp * Math.sin(t * rate);
  }

  function flicker(t, opts) {
    const o = opts || {};
    const rate = o.rate != null ? o.rate : 4.0;
    return Math.abs(Math.sin(t * rate));
  }

  window.SJPulse = { kick, wave, flicker };
})();
