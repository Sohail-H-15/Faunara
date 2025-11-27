const API_BASE = "";

function showResult(elementId, html) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.innerHTML = html;
  el.classList.remove("hidden");
}

function scoreToPercent(score) {
  if (score == null) return "N/A";
  return `${Math.round(score * 100)}%`;
}

// ---- Image classifier ----

const imageForm = document.getElementById("image-form");
if (imageForm) {
  imageForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(imageForm);
    const imageFile = formData.get("image");
    
    showResult(
      "image-result",
      "<h4>Classifying…</h4><p>Please wait while FAUNARA analyzes your image.</p>",
    );

    try {
      const res = await fetch(`${API_BASE}/api/classify-image`, {
        method: "POST",
        body: formData,
      });
      
      // Check if response is JSON
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(`Server returned non-JSON response. Status: ${res.status}. Response: ${text.substring(0, 200)}`);
      }
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Classification failed");
      }

      const animal = data.animal || {};
      const header = "Classification Result";

      // Show modal with image and results
      showClassificationModal(imageFile, animal, data.match_score, header, false);

      // Also show in result panel
      showResult(
        "image-result",
        `<h4>Classification Complete</h4>
         <p><strong>Animal Name:</strong> ${animal.name || "Unknown"}</p>
         <p><strong>Similarity Score:</strong> ${scoreToPercent(data.match_score)}</p>
         <p><strong>Habitat:</strong> ${animal.habitat || "Not available yet"}</p>
         <p><strong>Facts:</strong> ${animal.facts || "No facts stored yet."}</p>`,
      );
    } catch (err) {
      console.error("Error classifying image:", err);
      const errorMsg = err.message || "Something went wrong.";
      
      // Check if it's a "no match" error
      if (errorMsg.includes("No similar animal found")) {
        showResult(
          "image-result",
          `<h4>No Match Found</h4>
           <p>The uploaded image doesn't match any animal in FAUNARA's database.</p>
           <p class="mt-2"><small>💡 <strong>Tip:</strong> Consider adding this animal using the <strong>Improve Faunara</strong> section to help FAUNARA learn!</small></p>`,
        );
      } else {
        showResult(
          "image-result",
          `<h4>Error</h4><p>${errorMsg}</p>`,
        );
      }
    }
  });
}

// ---- Attribute classifier ----

const attrForm = document.getElementById("attributes-form");
const attrSubmit = document.getElementById("attributes-submit");

