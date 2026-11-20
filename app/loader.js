// Loads the product library, then the editor.
// products/index.js lists the packs; each pack file calls SDG.register(...) with one product.
// Plain script tags are used (not fetch) so the folder also works opened straight from disk.
window.SDG = {
  families: [], groups: {}, list: [], packs: [], failed: [],
  index(i) { this.families = i.families || []; this.groups = i.groups || {}; this.list = i.packs || []; },
  register(pack) { this.packs.push(pack); }
};
(function () {
  const base = document.currentScript.src.replace(/app\/loader\.js.*$/, "");
  const load = src => new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = base + src; s.onload = ok; s.onerror = () => fail(new Error(src));
    document.head.appendChild(s);
  });
  load("products/index.js")
    .then(async () => {
      for (const p of SDG.list) { try { await load("products/" + p); } catch (e) { SDG.failed.push(p); } }
      try { await load("app/logo.js"); } catch (e) {}
      try { await load("app/equipment.js"); } catch (e) {}
      try { await load("app/shapes.js"); } catch (e) {}
      return load("app/app.js");
    })
    .catch(() => { document.getElementById("status").textContent = "Could not load the product library (products/index.js)."; });
})();
