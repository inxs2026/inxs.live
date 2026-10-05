(function () {
  const CANDIDATE_SELECTOR = ".print-page-group";

  function uniqueElements(elements) {
    return Array.from(new Set(elements));
  }

  function hasManualPageBreak(node) {
    return (
      node.classList.contains("print-break-before-page") ||
      node.classList.contains("break-before-page") ||
      node.classList.contains("force-page-break")
    );
  }

  function hasCandidateAncestor(node, scope) {
    let parent = node.parentElement;

    while (parent && parent !== scope) {
      if (parent.matches?.(CANDIDATE_SELECTOR)) {
        return true;
      }
      parent = parent.parentElement;
    }

    return false;
  }

  function clearPrintPagination(doc = document) {
    doc.querySelectorAll("[data-dynamic-print-break='true']").forEach((node) => node.remove());
    doc.querySelectorAll(".print-can-split").forEach((node) => node.classList.remove("print-can-split"));
  }

  function getPrintPageBodyHeight(doc = document) {
    if (!doc.body) {
      return 0;
    }

    const probe = doc.createElement("div");
    const styles = doc.defaultView ? doc.defaultView.getComputedStyle(doc.documentElement) : null;
    const bodyHeight = styles?.getPropertyValue("--print-body-height").trim() || "calc(11in - 40mm)";

    probe.style.position = "absolute";
    probe.style.left = "-10000px";
    probe.style.top = "0";
    probe.style.visibility = "hidden";
    probe.style.pointerEvents = "none";
    probe.style.width = "1px";
    probe.style.height = bodyHeight;

    doc.body.appendChild(probe);
    const height = probe.getBoundingClientRect().height;
    probe.remove();

    return height;
  }

  function preparePrintPagination(doc = document, root) {
    const scope = root || doc.querySelector("#lease-preview") || doc.body;

    if (!scope || !doc.body) {
      return 0;
    }

    clearPrintPagination(doc);

    const pageHeight = getPrintPageBodyHeight(doc);
    if (!pageHeight) {
      return 0;
    }

    const scopeTop = scope.getBoundingClientRect().top;
    const tolerance = 12;
    const candidates = uniqueElements(Array.from(scope.querySelectorAll(CANDIDATE_SELECTOR))).filter((node) => {
      if (!scope.contains(node) || hasManualPageBreak(node) || hasCandidateAncestor(node, scope)) {
        return false;
      }

      return true;
    });

    candidates.forEach((node) => {
      node.classList.remove("print-can-split");

      const rect = node.getBoundingClientRect();
      if (!rect.height) {
        return;
      }

      if (rect.height >= pageHeight - tolerance) {
        node.classList.add("print-can-split");
        return;
      }

      const relativeTop = rect.top - scopeTop;
      const usedOnPage = ((relativeTop % pageHeight) + pageHeight) % pageHeight;

      if (usedOnPage <= tolerance) {
        return;
      }

      if (usedOnPage + rect.height > pageHeight - tolerance) {
        const pageBreak = doc.createElement("div");
        pageBreak.className = "print-page-break";
        pageBreak.setAttribute("aria-hidden", "true");
        pageBreak.setAttribute("data-dynamic-print-break", "true");
        node.before(pageBreak);
      }
    });

    return pageHeight;
  }

  function setupLeasePrintPagination(rootSelector = "#lease-preview") {
    if (window.__leasePrintPaginationSetup) {
      return;
    }

    const run = () => {
      const root = document.querySelector(rootSelector);
      if (root) {
        preparePrintPagination(document, root);
      }
    };

    const cleanup = () => {
      clearPrintPagination(document);
    };

    window.addEventListener("beforeprint", run);
    window.addEventListener("afterprint", cleanup);
    window.__leasePrintPaginationSetup = true;
  }

  window.preparePrintPagination = preparePrintPagination;
  window.clearPrintPagination = clearPrintPagination;
  window.setupLeasePrintPagination = setupLeasePrintPagination;

  const init = () => {
    if (document.querySelector("#lease-preview")) {
      setupLeasePrintPagination("#lease-preview");
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
