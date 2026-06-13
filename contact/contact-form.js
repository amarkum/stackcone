(function () {
  var form = document.getElementById("contact-form");
  var modal = document.getElementById("contact-modal");
  if (!form || !modal) return;

  var modalTitle = document.getElementById("contact-modal-title");
  var modalDesc = document.getElementById("contact-modal-desc");
  var modalIcon = document.getElementById("contact-modal-icon");
  var closeTriggers = modal.querySelectorAll("[data-contact-modal-close]");
  var lastFocused = null;

  var params = new URLSearchParams(window.location.search);
  if (params.get("sent") === "1") {
    openModal("success", "Message sent", "Thanks — we received your message and will reply within 24 hours.");
    window.history.replaceState({}, "", window.location.pathname);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var submitBtn = form.querySelector(".contact-form-submit");
    var defaultLabel = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    })
      .then(function (response) {
        if (response.ok) {
          form.reset();
          openModal("success", "Message sent", "Thanks — we received your message and will reply within 24 hours.");
          return;
        }
        return response.json().then(function (data) {
          throw new Error(data.error || "Could not send your message. Please try again.");
        });
      })
      .catch(function (error) {
        openModal(
          "error",
          "Could not send",
          error.message || "Something went wrong. Email hello@stackcone.com directly."
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
