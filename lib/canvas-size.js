// SJCanvas — DPR-aware canvas sizing for full-viewport demos.
//
// The common pattern: set the canvas backing store to innerWidth/Height × dpr
// for sharp pixels, set CSS width/height to innerWidth/Height for layout, and
// apply a transform to ctx so all draw coordinates are in CSS pixels. Without
// this, canvas renders blurry on retina or at 50% size on fractional-DPR
// displays (external monitors at 1.25×, 1.5×, etc.).
//
// Usage:
//   const canvas = document.getElementById('c');
//   const ctx    = canvas.getContext('2d');
//   window.SJCanvas.fit(canvas, ctx);
//   // canvas is now sized correctly + re-fits on window resize.
//
// For WebGL contexts (no setTransform), pass ctx = null:
//   window.SJCanvas.fit(canvas, null);
//   // Use canvas.width / canvas.height in your render code.
//
// Returns an unsubscribe function. Call it to detach the resize listener
// when tearing down a demo:
//   const stop = window.SJCanvas.fit(canvas, ctx);
//   // later:
//   stop();

(() => {
  function fit(canvas, ctx) {
    const apply = () => {
      const dpr = window.devicePixelRatio || 1;
      const w = window.innerWidth;
      const h = window.innerHeight;
      canvas.width  = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      canvas.style.width  = w + 'px';
      canvas.style.height = h + 'px';
      if (ctx && ctx.setTransform) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
    };
    apply();
    window.addEventListener('resize', apply);
    return () => window.removeEventListener('resize', apply);
  }

  window.SJCanvas = { fit };
})();
