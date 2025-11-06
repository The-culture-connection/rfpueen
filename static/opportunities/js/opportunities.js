(function () {
  const matchesById = new Map();

  // Preload matches from recommendation script tag.
  const matchesScript = document.getElementById("matches-data");
  if (matchesScript) {
    try {
      const parsed = JSON.parse(matchesScript.textContent || "[]");
      parsed.forEach((item) => {
        if (item && item.id) {
          matchesById.set(item.id, item);
        }
      });
    } catch (error) {
      console.error("Unable to parse match data", error);
    }
  }

  // Load match data from table rows (applied/saved pages).
  document.querySelectorAll("[data-match-json]").forEach((row) => {
    try {
      const data = JSON.parse(row.dataset.matchJson || "{}");
      if (data && row.dataset.opportunityId) {
        matchesById.set(row.dataset.opportunityId, data);
      }
    } catch (error) {
      console.warn("Failed to parse data-match-json for row", error);
    }
  });

  const grid = document.getElementById("opportunity-grid");
  if (grid) {
    grid.addEventListener("click", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const action = target.dataset.action;
      if (!action) return;
      handleAction(target, action);
    });
  }

  document.querySelectorAll(".js-apply, .js-remove").forEach((button) => {
    button.addEventListener("click", () => {
      const action = button.dataset.action;
      if (!action) return;
      handleAction(button, action);
    });
  });

  function handleAction(element, action) {
    const container = element.closest("[data-opportunity-id]");
    if (!container) return;
    const opportunityId = container.dataset.opportunityId;
    const match = matchesById.get(opportunityId) || {};

    setLoading(element, true);

    fetch(`/opportunities/${encodeURIComponent(opportunityId)}/action`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        action,
        match,
        url: match.url,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        setLoading(element, false);
        matchesById.set(opportunityId, { ...match, ...data });
        handleSuccess(element, action, data, container);
      })
      .catch((error) => {
        console.error(error);
        setLoading(element, false);
        flashMessage("We could not complete that action. Please try again.", "error");
      });
  }

  function handleSuccess(element, action, data, container) {
    switch (action) {
      case "apply": {
        flashMessage("Marked as applied. Opening application details…", "success");
        if (data.application_url) {
          window.open(data.application_url, "_blank", "noopener");
        }
        injectInstructions(container, data);
        break;
      }
      case "save": {
        element.textContent = "Saved";
        element.classList.add("disabled");
        flashMessage("Saved for later.", "success");
        break;
      }
      case "pass": {
        flashMessage("Removed from your queue.", "info");
        container.classList.add("is-dismissed");
        window.setTimeout(() => container.remove(), 250);
        break;
      }
      default:
        flashMessage("Action completed.", "success");
    }
  }

  function injectInstructions(container, data) {
    if (!data.instructions && !data.application_url) return;

    let summary = container.querySelector(".application-summary");
    if (!summary) {
      summary = document.createElement("section");
      summary.className = "callout";
      summary.classList.add("application-summary");
      container.appendChild(summary);
    }

    const instructions = Array.isArray(data.instructions) ? data.instructions : [];
    summary.innerHTML = `
      <strong>Application pathway</strong>
      <p>Confidence: ${(data.confidence * 100 || 0).toFixed(0)}%</p>
      ${data.application_url ? `<p><a class="btn link" href="${data.application_url}" target="_blank" rel="noopener">Open application</a></p>` : ""}
      ${instructions.length ? `<ol>${instructions.map((step) => `<li>${step}</li>`).join("")}</ol>` : ""}
      ${data.notes ? `<p class="text-muted">${data.notes}</p>` : ""}
    `;
  }

  function setLoading(element, state) {
    if (state) {
      element.dataset.originalText = element.textContent || "";
      element.textContent = "Working…";
      element.setAttribute("disabled", "disabled");
    } else {
      if (element.dataset.originalText) {
        element.textContent = element.dataset.originalText;
      }
      element.removeAttribute("disabled");
    }
  }

  function flashMessage(text, variant = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
      container = document.createElement("div");
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${variant}`;
    toast.textContent = text;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("hide");
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }
})();
