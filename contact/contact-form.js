(function () {
  var form = document.getElementById("contact-form");
  var status = document.getElementById("contact-form-status");
  if (!form || !status) return;

  var params = new URLSearchParams(window.location.search);
  if (params.get("sent") === "1") {
    showStatus("success", "Thanks — we received your message and will reply within 24 hours.");
    window.history.replaceState({}, "", window.location.pathname);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var submitBtn = form.querySelector(".contact-form-submit");
    var defaultLabel = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";
    status.hidden = true;

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    })
      .then(function (response) {
        if (response.ok) {
          form.reset();
          showStatus("success", "Thanks — we received your message and will reply within 24 hours.");
          return;
        }
        return response.json().then(function (data) {
          throw new Error(data.error || "Could not send your message. Please try again.");
        });
      })
      .catch(function (error) {
        showStatus(
          "error",
          error.message || "Could not send your message. Email hello@stackcone.com directly."
        );
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = defaultLabel;
      });
  });

  function showStatus(type, message) {
    status.hidden = false;
    status.className = "contact-form-status contact-form-status--" + type;
    status.textContent = message;
    status.setAttribute("role", "alert");
    status.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
})();
