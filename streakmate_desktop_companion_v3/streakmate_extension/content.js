(() => {
  if (window.__streakMateObserverInstalled) return;
  window.__streakMateObserverInstalled = true;
  let lastSignal = 0;
  const acceptedPattern = /\bAccepted\b/i;
  function scan(node) {
    if (!node || !(node instanceof Element)) return;
    const text = (node.innerText || node.textContent || "").slice(0, 6000);
    if (!acceptedPattern.test(text)) return;
    // Require result-like context to reduce false positives.
    if (!/\b(Runtime|Memory|submission|beats|testcases?)\b/i.test(text)) return;
    const now = Date.now();
    if (now - lastSignal < 8000) return;
    lastSignal = now;
    chrome.runtime.sendMessage({type:"STREAKMATE_ACCEPTED"}).catch(()=>{});
  }
  const observer = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const n of m.addedNodes) {
        if (n instanceof Element) {
          scan(n);
          n.querySelectorAll?.("*").forEach(scan);
        }
      }
    }
  });
  observer.observe(document.documentElement,{subtree:true,childList:true});
})();
