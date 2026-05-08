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
