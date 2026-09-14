// Defer AdSense loading until page is idle or user interacts
(function() {
  'use strict';
  
  var loaded = false;
  var adSenseClient = 'ca-pub-4080297219638785';
  
  function loadAdSense() {
    if (loaded) return;
    loaded = true;
    
    var script = document.createElement('script');
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + adSenseClient;
    script.async = true;
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
  }
  
  // Load on idle if supported, otherwise on load
  if ('requestIdleCallback' in window) {
    requestIdleCallback(loadAdSense, { timeout: 2000 });
  } else {
    // Fallback: load after a short delay
    setTimeout(loadAdSense, 1000);
  }
  
  // Also load on first user interaction
  var events = ['mousemove', 'scroll', 'touchstart', 'click', 'keydown'];
  var loadOnInteraction = function() {
    loadAdSense();
    events.forEach(function(event) {
      window.removeEventListener(event, loadOnInteraction, { passive: true });
    });
  };
  
  events.forEach(function(event) {
    window.addEventListener(event, loadOnInteraction, { passive: true, once: true });
  });
})();
