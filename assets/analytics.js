(function () {
  var GA_MEASUREMENT_ID = "G-B29M3GX6QM";
  if (!GA_MEASUREMENT_ID) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", GA_MEASUREMENT_ID, {
    anonymize_ip: true,
    send_page_view: true
  });

  // Track CTA clicks to contact page and primary actions
  function trackCTAClick(element) {
    var href = element.getAttribute("href");
    var text = element.textContent.trim();
    var isContact = href && (href.includes("/contact") || href.startsWith("mailto:") || href.startsWith("tel:"));
    
    if (isContact || element.classList.contains("cta--primary")) {
      gtag("event", "cta_click", {
        event_category: "Engagement",
        event_label: text,
        link_url: href,
        link_text: text
      });
    }
  }

  // Attach click tracking to CTA links
  document.addEventListener("DOMContentLoaded", function () {
    var ctaLinks = document.querySelectorAll('a.cta, a[href*="/contact"], a[href^="mailto:"], a[href^="tel:"]');
    ctaLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        trackCTAClick(link);
      });
    });
  });
})();