if (attrForm && attrSubmit) {
  attrSubmit.addEventListener("click", async () => {
    const formData = new FormData(attrForm);
    const attrs = {};
    for (const [key, value] of formData.entries()) {
      if (value !== "") {
        attrs[key] = value;
      }
    }

    if (Object.keys(attrs).length === 0) {
      showResult(
        "attributes-result",
        "<h4>Missing attributes</h4><p>Please fill at least one attribute.</p>",
      );
      return;
    }

    showResult(
      "attributes-result",
      "<h4>Guessing…</h4><p>FAUNARA is comparing your attributes to its knowledge.</p>",
    );

    try {
      const res = await fetch(`${API_BASE}/api/classify-attributes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ attributes: attrs }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Attribute classification failed");
      }

      const animal = data.animal || {};

      showResult(
        "attributes-result",
        `<h4>Closest match</h4>
         <p><strong>Name:</strong> ${animal.name || "Unknown"}</p>
         <p><strong>Match score:</strong> ${scoreToPercent(data.match_score)}</p>
         <p><strong>Habitat:</strong> ${animal.habitat || "Not available yet"}</p>
         <p><strong>Facts:</strong> ${animal.facts || "No facts stored yet."}</p>`,
      );
    } catch (err) {
      showResult(
        "attributes-result",
        `<h4>Error</h4><p>${err.message || "Something went wrong."}</p>`,
      );
    }
  });
}

// ---- Improve Faunara ----

// Toggle attributes form
const toggleAttributesBtn = document.getElementById("toggle-attributes-btn");
const attributesContainer = document.getElementById("attributes-form-container");
const attributesToggleText = document.getElementById("attributes-toggle-text");

if (toggleAttributesBtn && attributesContainer) {
  toggleAttributesBtn.addEventListener("click", () => {
    const isHidden = attributesContainer.classList.contains("hidden");
    const arrowSpan = toggleAttributesBtn.querySelector("span:last-child");
    
    if (isHidden) {
      attributesContainer.classList.remove("hidden");
      if (attributesToggleText) attributesToggleText.textContent = "Hide attributes";
      if (arrowSpan) arrowSpan.textContent = "▲";
    } else {
      attributesContainer.classList.add("hidden");
      if (attributesToggleText) attributesToggleText.textContent = "Click to select attributes";
      if (arrowSpan) arrowSpan.textContent = "▼";
    }
  });
}

// Collect attributes from form
function collectImproveAttributes() {
  const attrs = {};
  const legs = document.getElementById("improve-legs");
  const skin = document.getElementById("improve-skin");
  const diet = document.getElementById("improve-diet");
  const canFly = document.getElementById("improve-can_fly");
  const canSwim = document.getElementById("improve-can_swim");
  const activity = document.getElementById("improve-activity");

  if (legs && legs.value !== "") attrs.legs = parseInt(legs.value);
  if (skin && skin.value !== "") attrs.skin = skin.value;
  if (diet && diet.value !== "") attrs.diet = diet.value;
  if (canFly && canFly.value !== "") attrs.can_fly = canFly.value;
  if (canSwim && canSwim.value !== "") attrs.can_swim = canSwim.value;
  if (activity && activity.value !== "") attrs.activity = activity.value;

  return attrs;
}

const improveForm = document.getElementById("improve-form");
if (improveForm) {
  improveForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(improveForm);

    // Collect attributes from the form and add as JSON
    const attrs = collectImproveAttributes();
    const attrsJson = JSON.stringify(attrs);
    formData.set("attributes", attrsJson);
    
    // Debug: log what we're sending
    console.log("Submitting animal:", {
      name: formData.get("name"),
      attributes: attrsJson,
      hasImage: formData.get("image") ? "yes" : "no"
    });

    showResult(
      "improve-result",
      "<h4>Saving…</h4><p>Adding your species to FAUNARA's knowledge base.</p>",
    );

    try {
      const res = await fetch(`${API_BASE}/api/improve-faunara`, {
        method: "POST",
        body: formData,
      });
      
      // Check if response is JSON
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(`Server returned non-JSON response. Status: ${res.status}. Response: ${text.substring(0, 200)}`);
      }
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to save animal");
      }

      // Get form data for display
      const name = formData.get("name");
      const habitat = formData.get("habitat") || "Not specified";
      const facts = formData.get("facts") || "No facts provided";
      const imageFile = formData.get("image");
      const attrs = collectImproveAttributes();

      // Show modal with image and info
      showSuccessModal(name, habitat, facts, attrs, imageFile, data.id);

      improveForm.reset();
      // Reset attributes form visibility
      if (attributesContainer) {
        attributesContainer.classList.add("hidden");
        if (attributesToggleText) attributesToggleText.textContent = "Click to select attributes";
        if (toggleAttributesBtn) {
          const arrowSpan = toggleAttributesBtn.querySelector("span:last-child");
          if (arrowSpan) arrowSpan.textContent = "▼";
        }
      }
    } catch (err) {
      console.error("Error adding animal:", err);
      showResult(
        "improve-result",
        `<h4>Error</h4><p>${err.message || "Something went wrong."}</p>`,
      );
    }
  });
}

// Modal functions
function showSuccessModal(name, habitat, facts, attrs, imageFile, animalId) {
  const modal = document.getElementById("success-modal");
  const modalBody = document.getElementById("modal-body");
  
  if (!modal || !modalBody) return;

  // Build attributes string
  let attrsText = "None";
  if (Object.keys(attrs).length > 0) {
    attrsText = Object.entries(attrs)
      .map(([key, value]) => `${key}: ${value}`)
      .join(", ");
  }

  // Create image preview if file was uploaded
  let imageHtml = "";
  if (imageFile && imageFile.size > 0) {
    const imageUrl = URL.createObjectURL(imageFile);
    imageHtml = `<img src="${imageUrl}" alt="${name}" class="modal-image" />`;
  } else {
    imageHtml = `<div class="modal-image bg-emerald-900/30 border-2 border-dashed border-emerald-400/50 flex items-center justify-center text-emerald-300/60 text-sm" style="min-height: 200px;">No image uploaded</div>`;
  }

  modalBody.innerHTML = `
    ${imageHtml}
    <div class="modal-info">
      <p><strong>Name:</strong> ${name}</p>
      <p><strong>ID:</strong> ${animalId}</p>
      <p><strong>Habitat:</strong> ${habitat}</p>
      <p><strong>Facts:</strong> ${facts}</p>
      <p><strong>Attributes:</strong> ${attrsText}</p>
    </div>
  `;

  modal.classList.remove("hidden");
}

// Close modal handlers
const closeModalBtn = document.getElementById("close-modal");
const successModal = document.getElementById("success-modal");

if (closeModalBtn && successModal) {
  closeModalBtn.addEventListener("click", () => {
    successModal.classList.add("hidden");
  });

  // Close on overlay click
  const overlay = successModal.querySelector(".modal-overlay");
  if (overlay) {
    overlay.addEventListener("click", () => {
      successModal.classList.add("hidden");
    });
  }

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !successModal.classList.contains("hidden")) {
      successModal.classList.add("hidden");
    }
  });
}

// Image Classification Modal
function showClassificationModal(imageFile, animal, matchScore, header, offerSave) {
  const modal = document.getElementById("classification-modal");
  const modalBody = document.getElementById("classification-modal-body");
  const modalTitle = document.getElementById("classification-modal-title");
  
  if (!modal || !modalBody || !modalTitle) return;

  modalTitle.textContent = "Animal Classification Result";

  // Create image preview
  let imageHtml = "";
  if (imageFile && imageFile.size > 0) {
    const imageUrl = URL.createObjectURL(imageFile);
    imageHtml = `<img src="${imageUrl}" alt="${animal.name || 'Animal'}" class="modal-image" />`;
  } else {
    imageHtml = `<div class="modal-image bg-emerald-900/30 border-2 border-dashed border-emerald-400/50 flex items-center justify-center text-emerald-300/60 text-sm" style="min-height: 200px;">No image available</div>`;
  }

  // Build attributes string if available
  let attrsText = "Not specified";
  if (animal.attributes && Object.keys(animal.attributes).length > 0) {
    attrsText = Object.entries(animal.attributes)
      .map(([key, value]) => `${key}: ${value}`)
      .join(", ");
  }

  const saveHint = offerSave === true
    ? `<div class="mt-3 p-2 rounded bg-amber-900/30 border border-amber-400/50 text-amber-100 text-xs">
         <strong>💡 Tip:</strong> You can add this animal permanently from the <strong>Improve Faunara</strong> panel.
       </div>`
    : "";

  modalBody.innerHTML = `
    ${imageHtml}
    <div class="modal-info">
      <p><strong>Animal Name:</strong> ${animal.name || "Unknown"}</p>
      <p><strong>Similarity Score:</strong> ${scoreToPercent(matchScore)}</p>
      <p><strong>Habitat:</strong> ${animal.habitat || "Not available yet"}</p>
      <p><strong>Facts:</strong> ${animal.facts || "No facts stored yet."}</p>
      <p><strong>Attributes:</strong> ${attrsText}</p>
      ${saveHint}
    </div>
  `;

  modal.classList.remove("hidden");
}

// Close classification modal handlers
const closeClassificationModalBtn = document.getElementById("close-classification-modal");
const classificationModal = document.getElementById("classification-modal");

if (closeClassificationModalBtn && classificationModal) {
  closeClassificationModalBtn.addEventListener("click", () => {
    classificationModal.classList.add("hidden");
  });

  // Close on overlay click
  const overlay = classificationModal.querySelector(".modal-overlay");
  if (overlay) {
    overlay.addEventListener("click", () => {
      classificationModal.classList.add("hidden");
    });
  }

  // Close on Escape key (update existing handler)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (!successModal.classList.contains("hidden")) {
        successModal.classList.add("hidden");
      }
      if (!classificationModal.classList.contains("hidden")) {
        classificationModal.classList.add("hidden");
      }
    }
  });
}


