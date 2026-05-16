// SJGpu — standalone WebGPU bootstrap for sj-design scene demos.
//
// Ported from musicplayer-viz/app.js initWebGPU(). That repo's web graphics
// stack is 100% raw WebGPU now — no Three.js, no TSL, WGSL as inline
// template literals, single render pass, zero postprocessing. sj-design
// scene demos mirror that exactly.
//
// Usage:
//   const gpu = await window.SJGpu.init(canvas);
//   if (!gpu) return;                       // overlay already shown
//   const { device, queue, context, format } = gpu;
//   // ... createShaderModule / createRenderPipeline / bind group ...
//   function frame(ts) {
//     // gpu.canvas.width / .height are physical px (DPR-scaled) — use for aspect
//     const enc  = device.createCommandEncoder();
//     const pass = enc.beginRenderPass({ colorAttachments: [{
//       view: context.getCurrentTexture().createView(),
//       loadOp: 'clear', storeOp: 'store', clearValue: { r:0,g:0,b:0,a:1 } }] });
//     pass.setPipeline(pipeline); pass.setBindGroup(0, bg); pass.draw(3);
//     pass.end(); queue.submit([enc.finish()]);
//     requestAnimationFrame(frame);
//   }
//   requestAnimationFrame(frame);
//
// init() returns null and paints a centered "WebGPU unavailable" overlay
// when navigator.gpu is missing or no adapter is returned, so a demo
// degrades to an honest message instead of a blank canvas. There is NO
// WebGL fallback — same as the musicplayer-viz fleet.

(() => {
  function showUnavailable(canvas, reason) {
    const host = canvas.parentElement || document.body;
    const el = document.createElement('div');
    el.setAttribute('data-sjgpu-msg', '');
    Object.assign(el.style, {
      position: 'fixed', inset: '0', zIndex: '50',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', gap: '10px', textAlign: 'center',
      padding: '32px', pointerEvents: 'none',
      font: '600 14px -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
      color: '#8e8e93',
    });
    el.innerHTML =
      '<div style="font-size:32px;opacity:0.5;">⚡</div>' +
      '<div style="color:#f5f5f7;font-size:15px;">WebGPU unavailable</div>' +
      '<div style="max-width:320px;line-height:1.55;">' + reason +
      ' Try a recent Chrome, Edge, or Safari Technology Preview.</div>';
    host.appendChild(el);
  }

  // Size the canvas backing store. WebGPU does not need context.configure()
  // re-called on resize — only the backing-store dimensions change; scenes
  // read canvas.width/height for aspect ratio (preserved — both axes scale
  // by the same factor).
  //
  // For fragment-bound scenes (raymarchers especially) resolution is THE
  // perf lever — halving it is ~4× fewer fragments. Two knobs:
  //   opts.maxDPR      — clamp device pixel ratio (default 2; retina caps here)
  //   opts.renderScale — extra multiplier on the backing store (default 1;
  //                       a heavy scene passes e.g. 0.66 and the GPU upscales
  //                       to the unchanged CSS size — blur hidden by motion)
  function sizeCanvas(canvas, opts) {
    const o = opts || {};
    const maxDPR = o.maxDPR != null ? o.maxDPR : 2;
    const scale  = o.renderScale != null ? o.renderScale : 1;
    const dpr = Math.min(window.devicePixelRatio || 1, maxDPR) * scale;
    canvas.width  = Math.max(1, Math.round(window.innerWidth  * dpr));
    canvas.height = Math.max(1, Math.round(window.innerHeight * dpr));
    canvas.style.width  = window.innerWidth  + 'px';   // CSS stays full size
    canvas.style.height = window.innerHeight + 'px';    // → hardware upscales
    return dpr;
  }

  async function init(canvas, opts) {
    const o = opts || {};
    if (!navigator.gpu) {
      showUnavailable(canvas, 'This browser has no navigator.gpu.');
      return null;
    }
    let adapter;
    try {
      adapter = await navigator.gpu.requestAdapter({
        powerPreference: o.powerPreference || 'high-performance',
      });
    } catch (err) {
      showUnavailable(canvas, 'Adapter request failed: ' + err.message + '.');
      return null;
    }
    if (!adapter) {
      showUnavailable(canvas, 'No GPU adapter returned.');
      return null;
    }
    const device  = await adapter.requestDevice();
    const dpr     = sizeCanvas(canvas, o);
    const context = canvas.getContext('webgpu');
    const format  = navigator.gpu.getPreferredCanvasFormat();
    context.configure({ device, format, alphaMode: 'opaque' });

    const gpu = { adapter, device, queue: device.queue, context, format, canvas, dpr };

    // Re-size the backing store on viewport change (same opts). No reconfigure.
    window.addEventListener('resize', () => { gpu.dpr = sizeCanvas(canvas, o); });

    return gpu;
  }

  window.SJGpu = { init };
})();
