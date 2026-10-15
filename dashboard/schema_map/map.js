// Schema map component (st.components.v2). Python sends the schema, links and positions as `data`;
// when a move finishes this sends {positions} back as the "layout" trigger, and Python saves it.
// One map instance per mount point survives Streamlit reruns, so a rerun never interrupts a drag.

const SOURCES = {
  history: { label: "Last.fm listening history", color: "var(--history)" },
  details: { label: "Last.fm track & artist details", color: "var(--details)" },
  spotify: { label: "Spotify", color: "var(--spotify)" },
  view: { label: "View (a saved query)", color: "var(--iris)" },
};
const NS = "http://www.w3.org/2000/svg";
const instances = new WeakMap();

function el(tag, attrs = {}, text) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
}
function svgEl(tag, attrs) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
}
function swatch(source) {
  const s = el("i", { class: "swatch" + (source === "view" ? " sq" : "") });
  s.style.setProperty("--c", (SOURCES[source] || { color: "var(--unknown)" }).color);
  return s;
}

function createMap(root, setTriggerValue) {
  const state = { data: null, positions: {}, zoom: 1, drag: null, hover: null, topZ: 10, sig: "" };
  const cards = {};

  const wrap = el("div", { class: "schema-map" });
  const bar = el("div", { class: "bar" });
  const tools = el("div", { class: "tools" });
  const zoomBox = el("span", { class: "zoom" });
  const zoomOut = el("button", { type: "button", "aria-label": "Zoom out" }, "−");
  const zoomLevel = el("output", {}, "100%");
  const zoomIn = el("button", { type: "button", "aria-label": "Zoom in" }, "+");
  zoomBox.append(zoomOut, zoomLevel, zoomIn);
  const fitBtn = el("button", { type: "button" }, "Fit to screen");
  const lineageLabel = el("label", { class: "toggle" });
  const lineageBox = el("input", { type: "checkbox" });
  lineageLabel.append(lineageBox, document.createTextNode(" Show how views are built"));
  const resetBtn = el("button", { type: "button" }, "Reset layout");
  const status = el("span", { class: "status", role: "status", "aria-live": "polite" });
  tools.append(zoomBox, fitBtn, lineageLabel, resetBtn, status);
  const legend = el("div", { class: "legend", "aria-label": "Legend" });
  for (const [key, s] of Object.entries(SOURCES)) {
    const item = el("span");
    item.append(swatch(key), document.createTextNode(s.label));
    legend.append(item);
  }
  bar.append(tools, legend);

  const viewport = el("div", { class: "viewport" });
  const stage = el("div", { class: "stage" });
  const canvas = el("div", { class: "canvas" });
  const svg = svgEl("svg", { class: "links", "aria-hidden": "true" });
  canvas.append(svg);
  stage.append(canvas);
  viewport.append(stage);
  wrap.append(bar, viewport);
  root.append(wrap);

  function setStatus(text, bad = false) {
    status.textContent = text;
    status.classList.toggle("bad", bad);
  }
  function size() { return state.data.size; }

  // ---- positions ----
  function clampPos(name, x, y) {
    const c = cards[name], { w, h } = size();
    return {
      x: Math.round(Math.min(Math.max(0, x), w - c.offsetWidth)),
      y: Math.round(Math.min(Math.max(0, y), h - Math.min(c.offsetHeight, h))),
    };
  }
  function place(name) {
    const p = state.positions[name];
    cards[name].style.left = p.x + "px";
    cards[name].style.top = p.y + "px";
  }
  function setPos(name, x, y) {
    state.positions[name] = clampPos(name, x, y);
    place(name);
    drawLinks();
  }
  function applyPositions(positions) {
    for (const name of Object.keys(cards)) {
      const p = positions[name] || state.data.defaults[name];
      state.positions[name] = clampPos(name, p.x, p.y);
      place(name);
    }
    drawLinks();
  }

  let soon = null;
  function send() {
    clearTimeout(soon);
    setStatus("Saving layout…");
    setTriggerValue("layout", { positions: structuredClone(state.positions) });
  }
  function sendSoon() {
    clearTimeout(soon);
    soon = setTimeout(send, 600);
  }

  // ---- cards ----
  function buildCard(o) {
    const card = el("section", { class: "card" + (o.kind === "view" ? " view" : ""), "aria-label": o.title });
    const head = el("div", { class: "card-head", tabindex: "0", role: "button",
      "aria-label": `${o.title}. Drag, or use the arrow keys, to move.` });
    const titleRow = el("div", { class: "title-row" });
    titleRow.append(el("h3", {}, o.title), el("span", { class: "grip", "aria-hidden": "true" }, "⠿⠿"));
    const meta = el("div", { class: "meta-row" });
    meta.append(el("span", { class: "sqlname" }, o.name));
    const chip = el("span", { class: "chip" });
    chip.append(swatch(o.source), document.createTextNode(SOURCES[o.source] ? SOURCES[o.source].label.replace(" (a saved query)", "") : "Source not described"));
    meta.append(chip);
    if (o.rows != null) meta.append(el("span", { class: "count" }, `${o.rows.toLocaleString("en-US")} ${o.rows === 1 ? "row" : "rows"}`));
    head.append(titleRow, meta);

    const desc = el("p", { class: "desc" + (o.description ? "" : " none") }, o.description || "No description yet");
    const list = el("ul", { class: "cols" });
    for (const c of o.columns) {
      const li = el("li", { class: "col", "data-col": c.name });
      const name = el("span", { class: "colname" }, c.name);
      if (c.key) name.append(el("span", { class: "badge key", title: "Part of what identifies each row" }, "ID"));
      if (c.link) name.append(el("span", { class: "badge link", title: "Links to another table" }, "LINK"));
      if (!c.required && !c.key && o.kind === "table") name.append(el("span", { class: "opt" }, "optional"));
      li.append(name, el("span", { class: "type" }, c.type || "any"),
        el("span", { class: "coldesc" + (c.meaning ? "" : " none") }, c.meaning || "No description yet"));
      list.append(li);
    }
    card.append(head, desc, list);
    canvas.append(card);
    cards[o.name] = card;

    head.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      head.setPointerCapture(e.pointerId);
      card.style.zIndex = ++state.topZ;
      card.classList.add("dragging");
      const p = state.positions[o.name];
      state.drag = { name: o.name, sx: e.clientX, sy: e.clientY, ox: p.x, oy: p.y, moved: false };
    });
    head.addEventListener("pointermove", (e) => {
      const d = state.drag;
      if (!d || d.name !== o.name) return;
      const dx = (e.clientX - d.sx) / state.zoom, dy = (e.clientY - d.sy) / state.zoom;
      if (Math.abs(dx) + Math.abs(dy) > 2) d.moved = true;
      setPos(o.name, d.ox + dx, d.oy + dy);
    });
    const end = () => {
      const d = state.drag;
      if (!d || d.name !== o.name) return;
      state.drag = null;
      card.classList.remove("dragging");
      if (d.moved) send();
    };
    head.addEventListener("pointerup", end);
    head.addEventListener("pointercancel", end);
    head.addEventListener("keydown", (e) => {
      const step = e.shiftKey ? 80 : 20;
      const d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
      if (!d) return;
      e.preventDefault();
      const p = state.positions[o.name];
      setPos(o.name, p.x + d[0], p.y + d[1]);
      sendSoon();
    });
    const hover = (on) => () => {
      if (on) state.hover = o.name; else if (state.hover === o.name) state.hover = null;
      drawLinks();
    };
    card.addEventListener("pointerenter", hover(true));
    card.addEventListener("pointerleave", hover(false));
    head.addEventListener("focus", hover(true));
    head.addEventListener("blur", hover(false));
  }

  // ---- links ----
  function anchor(name, col) {
    const c = cards[name], p = state.positions[name];
    let y = p.y + 28;
    if (col) {
      const row = c.querySelector(`[data-col="${CSS.escape(col)}"]`);
      y = p.y + row.offsetTop + Math.min(row.offsetHeight / 2, 15);
    }
    return { l: p.x, r: p.x + c.offsetWidth, y };
  }
  function curve(a, b) {
    let p0, p3, c1, c2, anchorText = "middle";
    if (a.r + 24 <= b.l) {
      const d = Math.max(40, (b.l - a.r) / 2);
      p0 = [a.r, a.y]; p3 = [b.l, b.y]; c1 = [a.r + d, a.y]; c2 = [b.l - d, b.y];
    } else if (b.r + 24 <= a.l) {
      const d = Math.max(40, (a.l - b.r) / 2);
      p0 = [a.l, a.y]; p3 = [b.r, b.y]; c1 = [a.l - d, a.y]; c2 = [b.r + d, b.y];
    } else {
      const x = Math.max(a.r, b.r) + 60;
      p0 = [a.r, a.y]; p3 = [b.r, b.y]; c1 = [x, a.y]; c2 = [x, b.y];
      anchorText = "start";  // the loop bulges right of the cards, so keep its label out there too
    }
    const mid = [(p0[0] + 3 * c1[0] + 3 * c2[0] + p3[0]) / 8, (p0[1] + 3 * c1[1] + 3 * c2[1] + p3[1]) / 8];
    if (anchorText === "start") mid[0] += 4;
    return { d: `M${p0} C${c1} ${c2} ${p3}`, p0, p3, mid, anchorText };
  }
  function drawLinks() {
    svg.replaceChildren();
    for (const c of canvas.querySelectorAll(".col.hot")) c.classList.remove("hot");
    let anyHot = false;
    if (lineageBox.checked) {
      for (const [from, to] of state.data.lineage) {
        const hot = state.hover === from || state.hover === to;
        anyHot ||= hot;
        const g = svgEl("g", { class: "rel lineage" + (hot ? " hot" : "") });
        g.append(svgEl("path", { class: "link lineage", d: curve(anchor(from), anchor(to)).d }));
        svg.append(g);
      }
    }
    for (const r of state.data.links) {
      const hot = state.hover === r.from[0] || state.hover === r.to[0];
      anyHot ||= hot;
      const k = curve(anchor(...r.from), anchor(...r.to));
      const g = svgEl("g", { class: "rel" + (hot ? " hot" : "") });
      g.append(svgEl("path", { class: "link", d: k.d }));
      g.append(svgEl("circle", { class: "end" + (r.label.startsWith("1 ") ? "" : " many"), cx: k.p0[0], cy: k.p0[1], r: 4 }));
      g.append(svgEl("circle", { class: "end", cx: k.p3[0], cy: k.p3[1], r: 4 }));
      const label = svgEl("text", { class: "link-label", x: k.mid[0], y: k.mid[1] - 6, "text-anchor": k.anchorText });
      label.textContent = r.label;
      g.append(label);
      svg.append(g);
      if (hot) {
        cards[r.from[0]].querySelector(`[data-col="${CSS.escape(r.from[1])}"]`).classList.add("hot");
        cards[r.to[0]].querySelector(`[data-col="${CSS.escape(r.to[1])}"]`).classList.add("hot");
      }
    }
    svg.classList.toggle("dim", anyHot);
  }

  // ---- zoom ----
  function setZoom(z) {
    state.zoom = Math.min(1.5, Math.max(0.3, Math.round(z * 100) / 100));
    const { w, h } = size();
    canvas.style.transform = `scale(${state.zoom})`;
    stage.style.width = w * state.zoom + "px";
    stage.style.height = h * state.zoom + "px";
    zoomLevel.textContent = Math.round(state.zoom * 100) + "%";
  }
  function fit() {
    let r = 0, b = 0;
    for (const name of Object.keys(cards)) {
      r = Math.max(r, state.positions[name].x + cards[name].offsetWidth);
      b = Math.max(b, state.positions[name].y + cards[name].offsetHeight);
    }
    setZoom(Math.min((viewport.clientWidth - 4) / (r + 40), (viewport.clientHeight - 4) / (b + 40), 1));
    viewport.scrollTo(0, 0);
  }
  zoomIn.addEventListener("click", () => setZoom(state.zoom + 0.1));
  zoomOut.addEventListener("click", () => setZoom(state.zoom - 0.1));
  fitBtn.addEventListener("click", fit);
  lineageBox.addEventListener("change", drawLinks);

  let armed = null;
  resetBtn.addEventListener("click", () => {
    if (!armed) {
      resetBtn.textContent = "Click again to reset";
      resetBtn.classList.add("warn");
      armed = setTimeout(() => { armed = null; resetBtn.textContent = "Reset layout"; resetBtn.classList.remove("warn"); }, 3000);
      return;
    }
    clearTimeout(armed); armed = null;
    resetBtn.textContent = "Reset layout"; resetBtn.classList.remove("warn");
    applyPositions(state.data.defaults);
    send();
  });

  // ---- data from Python (first mount and every rerun) ----
  function update(data) {
    const sig = JSON.stringify([data.objects, data.links, data.lineage, data.size]);
    const first = !state.data;
    state.data = data;
    if (sig !== state.sig) {
      // The schema changed (or first run): rebuild the cards.
      state.sig = sig;
      for (const name of Object.keys(cards)) { cards[name].remove(); delete cards[name]; }
      canvas.style.width = data.size.w + "px";
      canvas.style.height = data.size.h + "px";
      svg.setAttribute("width", data.size.w);
      svg.setAttribute("height", data.size.h);
      for (const o of data.objects) buildCard(o);
      applyPositions(data.positions);
      if (first) fit(); else setZoom(state.zoom);
    } else if (!state.drag) {
      applyPositions(data.positions);
    }
    if (data.status) setStatus(data.status, data.status.startsWith("Couldn't"));
    else if (first) setStatus("Drag a card's header to move it");
  }

  const onResize = () => state.data && drawLinks();
  window.addEventListener("resize", onResize);
  document.fonts?.ready.then(onResize);

  return { update, wrap, destroy: () => window.removeEventListener("resize", onResize) };
}

export default function (component) {
  const { data, setTriggerValue, parentElement } = component;
  let map = instances.get(parentElement);
  if (!map || !map.wrap.isConnected) {
    map = createMap(parentElement, setTriggerValue);
    instances.set(parentElement, map);
  }
  map.update(data);
}
