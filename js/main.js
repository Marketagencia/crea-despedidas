/* ============================================================================
   Crea Despedidas — microinteracciones (JavaScript nativo, sin dependencias)
   Módulos:
     - prefersReducedMotion / finePointer helpers
     - initYear .............. año dinámico en el footer
     - initNavScroll ......... nav glass al hacer scroll
     - initReveal ............ scroll-reveal con IntersectionObserver
     - initCounters .......... contadores animados del hero
     - initMagnetic .......... botones magnéticos (siguen al cursor)
     - initSpotlight ......... spotlight de las celdas Bento
     - initFastPlanner ....... configurador rápido + CTA WhatsApp
     - initNewsletter ........ validación y feedback del formulario
   ========================================================================== */
(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(pointer: fine)').matches;
  const WHATSAPP = '34644687001';

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  /* ------------------------------------------------------------- año footer */
  function initYear() {
    const el = $('#year');
    if (el) el.textContent = new Date().getFullYear();
  }

  /* --------------------------------------------------------- nav on scroll */
  function initNavScroll() {
    const nav = $('#nav');
    if (!nav) return;
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------------ reveal */
  function initReveal() {
    const items = $$('.reveal');
    if (!items.length) return;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      items.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const show = (el) => el.classList.add('is-visible');

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry, i) => {
          if (!entry.isIntersecting) return;
          // pequeño stagger según posición en el viewport
          setTimeout(() => show(entry.target), i * 70);
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -6% 0px' }
    );
    items.forEach((el) => io.observe(el));

    // Revela de inmediato lo que ya está en pantalla (por si el observer tarda)
    requestAnimationFrame(() => {
      items.forEach((el) => {
        if (el.getBoundingClientRect().top < window.innerHeight * 0.92) {
          show(el);
          io.unobserve(el);
        }
      });
    });

    // Failsafe: nada debe quedarse invisible pase lo que pase
    setTimeout(() => items.forEach(show), 3000);
  }

  /* ---------------------------------------------------------- counters */
  function initCounters() {
    const counters = $$('.counter');
    if (!counters.length) return;

    const group = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const run = (el) => {
      const target = parseFloat(el.dataset.to || '0');
      const suffix = el.dataset.suffix || '';
      if (prefersReducedMotion) {
        el.textContent = group(target) + suffix;
        return;
      }
      const duration = 1400;
      const start = performance.now();
      const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
        el.textContent = group(Math.round(target * eased)) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    if (!('IntersectionObserver' in window)) {
      counters.forEach(run);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          run(entry.target);
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.6 }
    );
    counters.forEach((el) => io.observe(el));
  }

  /* --------------------------------------------------------- magnetic */
  function initMagnetic() {
    if (!finePointer || prefersReducedMotion) return;
    const STRENGTH = 0.3;

    $$('[data-magnetic]').forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        el.style.transform = `translate(${x * STRENGTH}px, ${y * STRENGTH}px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = 'translate(0, 0)';
      });
    });
  }

  /* -------------------------------------------------------- spotlight */
  function initSpotlight() {
    if (!finePointer) return;
    $$('[data-spotlight]').forEach((tile) => {
      tile.addEventListener('mousemove', (e) => {
        const r = tile.getBoundingClientRect();
        tile.style.setProperty('--x', `${e.clientX - r.left}px`);
        tile.style.setProperty('--y', `${e.clientY - r.top}px`);
      });
    });
  }

  /* ------------------------------------------------------ fast planner */
  function initFastPlanner() {
    const form = $('#fast-planner');
    if (!form) return;

    const peopleInput = $('#people', form);
    const peopleOut = $('#people-out', form);
    const summaryTitle = $('#summary-title', form);
    const summaryDetail = $('#summary-detail', form);
    const summaryList = $('#summary-list', form);
    const totalOut = $('#total-out', form);
    const perPersonOut = $('#per-person-out', form);
    const cta = $('#planner-cta', form);
    const segButtons = $$('.seg-btn', form);
    const panes = $$('.planner-pane', form);

    let mode = 'packs'; // 'packs' | 'carta'

    // Formato de miles "1.234" (con respaldo manual si el motor no agrupa)
    const nf = {
      format(n) {
        return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
      },
    };

    const setRangeFill = (input) => {
      const pct = ((input.value - input.min) / (input.max - input.min)) * 100;
      input.style.setProperty('--pct', pct + '%');
    };

    // Lee la selección actual según el modo activo
    function readSelection() {
      const people = parseInt(peopleInput.value, 10);

      if (mode === 'packs') {
        const r = form.querySelector('input[name="pack"]:checked');
        if (!r) {
          return { people, perPerson: 0, items: [], kind: 'packs', title: 'Elige tu pack', detail: 'Selecciona uno de los packs para ver la estimación.' };
        }
        const price = parseFloat(r.dataset.price) || 0;
        return {
          people,
          perPerson: price,
          items: [{ label: r.value, price }],
          kind: 'pack',
          title: r.value,
          detail: r.dataset.desc || '',
        };
      }

      // A la carta
      const checks = $$('input[name="item"]:checked', form);
      const items = checks.map((c) => ({
        label: c.value,
        price: parseFloat(c.dataset.price) || 0,
        cat: c.dataset.cat || '',
      }));
      const perPerson = items.reduce((sum, i) => sum + i.price, 0);
      return {
        people,
        perPerson,
        items,
        kind: 'carta',
        title: items.length
          ? `${items.length} ${items.length === 1 ? 'servicio' : 'servicios'} a la carta`
          : 'Plan a la carta',
        detail: items.length
          ? 'Combinamos exactamente lo que elijas, sin pagar de más.'
          : 'Marca las actividades y servicios que quieras añadir.',
      };
    }

    const animateTotal = (() => {
      let frame;
      let safety;
      let current = parseInt(totalOut.textContent.replace(/\D/g, ''), 10) || 0;
      return (value) => {
        cancelAnimationFrame(frame);
        clearTimeout(safety);
        const from = current;
        current = value;
        if (prefersReducedMotion || from === value) {
          totalOut.textContent = nf.format(value);
          return;
        }
        const start = performance.now();
        const step = (now) => {
          const p = Math.min((now - start) / 500, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          totalOut.textContent = nf.format(Math.round(from + (value - from) * eased));
          if (p < 1) frame = requestAnimationFrame(step);
          else totalOut.textContent = nf.format(value);
        };
        frame = requestAnimationFrame(step);
        // Respaldo si rAF está pausado (pestaña en segundo plano)
        safety = setTimeout(() => { totalOut.textContent = nf.format(value); }, 650);
      };
    })();

    function update() {
      const sel = readSelection();
      const eventType = (form.querySelector('input[name="event"]:checked') || {}).value || 'despedida';
      const total = sel.people * sel.perPerson;

      peopleOut.textContent = sel.people >= 40 ? '40+' : sel.people;
      setRangeFill(peopleInput);

      summaryTitle.textContent = sel.title;
      summaryDetail.textContent = sel.detail;
      perPersonOut.textContent = sel.perPerson ? nf.format(sel.perPerson) : '—';

      // Desglose de items (solo en modo a la carta)
      summaryList.innerHTML = '';
      if (sel.kind === 'carta' && sel.items.length) {
        sel.items.forEach((i) => {
          const li = document.createElement('li');
          const name = document.createElement('span');
          name.textContent = i.label;
          const price = document.createElement('span');
          price.textContent = nf.format(i.price) + ' €';
          li.append(name, price);
          summaryList.appendChild(li);
        });
      }

      animateTotal(total);

      // Mensaje de WhatsApp con el detalle real de la configuración
      let body;
      if (sel.kind === 'pack') {
        body = `Me interesa el ${sel.title} (${nf.format(sel.perPerson)} €/persona aprox.).`;
      } else if (sel.items.length) {
        body = `Quiero montarlo a la carta con: ${sel.items.map((i) => i.label).join(', ')}.`;
      } else {
        body = 'Quiero que me asesoréis para montar el plan.';
      }
      const msg =
        `¡Hola Crea Despedidas! Somos ${sel.people} personas para una ${eventType}. ` +
        body +
        (total ? ` Estimación aproximada: ${nf.format(total)} € en total.` : '') +
        ' ¿Me pasáis propuesta?';
      cta.href = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(msg)}`;
    }

    // Cambio de modo pack / a la carta
    segButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        mode = btn.dataset.mode;
        segButtons.forEach((b) => {
          const on = b === btn;
          b.classList.toggle('is-active', on);
          b.setAttribute('aria-selected', String(on));
        });
        panes.forEach((p) => p.classList.toggle('is-hidden', p.dataset.pane !== mode));
        update();
      });
    });

    form.addEventListener('input', update);
    form.addEventListener('change', update);
    update();
  }

  /* -------------------------------------------------------- newsletter */
  function initNewsletter() {
    const form = $('#newsletter');
    if (!form) return;
    const input = $('input[name="email"]', form);
    const msg = $('#newsletter-msg', form);
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const value = input.value.trim();
      if (!re.test(value)) {
        msg.textContent = 'Introduce un correo válido, porfa.';
        msg.classList.add('is-error');
        input.focus();
        return;
      }
      // Demo sin backend: feedback optimista.
      msg.classList.remove('is-error');
      msg.textContent = '¡Hecho! Revisa tu bandeja para confirmar la suscripción.';
      form.reset();
    });
  }

  /* ------------------------------------ pez tras el cursor / nadando solo */
  function initFishCursor() {
    const fish = document.getElementById('fish-cursor');
    if (!fish || prefersReducedMotion) return;

    // Sin ratón preciso (móvil/tablet) o pantalla estrecha -> el pez nada solo.
    let roam =
      !window.matchMedia('(pointer: fine)').matches ||
      window.innerWidth < 760;

    let tx = window.innerWidth * 0.5;
    let ty = window.innerHeight * 0.5;
    let x = tx;
    let y = ty;
    let vx = 0; // velocidad suavizada
    let vy = 0;
    let dir = 1; // 1 mira a la derecha, -1 a la izquierda
    let t = 0;
    let started = false;
    let nextBubble = 0;
    let ux = -1; // vector unitario pez -> ratón (para mantener la separación)
    let uy = 0;
    const GAP = 38; // ~1 cm: el pez nunca se acerca más que esto al cursor

    // Elige un nuevo destino aleatorio dentro de la pantalla (modo "nada solo"),
    // procurando que el trayecto sea largo para que se vea como un glide suave.
    function newRoamTarget() {
      const m = 56;
      const minLeg = Math.min(260, window.innerHeight * 0.45);
      for (let i = 0; i < 8; i++) {
        const nx = m + Math.random() * Math.max(1, window.innerWidth - 2 * m);
        const ny = m + Math.random() * Math.max(1, window.innerHeight - 2 * m);
        if (Math.hypot(nx - x, ny - y) > minLeg) {
          tx = nx;
          ty = ny;
          return;
        }
      }
      tx = m + Math.random() * Math.max(1, window.innerWidth - 2 * m);
      ty = m + Math.random() * Math.max(1, window.innerHeight - 2 * m);
    }

    function enterRoam() {
      roam = true;
      started = true;
      fish.classList.add('is-active');
      newRoamTarget();
    }

    let sawMouse = false;

    // Un ratón de verdad (no un toque) manda: el pez pasa a seguir el cursor.
    window.addEventListener(
      'pointermove',
      (e) => {
        if (e.pointerType === 'touch') return;
        sawMouse = true;
        roam = false;
        tx = e.clientX;
        ty = e.clientY;
        if (!started) {
          started = true;
          x = tx;
          y = ty;
        }
        fish.classList.add('is-active');
      },
      { passive: true }
    );
    document.addEventListener('pointerout', (e) => {
      if (!roam && !e.relatedTarget) fish.classList.remove('is-active');
    });

    if (roam) {
      enterRoam();
    } else {
      // Sin movimiento de ratón pronto (táctil, emulación...) -> a nadar solo.
      setTimeout(() => {
        if (!sawMouse) enterRoam();
      }, 2500);
    }

    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

    // Suelta una burbuja desde la boca del pez
    function spawnBubble(px, py) {
      const b = document.createElement('div');
      b.className = 'bubble';
      const sz = 5 + Math.random() * 9;
      b.style.setProperty('--sz', sz.toFixed(1) + 'px');
      b.style.setProperty('--sx', px.toFixed(1) + 'px');
      b.style.setProperty('--sy', py.toFixed(1) + 'px');
      b.style.setProperty('--dx', ((Math.random() * 2 - 1) * 24).toFixed(1) + 'px');
      b.style.setProperty('--rise', (55 + Math.random() * 110).toFixed(0) + 'px');
      b.style.setProperty('--dur', (1.1 + Math.random() * 1.3).toFixed(2) + 's');
      document.body.appendChild(b);
      const kill = () => b.remove();
      b.addEventListener('animationend', kill);
      setTimeout(kill, 2800);
    }

    function loop(now) {
      t += 0.12;

      let gx, gy;
      if (roam) {
        // Nada hacia un punto aleatorio; al llegar, elige otro
        gx = tx;
        gy = ty;
        if (Math.hypot(tx - x, ty - y) < 44) newRoamTarget();
      } else {
        // Mantén la unidad pez -> ratón mientras haya separación real
        const cdx = tx - x;
        const cdy = ty - y;
        const cdist = Math.hypot(cdx, cdy);
        if (cdist > 6) {
          ux = cdx / cdist;
          uy = cdy / cdist;
        }
        // Objetivo: un punto a ~1 cm por detrás del ratón, para no taparlo
        gx = tx - ux * GAP;
        gy = ty - uy * GAP;
      }

      const dx = gx - x;
      const dy = gy - y;

      // Nada hacia ese punto con retardo -> queda por detrás (estela)
      const ease = roam ? 0.045 : 0.09; // más suave nadando solo
      x += dx * ease;
      y += dy * ease;

      // Velocidad suavizada para orientar el cuerpo
      vx += (dx - vx) * 0.12;
      vy += (dy - vy) * 0.12;

      // Mira hacia donde nada; si casi no se mueve, conserva el último sentido
      if (vx > 0.4) dir = 1;
      else if (vx < -0.4) dir = -1;

      // Inclinación del morro segun el componente vertical (limitada -> nunca boca abajo)
      const tilt = clamp((Math.atan2(vy, Math.abs(vx) + 8) * 180) / Math.PI, -34, 34);
      const wag = Math.sin(t) * 4; // coleteo
      const pulse = 1 + Math.sin(t * 2) * 0.025;

      // Desplaza el pez hacia la cola de la trayectoria SOLO cuando se mueve
      // (en reposo el offset es 0, así se respeta el gap de ~1 cm con el cursor)
      const speed = Math.hypot(vx, vy);
      const trail = Math.min(speed * 1.6, 22);
      const nvx = speed > 0.01 ? vx / speed : 0;
      const nvy = speed > 0.01 ? vy / speed : 0;
      const bx = x - nvx * trail;
      const by = y - nvy * trail;

      // rotate primero y scaleX despues => el morro siempre lidera y el pez
      // queda siempre con la panza hacia abajo, mire donde mire.
      fish.style.transform =
        `translate(${bx}px, ${by}px) translate(-50%, -50%) ` +
        `rotate(${tilt + wag}deg) scaleX(${dir}) scale(${pulse})`;

      // Burbujas saliendo por la boca (parte delantera del pez)
      if (started && fish.classList.contains('is-active') && now >= nextBubble) {
        spawnBubble(bx + dir * 26, by + 5);
        if (Math.random() < 0.3) {
          spawnBubble(bx + dir * (18 + Math.random() * 12), by + 1);
        }
        nextBubble = now + (speed > 6 ? 90 : 200) + Math.random() * 160;
      }

      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  /* ------------------------------------------ tira de fotos de actividades */
  function initPhotoStrip() {
    const strip = document.querySelector('[data-photo-strip]');
    if (!strip) return;

    const PICS = [
      ['velero', 'Grupo de fiesta en un barco velero al atardecer'],
      ['motos-agua', 'Moto de agua en la costa de Valencia'],
      ['banana-boat', 'Grupo en banana boat'],
      ['paddle-surf', 'Grupo haciendo paddle surf al atardecer'],
      ['mega-big-paddle', 'Grupo en una tabla de paddle gigante'],
      ['humor-amarillo', 'Humor amarillo con trajes de sumo hinchables'],
      ['persona-al-agua', 'Grupo en una actividad acuática de equipo'],
    ];

    // Barajado Fisher–Yates (orden aleatorio en cada carga)
    const list = PICS.slice();
    for (let i = list.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      [list[i], list[j]] = [list[j], list[i]];
    }

    const REPEAT = 3; // repetir la secuencia para llenar pantallas anchas
    const buildTrack = (decorative) => {
      let out = '';
      for (let r = 0; r < REPEAT; r++) {
        for (const [name, alt] of list) {
          out +=
            '<img class="strip-photo" src="/assets/' + name + '.webp" ' +
            (decorative ? 'alt="" aria-hidden="true"' : 'alt="' + alt + '"') +
            ' loading="lazy" onerror="this.src=\'/assets/' + name + '.jpg\'">';
        }
      }
      return out;
    };

    const tracks = strip.querySelectorAll('.marquee-track');
    if (tracks[0]) tracks[0].innerHTML = buildTrack(false);
    if (tracks[1]) tracks[1].innerHTML = buildTrack(true);
  }

  /* -------------------------------------------------------------- init */
  function init() {
    initYear();
    initNavScroll();
    initReveal();
    initCounters();
    initMagnetic();
    initSpotlight();
    initFastPlanner();
    initNewsletter();
    initFishCursor();
    initPhotoStrip();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
