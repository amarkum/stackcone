(function () {
  var form = document.getElementById("contact-form");
  var modal = document.getElementById("contact-modal");
  if (!form || !modal) return;

  var modalTitle = document.getElementById("contact-modal-title");
  var modalDesc = document.getElementById("contact-modal-desc");
  var modalIcon = document.getElementById("contact-modal-icon");
  var closeTriggers = modal.querySelectorAll("[data-contact-modal-close]");
  var lastFocused = null;

  // Attachments — keep in sync with MAX_FILES / MAX_TOTAL_BYTES / ALLOWED_EXT in
  // scripts/contact-form-apps-script.gs (the server re-checks everything).
  var MAX_FILES = 3;
  var MAX_TOTAL_BYTES = 10 * 1024 * 1024;
  var ALLOWED_EXT = /\.(pdf|docx?|pptx?|xlsx?|csv|txt|md|rtf|png|jpe?g|gif|webp|heic|zip)$/i;
  var dropzone = document.getElementById("contact-dropzone");
  var fileInput = document.getElementById("contact-files");
  var fileList = document.getElementById("contact-files-list");
  var fileError = document.getElementById("contact-files-error");
  var files = [];

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", function (event) {
      if (event.target !== fileInput) fileInput.click();
    });
    fileInput.addEventListener("change", function () {
      addFiles(fileInput.files);
      fileInput.value = "";
    });
    ["dragenter", "dragover"].forEach(function (type) {
      dropzone.addEventListener(type, function (event) {
        event.preventDefault();
        dropzone.classList.add("is-dragover");
      });
    });
    ["dragleave", "drop"].forEach(function (type) {
      dropzone.addEventListener(type, function (event) {
        event.preventDefault();
        dropzone.classList.remove("is-dragover");
      });
    });
    dropzone.addEventListener("drop", function (event) {
      if (event.dataTransfer) addFiles(event.dataTransfer.files);
    });
    fileList.addEventListener("click", function (event) {
      var remove = event.target.closest(".contact-file-remove");
      if (!remove) return;
      files.splice(Number(remove.getAttribute("data-index")), 1);
      showFileError("");
      renderFiles();
    });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var submitBtn = form.querySelector(".contact-form-submit");
    var defaultLabel = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";

    // Google Apps Script web app (scripts/contact-form-apps-script.gs) → hello@stackcone.com.
    // URL-encoded body keeps this a "simple" CORS request (no preflight, which Apps Script can't answer).
    // Files go along as base64 inside a JSON field, since Apps Script can't read multipart uploads.
    readAttachments(files)
      .then(function (attachments) {
        var body = new URLSearchParams(new FormData(form));
        if (attachments.length) body.append("attachments", JSON.stringify(attachments));
        return fetch(form.action, { method: "POST", body: body });
      })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.ok) {
          form.reset();
          files = [];
          renderFiles();
          
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

  function addFiles(list) {
    var error = "";
    Array.prototype.forEach.call(list, function (file) {
      var total = files.reduce(function (sum, f) { return sum + f.size; }, 0);
      var duplicate = files.some(function (f) { return f.name === file.name && f.size === file.size; });
      if (duplicate) return;
      if (!ALLOWED_EXT.test(file.name)) {
        error = "“" + file.name + "” isn't a supported file type.";
      } else if (files.length >= MAX_FILES) {
        error = "You can attach up to " + MAX_FILES + " files.";
      } else if (total + file.size > MAX_TOTAL_BYTES) {
        error = "“" + file.name + "” would take the total over 10 MB.";
      } else {
        files.push(file);
      }
    });
    showFileError(error);
    renderFiles();
  }

  function renderFiles() {
    if (!fileList) return;
    fileList.innerHTML = "";
    files.forEach(function (file, index) {
      var item = document.createElement("li");
      item.className = "contact-file";
      var name = document.createElement("span");
      name.className = "contact-file-name";
      name.textContent = file.name;
      var size = document.createElement("span");
      size.className = "contact-file-size";
      size.textContent = formatSize(file.size);
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "contact-file-remove";
      remove.setAttribute("data-index", index);
      remove.setAttribute("aria-label", "Remove " + file.name);
      remove.textContent = "×";
      item.append(name, size, remove);
      fileList.appendChild(item);
    });
    fileList.hidden = files.length === 0;
  }

  function showFileError(message) {
    if (!fileError) return;
    fileError.textContent = message;
    fileError.hidden = !message;
  }

  function formatSize(bytes) {
    if (bytes < 1024 * 1024) return Math.max(1, Math.round(bytes / 1024)) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function readAttachments(list) {
    return Promise.all(list.map(function (file) {
      return new Promise(function (resolve, reject) {
        var reader = new FileReader();
        reader.onload = function () {
          resolve({ name: file.name, type: file.type, data: String(reader.result).split(",")[1] || "" });
        };
        reader.onerror = function () {
          reject(new Error("Could not read “" + file.name + "”. Please try attaching it again."));
        };
        reader.readAsDataURL(file);
      });
    }));
  }

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
