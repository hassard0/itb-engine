async function postJSON(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

document.getElementById("check-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const constraints = fd.getAll("c");
  const coefficients = {
    g_4: parseFloat(fd.get("g_4")),
    g_6: parseFloat(fd.get("g_6")),
  };
  const gR2Raw = fd.get("g_R2");
  if (gR2Raw !== null && gR2Raw !== "") {
    coefficients.g_R2 = parseFloat(gR2Raw);
  }
  const out = document.getElementById("check-result");
  try {
    const data = await postJSON("/check", { coefficients, constraints });
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

const ALL_CONSTRAINTS = [
  "scalar_positivity_g4",
  "scalar_positivity_g6",
  "scalar_convexity_g6_vs_g4",
  "graviton_mixed_positivity",
  "bekenstein_tight",
  "eft_validity_box",
];

document.getElementById("adversarial-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    initial_guess: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
    },
    constraints: ALL_CONSTRAINTS,
  };
  const out = document.getElementById("adversarial-result");
  try {
    const data = await postJSON("/adversarial", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("path-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    start: { g_4: parseFloat(fd.get("sx")), g_6: parseFloat(fd.get("sy")) },
    end: { g_4: parseFloat(fd.get("ex")), g_6: parseFloat(fd.get("ey")) },
    x_param: "g_4", x_range: [-1, 1], x_steps: 31,
    y_param: "g_6", y_range: [-1, 1], y_steps: 31,
    constraints: ALL_CONSTRAINTS,
  };
  const out = document.getElementById("path-result");
  try {
    const data = await postJSON("/path", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("sensitivity-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    coefficients: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
      g_R2: parseFloat(fd.get("g_R2")),
    },
    constraints: ALL_CONSTRAINTS,
    sigma: parseFloat(fd.get("sigma")),
    n_samples: parseInt(fd.get("n_samples"), 10),
  };
  const out = document.getElementById("sensitivity-result");
  try {
    const data = await postJSON("/sensitivity/probability", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("duality-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    constraints: ALL_CONSTRAINTS,
    x_param: "g_4", x_range: [0, 2], x_steps: 21,
    y_param: "g_6", y_range: [0, 2], y_steps: 21,
    fixed_coefficients: { g_R2: parseFloat(fd.get("g_R2")) },
  };
  const out = document.getElementById("duality-result");
  try {
    const data = await postJSON("/duality", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("fingerprint-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    frameworks: ["pure_gr", "string_tree_eft"],
    constraints: ALL_CONSTRAINTS,
  };
  const out = document.getElementById("fingerprint-result");
  try {
    const data = await postJSON("/fingerprint", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("voxel-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    x_param: "g_4", x_range: [-1, 1], x_steps: 15,
    y_param: "g_6", y_range: [-1, 1], y_steps: 15,
    z_param: "g_R2", z_range: [0, 1], z_steps: 9,
    constraints: ALL_CONSTRAINTS,
    slice_axis: "g_R2",
    slice_value: parseFloat(fd.get("g_R2")),
  };
  const out = document.getElementById("voxel-result");
  try {
    const data = await postJSON("/voxel", body);
    const summary = {
      shape: data.shape,
      total_feasible_voxels: data.total_feasible_voxels,
      slice_axis: data.slice && data.slice.fixed_axis,
      slice_value: data.slice && data.slice.fixed_value,
      slice_feasible_count: data.slice
        ? data.slice.feasibility_grid.flat().filter(Boolean).length
        : 0,
    };
    out.textContent = JSON.stringify(summary, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("phases-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    x_param: "g_4", x_range: [-1, 1], x_steps: 31,
    y_param: "g_6", y_range: [-1, 1], y_steps: 31,
    constraints: ALL_CONSTRAINTS,
  };
  const out = document.getElementById("phases-result");
  try {
    const data = await postJSON("/phases", body);
    out.textContent = JSON.stringify({
      n_components: data.n_components,
      component_sizes: data.component_sizes,
    }, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("completeness-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    constraints: ALL_CONSTRAINTS,
    params: ["g_4", "g_6"],
    starting_box: 2.0,
    max_box: 8.0,
    steps_per_axis: 11,
  };
  const out = document.getElementById("completeness-result");
  try {
    const data = await postJSON("/completeness", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("sweep-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    x_param: fd.get("x_param"),
    x_range: [parseFloat(fd.get("x_min")), parseFloat(fd.get("x_max"))],
    x_steps: parseInt(fd.get("x_steps"), 10),
    y_param: fd.get("y_param"),
    y_range: [parseFloat(fd.get("y_min")), parseFloat(fd.get("y_max"))],
    y_steps: parseInt(fd.get("y_steps"), 10),
    constraints: ALL_CONSTRAINTS,
    color_by: fd.get("color_by"),
    overlay_frameworks: fd.getAll("fw"),
  };
  try {
    const data = await postJSON("/sweep", body);
    Plotly.newPlot("sweep-plot", data.figure.data, data.figure.layout, { responsive: true });
  } catch (err) { document.getElementById("sweep-plot").textContent = String(err); }
});

document.getElementById("fragility-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    x_param: "g_4",
    x_range: [-1, 1],
    x_steps: parseInt(fd.get("x_steps"), 10),
    y_param: "g_6",
    y_range: [-1, 1],
    y_steps: parseInt(fd.get("y_steps"), 10),
    constraints: ALL_CONSTRAINTS,
  };
  try {
    const data = await postJSON("/fragility", body);
    Plotly.newPlot("fragility-plot", data.figure.data, data.figure.layout, { responsive: true });
  } catch (err) { document.getElementById("fragility-plot").textContent = String(err); }
});

document.getElementById("importance-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    x_param: "g_4",
    x_range: [-1, 1],
    x_steps: parseInt(fd.get("x_steps"), 10),
    y_param: "g_6",
    y_range: [-1, 1],
    y_steps: parseInt(fd.get("y_steps"), 10),
    constraints: ALL_CONSTRAINTS,
  };
  const out = document.getElementById("importance-result");
  try {
    const data = await postJSON("/importance", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("perturb-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    coefficients: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
    },
    constraints: ["scalar_positivity_g4", "scalar_positivity_g6"],
  };
  const out = document.getElementById("perturb-result");
  try {
    const data = await postJSON("/perturbation", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("fisher-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    coefficients: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
    },
    params: ["g_4", "g_6"],
    s_values: fd.get("s_values").split(",").map((s) => parseFloat(s.trim())),
    sigma: parseFloat(fd.get("sigma")),
  };
  const out = document.getElementById("fisher-result");
  try {
    const data = await postJSON("/fisher", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});
