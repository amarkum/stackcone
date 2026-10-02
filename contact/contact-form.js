(function () {
  var form = document.getElementById("contact-form");
  var modal = document.getElementById("contact-modal");
  if (!form || !modal) return;

  var modalTitle = document.getElementById("contact-modal-title");
  var modalDesc = document.getElementById("contact-modal-desc");
  var modalIcon = document.getElementById("contact-modal-icon");
  var closeTriggers = modal.querySelectorAll("[data-contact-modal-close]");
  var lastFocused = null;

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var submitBtn = form.querySelector(".contact-form-submit");
    var defaultLabel = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";

    // Google Apps Script web app (scripts/contact-form-apps-script.gs) → hello@stackcone.com.
    // URL-encoded body keeps this a "simple" CORS request (no preflight, which Apps Script can't answer).
    fetch(form.action, {
      method: "POST",
      body: new URLSearchParams(new FormData(form))
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.ok) {
          form.reset();
          
          // Fire GA4 event for successful form submission
          if (typeof gtag !== 'undefined') {
            gtag('event', 'generate_lead', {
              event_category: 'Contact',
              event_label: 'Contact Form Submission',
              page_location: window.location.href,
              page_path: window.location.pathname,
              form_id: 'contact-form',
              value: 1
            });
          }
          
          openModal("success", "Message sent", "Thanks — we received your message and will reply within 24 hours.");
          return;
        }
        throw new Error(data.error || "Could not send your message. Please try again.");
      })
      .catch(function (error) {
        // Network/parse failures surface as generic TypeError/SyntaxError text — show a friendlier fallback.
        var message = error instanceof TypeError || error instanceof SyntaxError ? "" : error.message;
        openModal(
          "error",
          "Could not send",
          message || "Something went wrong. Email hello@stackcone.com directly."
        );
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = defaultLabel;
      });
  });

  closeTriggers.forEach(function (trigger) {
    trigger.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });

  function openModal(type, title, message) {
    lastFocused = document.activeElement;
    modalTitle.textContent = title;
    modalDesc.textContent = message;
    modalIcon.textContent = type === "success" ? "✓" : "!";
    modalIcon.className = "contact-modal-icon contact-modal-icon--" + type;
    modal.classList.toggle("contact-modal--error", type === "error");
    modal.hidden = false;
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("contact-modal-open");
    var actionBtn = modal.querySelector(".contact-modal-action");
    if (actionBtn) actionBtn.focus();
  }

  function closeModal() {
    modal.hidden = true;
    modal.setAttribute("aria-hidden", "true");
    modal.classList.remove("contact-modal--error");
    document.body.classList.remove("contact-modal-open");
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
  }
})();
