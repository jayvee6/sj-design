/**
 * sj-design/assets/transitions.js
 * Pluggable slide transition engine.
 *
 * Select an effect by setting data-transition="<name>" on <html>.
 * Register custom effects with SJTransitions.register(name, fn).
 *
 * Transition function signature:
 *   fn(fromEl, toEl, dir, opts)
 *     fromEl            — outgoing .slide DOM element
 *     toEl              — incoming .slide DOM element
 *     dir               — +1 forward, -1 backward
 *     opts.onComplete()     — release animating lock (required)
 *     opts.onContentReady() — trigger animateIn() for incoming slide
 *
 * Every transition must:
 *   1. Call toEl.classList.add('active') to make it renderable.
 *   2. Call fromEl.classList.remove('active') when outgoing is gone.
 *   3. Call opts.onComplete() exactly once when finished.
 *   4. Call opts.onContentReady() when content stagger should begin.
 */

/* globals gsap */
const SJTransitions = (() => {
  'use strict';

  const registry = Object.create(null);

  /* ─────────────────────────────────────────────────────────────
     PUBLIC API
  ───────────────────────────────────────────────────────────── */

  function register(name, fn) {
    registry[name] = fn;
  }

  function run(name, fromEl, toEl, dir, opts) {
    const fn = registry[name] || registry['slide'];
    try {
      fn(fromEl, toEl, dir, opts);
    } catch (err) {
      console.warn(`[SJTransitions] "${name}" threw, falling back to slide.`, err);
      registry['slide'](fromEl, toEl, dir, opts);
    }
  }

  /* ─────────────────────────────────────────────────────────────
     SLIDE  (default — preserves original sj-design behaviour)
  ───────────────────────────────────────────────────────────── */
  register('slide', function(fromEl, toEl, dir, { onComplete, onContentReady }) {
    const dx = dir * 36;

    gsap.to(fromEl, {
      opacity: 0, x: -dx,
      duration: 0.28,
      ease: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      onComplete() {
        fromEl.classList.remove('active');
        gsap.set(fromEl, { clearProps: 'x,opacity' });
      },
    });

    gsap.set(toEl, { opacity: 1, x: dx * 0.6 });
    toEl.classList.add('active');

    gsap.to(toEl, {
      x: 0,
      duration: 0.35,
      ease: 'cubic-bezier(0.16, 1, 0.3, 1)',
      delay: 0.12,
      onComplete,
    });

    setTimeout(onContentReady, 100);
  });

  /* ─────────────────────────────────────────────────────────────
     FADE  — simple cross-dissolve
  ───────────────────────────────────────────────────────────── */
  register('fade', function(fromEl, toEl, dir, { onComplete, onContentReady }) {
    toEl.classList.add('active');
    gsap.set(toEl, { opacity: 0 });

    gsap.to(fromEl, {
      opacity: 0, duration: 0.3, ease: 'power1.out',
      onComplete() {
        fromEl.classList.remove('active');
        gsap.set(fromEl, { clearProps: 'opacity' });
      },
    });

    gsap.to(toEl, {
      opacity: 1, duration: 0.45, ease: 'power1.inOut', delay: 0.15,
      onComplete,
    });

    setTimeout(onContentReady, 260);
  });

  /* ─────────────────────────────────────────────────────────────
     CUBE  — 3D card-flip using #deck's existing perspective

     #deck already has perspective: 1400px, so rotateY on child
     .slide elements produces genuine depth without any parent change.
     We sweep fromEl away at -90/+90° while toEl sweeps in from the
     opposite side, overlapping by 15% of the total duration for a
     continuous motion feel.
  ───────────────────────────────────────────────────────────── */
  register('cube', function(fromEl, toEl, dir, { onComplete, onContentReady }) {
    const DURATION   = 0.70;
    const startAngle = dir > 0 ?  90 : -90;
    const endAngle   = dir > 0 ? -90 :  90;

    // Place toEl behind the incoming angle — not yet visible
    gsap.set(toEl, { opacity: 1, rotateY: startAngle, transformOrigin: '50% 50% 0' });
    toEl.classList.add('active');

    gsap.timeline({
      onComplete() {
        fromEl.classList.remove('active');
        gsap.set(fromEl, { clearProps: 'rotateY,opacity,transformOrigin' });
        gsap.set(toEl,   { clearProps: 'rotateY,transformOrigin' });
        onComplete();
      },
    })
    // fromEl sweeps away and fades just before it crosses 90°
    .to(fromEl, {
      rotateY: endAngle,
      opacity: 0,
      duration: DURATION * 0.72,
      ease: 'power2.in',
      transformOrigin: '50% 50% 0',
    }, 0)
    // toEl sweeps in from its side, slightly after fromEl starts moving
    .to(toEl, {
      rotateY: 0,
      duration: DURATION,
      ease: 'power2.out',
    }, DURATION * 0.15);

    setTimeout(onContentReady, Math.round(DURATION * 850));
  });

  /* ─────────────────────────────────────────────────────────────
     IRIS  — expanding circle reveal via CSS clip-path

     The CSS transition handles interpolation; we just manage the
     before/after states and the synchronous reflow trick that
     commits the "closed" state before opening.

     150% is safe from any click origin — the maximum from-corner-
     to-corner distance is ≈141% of the clip-path reference length.
  ───────────────────────────────────────────────────────────── */
  register('iris', function(fromEl, toEl, dir, { onComplete, onContentReady }) {
    const EASE     = 'cubic-bezier(0.16, 1, 0.3, 1)';
    const DURATION = '0.80s';

    toEl.classList.add('active');

    // Snap closed (no transition active yet)
    toEl.style.transition = 'none';
    toEl.style.clipPath   = 'circle(0% at 50% 50%)';
    toEl.style.opacity    = '1';

    // Synchronous reflow — commits the closed state so the
    // browser doesn't batch it with the upcoming open state
    void toEl.offsetHeight;

    // Open the iris
    toEl.style.transition = `clip-path ${DURATION} ${EASE}`;
    toEl.style.clipPath   = 'circle(150% at 50% 50%)';

    // Fade out the outgoing slide partway through
    gsap.to(fromEl, {
      opacity: 0,
      duration: 0.3,
      delay: 0.35,
      ease: 'power1.out',
      onComplete() {
        fromEl.classList.remove('active');
        gsap.set(fromEl, { clearProps: 'opacity' });
      },
    });

    toEl.addEventListener('transitionend', function onEnd(e) {
      if (e.propertyName !== 'clip-path') return;
      toEl.removeEventListener('transitionend', onEnd);
      toEl.style.transition = '';
      toEl.style.clipPath   = '';
      onComplete();
    });

    setTimeout(onContentReady, 560);
  });

  /* ─────────────────────────────────────────────────────────────
     PARTICLES  — canvas shard dissolve

     Reads fromEl's screen rect via getBoundingClientRect().
     Spawns physics-driven glass shards at that position,
     immediately hides fromEl, and shows toEl behind the shards.

     A persistent canvas (#sj-fx-canvas) is created on first use
     and reused on subsequent navigations.
  ───────────────────────────────────────────────────────────── */
  register('particles', function(fromEl, toEl, dir, { onComplete, onContentReady }) {
    const rect = fromEl.getBoundingClientRect();

    // ── Canvas setup ──────────────────────────────────────────
    let canvas = document.getElementById('sj-fx-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'sj-fx-canvas';
      Object.assign(canvas.style, {
        position: 'fixed', top: '0', left: '0',
        width: '100%', height: '100%',
        pointerEvents: 'none', zIndex: '99999',
      });
      document.body.appendChild(canvas);
    }
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');

    // ── Colour palette: accent from CSS custom prop + bg ──────
    const cs      = window.getComputedStyle(fromEl);
    const accent  = cs.getPropertyValue('--accent').trim() || '#a0a0a0';
    const palette = [accent, '#ffffff', 'rgba(255,255,255,0.55)',
                     'rgba(255,255,255,0.25)', accent, accent];

    // ── Particle class ────────────────────────────────────────
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;

    class Shard {
      constructor() {
        this.x = rect.left + Math.random() * rect.width;
        this.y = rect.top  + Math.random() * rect.height;
        const dx    = this.x - cx, dy = this.y - cy;
        const dist  = Math.hypot(dx, dy) + 0.001;
        const speed = 1.5 + Math.random() * 7;
        this.vx   = (dx / dist) * speed + (Math.random() - 0.5) * 3;
        this.vy   = (dy / dist) * speed - (2 + Math.random() * 6);
        this.w    = 3 + Math.random() * 7;
        this.h    = this.w * (0.3 + Math.random());
        this.rot  = Math.random() * Math.PI * 2;
        this.spin = (Math.random() - 0.5) * 0.28;
        this.life = 0.85 + Math.random() * 0.15;
        this.decay= 0.007 + Math.random() * 0.012;
        this.col  = palette[Math.floor(Math.random() * palette.length)];
      }
      update() {
        this.vy   += 0.28; this.vx *= 0.982; this.vy *= 0.995;
        this.x    += this.vx; this.y += this.vy; this.rot += this.spin;
        this.life -= this.decay;
      }
      draw() {
        ctx.save();
        ctx.globalAlpha = Math.max(0, this.life) * 0.9;
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rot);
        ctx.fillStyle = this.col;
        ctx.fillRect(-this.w / 2, -this.h / 2, this.w, this.h);
        ctx.fillStyle = `rgba(255,255,255,${0.55 * this.life})`;
        ctx.fillRect(-this.w / 2, -this.h / 2, this.w, Math.max(1.5, this.h * 0.18));
        ctx.restore();
      }
      get isDead() { return this.life <= 0 || this.y > canvas.height + 60; }
    }

    const shards = Array.from({ length: 130 }, () => new Shard());

    // Hide outgoing, show incoming immediately (shards cover the gap)
    fromEl.style.opacity = '0';
    toEl.classList.add('active');
    gsap.set(toEl, { opacity: 1 });
    setTimeout(onContentReady, 60);

    let rafId;
    (function loop() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let anyAlive = false;
      for (const s of shards) {
        s.update(); s.draw();
        if (!s.isDead) anyAlive = true;
      }
      if (anyAlive) {
        rafId = requestAnimationFrame(loop);
      } else {
        fromEl.classList.remove('active');
        gsap.set(fromEl, { clearProps: 'opacity' });
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        onComplete();
      }
    }());
  });

  return { register, run };
})();
