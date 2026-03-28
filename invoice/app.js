const THEMES = {
  ember: { name: "Ember", accent: "#c85b31", soft: "#ffe8df", deep: "#8a3a1d" },
  tide: { name: "Tide", accent: "#0d8a83", soft: "#dff7f4", deep: "#0d5f5a" },
  cobalt: { name: "Cobalt", accent: "#2d5fd4", soft: "#e1e8fb", deep: "#1f4191" },
  olive: { name: "Olive", accent: "#718a27", soft: "#edf5d8", deep: "#4f6218" },
  amber: { name: "Amber", accent: "#d48a1f", soft: "#fff0d2", deep: "#9d6212" },
  rose: { name: "Rose", accent: "#ca5569", soft: "#fde3e7", deep: "#8f3443" },
};

const CURRENCY_META = {
  CAD: { label: "CAD", locale: "en-CA", currency: "CAD", maxFractionDigits: 2 },
  USD: { label: "USD", locale: "en-US", currency: "USD", maxFractionDigits: 2 },
  EUR: { label: "EUR", locale: "en-IE", currency: "EUR", maxFractionDigits: 2 },
  GBP: { label: "GBP", locale: "en-GB", currency: "GBP", maxFractionDigits: 2 },
  AUD: { label: "AUD", locale: "en-AU", currency: "AUD", maxFractionDigits: 2 },
  BTC: { label: "BTC (sats)", locale: "en-US", currency: "BTC", maxFractionDigits: 0 },
};

const form = document.querySelector("#invoice-form");
const lineItemsList = document.querySelector("#line-items-list");
const themePicker = document.querySelector("#theme-picker");
const logoUpload = document.querySelector("#logo-upload");
const addLineItemButton = document.querySelector("#add-line-item");
const downloadPdfButton = document.querySelector("#download-pdf");
const printInvoiceButton = document.querySelector("#print-invoice");
const resetInvoiceButton = document.querySelector("#reset-invoice");

const previewRefs = {
  formSubtotal: document.querySelector("#form-subtotal"),
  formTax: document.querySelector("#form-tax"),
  formDiscountLabel: document.querySelector("#form-discount-label"),
  formDiscount: document.querySelector("#form-discount"),
  formTotal: document.querySelector("#form-total"),
  toolbarCurrency: document.querySelector("#preview-toolbar-currency"),
  logoFrame: document.querySelector("#preview-logo-frame"),
  logoImage: document.querySelector("#preview-logo"),
  companyName: document.querySelector("#preview-company-name"),
  companyAddress: document.querySelector("#preview-company-address"),
  status: document.querySelector("#preview-status"),
  invoiceNumber: document.querySelector("#preview-invoice-number"),
  invoiceDate: document.querySelector("#preview-invoice-date"),
  dueDate: document.querySelector("#preview-due-date"),
  clientName: document.querySelector("#preview-client-name"),
  clientAddress: document.querySelector("#preview-client-address"),
  lineItems: document.querySelector("#preview-line-items"),
  subtotal: document.querySelector("#preview-subtotal"),
  tax: document.querySelector("#preview-tax"),
  discountLabel: document.querySelector("#preview-discount-label"),
  discount: document.querySelector("#preview-discount"),
  total: document.querySelector("#preview-total"),
  notes: document.querySelector("#preview-notes"),
  paymentInfo: document.querySelector("#preview-payment-info"),
};

const fields = Array.from(form.querySelectorAll("[data-field]"));
let state = createDefaultState();

init();

function init() {
  renderThemePicker();
  syncFormFields();
  renderLineItemControls();
  applyTheme();
  renderPreview();
  bindEvents();
}

function bindEvents() {
  form.addEventListener("input", handleFieldChange);
  form.addEventListener("change", handleFieldChange);

  lineItemsList.addEventListener("input", handleLineItemChange);
  lineItemsList.addEventListener("click", handleLineItemRemove);

  themePicker.addEventListener("click", handleThemeSelection);

  logoUpload.addEventListener("change", handleLogoUpload);
  addLineItemButton.addEventListener("click", () => {
    state.lineItems.push(createLineItem());
    renderLineItemControls();
    renderPreview();
  });

  downloadPdfButton.addEventListener("click", downloadPdf);
  printInvoiceButton.addEventListener("click", () => window.print());
  resetInvoiceButton.addEventListener("click", resetInvoice);
}

function handleFieldChange(event) {
  const field = event.target.dataset.field;

  if (!field) {
    return;
  }

  if (field === "discount") {
    state.discount = clampNumber(event.target.value, 0, 100);
  } else {
    state[field] = event.target.value;
  }

  if (field === "currency") {
    renderLineItemControls();
  }

  applyTheme();
  renderPreview();
}

function handleLineItemChange(event) {
  const itemId = event.target.dataset.lineId;
  const field = event.target.dataset.lineField;

  if (!itemId || !field) {
    return;
  }

  const item = state.lineItems.find((entry) => entry.id === itemId);

  if (!item) {
    return;
  }

  if (field === "description") {
    item.description = event.target.value;
  } else if (field === "qty") {
    item.qty = clampNumber(event.target.value, 0);
  } else if (field === "rate") {
    item.rate = clampNumber(event.target.value, 0);
  } else if (field === "tax") {
    item.tax = clampNumber(event.target.value, 0, 100);
  }

  updateLineItemAmount(item.id);
  renderPreview();
}

function handleLineItemRemove(event) {
  const removeButton = event.target.closest("[data-action='remove-line']");

  if (!removeButton) {
    return;
  }

  const itemId = removeButton.dataset.lineId;

  state.lineItems = state.lineItems.filter((item) => item.id !== itemId);

  if (!state.lineItems.length) {
    state.lineItems = [createLineItem()];
  }

  renderLineItemControls();
  renderPreview();
}

function handleThemeSelection(event) {
  const themeButton = event.target.closest("[data-theme]");

  if (!themeButton) {
    return;
  }

  state.accentTheme = themeButton.dataset.theme;
  applyTheme();
  renderThemePicker();
  renderPreview();
}

function handleLogoUpload(event) {
  const [file] = event.target.files || [];

  if (!file) {
    state.logoDataUrl = "";
    renderPreview();
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    state.logoDataUrl = typeof reader.result === "string" ? reader.result : "";
    renderPreview();
  };
  reader.readAsDataURL(file);
}

function renderThemePicker() {
  themePicker.innerHTML = Object.entries(THEMES)
    .map(([key, theme]) => {
      const isActive = key === state.accentTheme ? "is-active" : "";
      return `
        <button class="theme-chip ${isActive}" type="button" data-theme="${key}" aria-pressed="${key === state.accentTheme}">
          <span class="theme-swatch" style="background:${theme.accent}"></span>
          <span class="theme-name">${theme.name}</span>
        </button>
      `;
    })
    .join("");
}

function renderLineItemControls() {
  const rateStep = state.currency === "BTC" ? "1" : "0.01";

  lineItemsList.innerHTML = state.lineItems
    .map((item) => {
      const amount = calculateLineTotal(item);
      return `
        <div class="line-item-row">
          <input
            class="line-item-description"
            type="text"
            data-line-id="${item.id}"
            data-line-field="description"
            value="${escapeAttribute(item.description)}"
            placeholder="Website design sprint"
          />
          <input
            type="number"
            min="0"
            step="0.01"
            data-line-id="${item.id}"
            data-line-field="qty"
            value="${formatInputNumber(item.qty)}"
          />
          <input
            type="number"
            min="0"
            step="${rateStep}"
            data-line-id="${item.id}"
            data-line-field="rate"
            value="${formatInputNumber(item.rate)}"
          />
          <input
            type="number"
            min="0"
            max="100"
            step="0.01"
            data-line-id="${item.id}"
            data-line-field="tax"
            value="${formatInputNumber(item.tax)}"
          />
          <div class="line-item-amount" data-line-amount="${item.id}">${formatMoney(amount, state.currency)}</div>
          <button
            class="icon-button"
            type="button"
            aria-label="Remove line item"
            data-action="remove-line"
            data-line-id="${item.id}"
          >
            x
          </button>
        </div>
      `;
    })
    .join("");
}

function renderPreview() {
  const totals = calculateTotals();

  previewRefs.toolbarCurrency.textContent = CURRENCY_META[state.currency].label;

  if (state.logoDataUrl) {
    previewRefs.logoFrame.hidden = false;
    previewRefs.logoImage.src = state.logoDataUrl;
  } else {
    previewRefs.logoFrame.hidden = true;
    previewRefs.logoImage.removeAttribute("src");
  }

  setText(previewRefs.companyName, state.companyName || "Your Company");
  setMultilineText(
    previewRefs.companyAddress,
    state.companyAddress || "Add your company address to brand the invoice.",
    !state.companyAddress
  );

  previewRefs.status.className = `status-pill status-${state.status.toLowerCase()}`;
  setText(previewRefs.status, state.status);
  setText(previewRefs.invoiceNumber, state.invoiceNumber || "INV-001");
  setText(previewRefs.invoiceDate, formatDate(state.invoiceDate));
  setText(previewRefs.dueDate, formatDate(state.dueDate));

  setText(previewRefs.clientName, state.clientName || "Client or company name");
  setMultilineText(
    previewRefs.clientAddress,
    state.clientAddress || "Add the bill-to address block here.",
    !state.clientAddress
  );

  previewRefs.lineItems.innerHTML = state.lineItems
    .map((item) => {
      const description = item.description || "Line item";
      return `
        <tr>
          <td>${escapeHtml(description)}</td>
          <td>${formatQuantity(item.qty)}</td>
          <td>${formatMoney(item.rate, state.currency)}</td>
          <td>${formatPercent(item.tax)}</td>
          <td>${formatMoney(calculateLineTotal(item), state.currency)}</td>
        </tr>
      `;
    })
    .join("");

  setText(previewRefs.subtotal, formatMoney(totals.subtotal, state.currency));
  setText(previewRefs.tax, formatMoney(totals.tax, state.currency));
  setText(previewRefs.formSubtotal, formatMoney(totals.subtotal, state.currency));
  setText(previewRefs.formTax, formatMoney(totals.tax, state.currency));
  setText(previewRefs.discountLabel, `Discount (${formatPercent(state.discount)})`);
  setText(previewRefs.formDiscountLabel, `Discount (${formatPercent(state.discount)})`);
  setText(previewRefs.discount, `-${formatMoney(totals.discountAmount, state.currency)}`);
  setText(previewRefs.formDiscount, `-${formatMoney(totals.discountAmount, state.currency)}`);
  setText(previewRefs.total, formatMoney(totals.total, state.currency));
  setText(previewRefs.formTotal, formatMoney(totals.total, state.currency));

  setMultilineText(
    previewRefs.notes,
    state.notes || "Add optional notes for your client.",
    !state.notes
  );
  setMultilineText(
    previewRefs.paymentInfo,
    state.paymentInfo || "Add bank details, e-Transfer info, or payment instructions.",
    !state.paymentInfo
  );
}

function applyTheme() {
  const theme = THEMES[state.accentTheme] || THEMES.ember;
  document.documentElement.style.setProperty("--accent", theme.accent);
  document.documentElement.style.setProperty("--accent-soft", theme.soft);
  document.documentElement.style.setProperty("--accent-deep", theme.deep);
  document.documentElement.style.setProperty("--accent-ghost", hexToRgba(theme.accent, 0.12));
}

function syncFormFields() {
  fields.forEach((field) => {
    const stateValue = state[field.dataset.field];

    if (typeof stateValue === "number") {
      field.value = formatInputNumber(stateValue);
    } else {
      field.value = stateValue;
    }
  });
}

function updateLineItemAmount(itemId) {
  const amountNode = lineItemsList.querySelector(`[data-line-amount="${itemId}"]`);
  const item = state.lineItems.find((entry) => entry.id === itemId);

  if (!amountNode || !item) {
    return;
  }

  amountNode.textContent = formatMoney(calculateLineTotal(item), state.currency);
}

function calculateLineSubtotal(item) {
  return item.qty * item.rate;
}

function calculateLineTax(item) {
  return calculateLineSubtotal(item) * (item.tax / 100);
}

function calculateLineTotal(item) {
  return calculateLineSubtotal(item) + calculateLineTax(item);
}

function calculateTotals() {
  const rawSubtotal = state.lineItems.reduce((sum, item) => sum + calculateLineSubtotal(item), 0);
  const rawTax = state.lineItems.reduce((sum, item) => sum + calculateLineTax(item), 0);
  const discountRate = state.discount / 100;
  const discountAmount = rawSubtotal * discountRate;
  const tax = rawTax * (1 - discountRate);
  const total = rawSubtotal - discountAmount + tax;

  return {
    subtotal: rawSubtotal,
    tax,
    discountAmount,
    total,
  };
}

function downloadPdf() {
  if (!window.jspdf || typeof window.jspdf.jsPDF !== "function") {
    window.alert("jsPDF did not load. Check your connection and try again.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const theme = THEMES[state.accentTheme] || THEMES.ember;
  const totals = calculateTotals();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 42;
  const metaX = pageWidth - margin - 180;
  let cursorY = 42;
  let hasRenderableLogo = false;

  if (typeof doc.autoTable !== "function") {
    window.alert("autoTable did not load. Check your connection and try again.");
    return;
  }

  doc.setFillColor(...hexToRgb(theme.accent));
  doc.rect(0, 0, pageWidth, 18, "F");

  if (state.logoDataUrl) {
    const imageType = getImageType(state.logoDataUrl);

    if (imageType) {
      try {
        doc.addImage(state.logoDataUrl, imageType, margin, cursorY, 58, 58);
        hasRenderableLogo = true;
      } catch (error) {
        hasRenderableLogo = false;
      }
    }
  }

  const headerStartX = hasRenderableLogo ? margin + 74 : margin;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(24);
  doc.setTextColor(...hexToRgb(theme.deep));
  doc.text(state.companyName || "Your Company", headerStartX, cursorY + 22);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(92, 82, 74);
  const companyLines = splitText(doc, state.companyAddress || "Add your company address.", 180);
  doc.text(companyLines, headerStartX, cursorY + 42);

  doc.setFillColor(...hexToRgb(theme.soft));
  doc.roundedRect(metaX, cursorY - 4, 180, 98, 16, 16, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(...hexToRgb(theme.deep));
  doc.text(state.status, metaX + 16, cursorY + 18);

  doc.setFontSize(22);
  doc.text(`Invoice ${state.invoiceNumber || "INV-001"}`, metaX + 16, cursorY + 48);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(80, 72, 64);
  doc.text(`Issued: ${formatDate(state.invoiceDate)}`, metaX + 16, cursorY + 68);
  doc.text(`Due: ${formatDate(state.dueDate)}`, metaX + 16, cursorY + 84);

  cursorY = 156;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9.5);
  doc.setTextColor(...hexToRgb(theme.deep));
  doc.text("Bill to", margin, cursorY);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.setTextColor(30, 28, 26);
  doc.text(state.clientName || "Client or company name", margin, cursorY + 24);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(92, 82, 74);
  const clientLines = splitText(doc, state.clientAddress || "Add the bill-to address block here.", 250);
  doc.text(clientLines, margin, cursorY + 44);

  const tableStartY = Math.max(250, cursorY + 44 + clientLines.length * 13 + 18);
  const rows = state.lineItems.map((item) => [
    item.description || "Line item",
    formatQuantity(item.qty),
    formatMoney(item.rate, state.currency),
    formatPercent(item.tax),
    formatMoney(calculateLineTotal(item), state.currency),
  ]);

  doc.autoTable({
    startY: tableStartY,
    head: [["Description", "Qty", "Rate", "Tax", "Amount"]],
    body: rows,
    theme: "plain",
    headStyles: {
      fillColor: hexToRgb(theme.soft),
      textColor: hexToRgb(theme.deep),
      fontStyle: "bold",
      cellPadding: { top: 10, right: 10, bottom: 10, left: 10 },
    },
    bodyStyles: {
      textColor: [42, 37, 33],
      fontSize: 10.5,
      cellPadding: { top: 10, right: 10, bottom: 10, left: 10 },
    },
    alternateRowStyles: {
      fillColor: [255, 252, 247],
    },
    columnStyles: {
      1: { halign: "right", cellWidth: 54 },
      2: { halign: "right", cellWidth: 80 },
      3: { halign: "right", cellWidth: 60 },
      4: { halign: "right", cellWidth: 96 },
    },
    margin: { left: margin, right: margin },
  });

  let afterTableY = doc.lastAutoTable.finalY + 26;
  const summaryX = pageWidth - margin - 180;

  if (afterTableY + 130 > pageHeight - margin) {
    doc.addPage();
    afterTableY = margin;
  }

  doc.setDrawColor(232, 223, 213);
  doc.setFillColor(255, 251, 245);
  doc.roundedRect(summaryX, afterTableY, 180, 104, 14, 14, "FD");

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(88, 78, 70);
  doc.text("Subtotal", summaryX + 14, afterTableY + 24);
  doc.text("Tax", summaryX + 14, afterTableY + 44);
  doc.text(`Discount (${formatPercent(state.discount)})`, summaryX + 14, afterTableY + 64);

  doc.setFont("helvetica", "bold");
  doc.setTextColor(28, 27, 25);
  doc.text(formatMoney(totals.subtotal, state.currency), summaryX + 166, afterTableY + 24, { align: "right" });
  doc.text(formatMoney(totals.tax, state.currency), summaryX + 166, afterTableY + 44, { align: "right" });
  doc.text(`-${formatMoney(totals.discountAmount, state.currency)}`, summaryX + 166, afterTableY + 64, { align: "right" });

  doc.setDrawColor(...hexToRgb(theme.accent));
  doc.line(summaryX + 14, afterTableY + 78, summaryX + 166, afterTableY + 78);
  doc.setFontSize(13);
  doc.setTextColor(...hexToRgb(theme.deep));
  doc.text("Total", summaryX + 14, afterTableY + 96);
  doc.text(formatMoney(totals.total, state.currency), summaryX + 166, afterTableY + 96, { align: "right" });

  let notesY = afterTableY;

  if (state.notes) {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9.5);
    doc.setTextColor(...hexToRgb(theme.deep));
    doc.text("Notes", margin, notesY + 12);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor(92, 82, 74);
    doc.text(splitText(doc, state.notes, 270), margin, notesY + 32);
    notesY += 76;
  }

  if (state.paymentInfo) {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9.5);
    doc.setTextColor(...hexToRgb(theme.deep));
    doc.text("Payment details", margin, notesY + 12);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor(92, 82, 74);
    doc.text(splitText(doc, state.paymentInfo, 270), margin, notesY + 32);
  }

  doc.save(`${sanitizeFilename(state.invoiceNumber || "invoice")}.pdf`);
}

function resetInvoice() {
  state = createDefaultState();
  syncFormFields();
  logoUpload.value = "";
  renderThemePicker();
  renderLineItemControls();
  applyTheme();
  renderPreview();
}

function createDefaultState() {
  return {
    companyName: "",
    companyAddress: "",
    clientName: "",
    clientAddress: "",
    invoiceNumber: "INV-001",
    invoiceDate: toIsoDate(new Date()),
    dueDate: toIsoDate(addDays(new Date(), 14)),
    status: "Draft",
    currency: "CAD",
    discount: 0,
    notes: "",
    paymentInfo: "",
    accentTheme: "ember",
    logoDataUrl: "",
    lineItems: [createLineItem()],
  };
}

function createLineItem() {
  return {
    id: createId(),
    description: "",
    qty: 1,
    rate: 0,
    tax: 0,
  };
}

function createId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }

  return `line-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatMoney(value, currencyCode) {
  if (currencyCode === "BTC") {
    return `${Math.round(value).toLocaleString("en-US")} sats`;
  }

  const meta = CURRENCY_META[currencyCode];

  return new Intl.NumberFormat(meta.locale, {
    style: "currency",
    currency: meta.currency,
    maximumFractionDigits: meta.maxFractionDigits,
    minimumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value) {
  const numericValue = Number.isFinite(value) ? value : 0;
  return `${numericValue.toFixed(numericValue % 1 === 0 ? 0 : 2)}%`;
}

function formatQuantity(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return value % 1 === 0 ? String(value) : value.toFixed(2);
}

function formatInputNumber(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return String(value);
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-CA", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function setText(node, value) {
  node.textContent = value;
}

function setMultilineText(node, value, isPlaceholder) {
  node.textContent = value;
  node.classList.toggle("is-placeholder", Boolean(isPlaceholder));
}

function clampNumber(value, min = 0, max = Number.POSITIVE_INFINITY) {
  const numericValue = Number.parseFloat(value);

  if (Number.isNaN(numericValue)) {
    return min;
  }

  return Math.min(Math.max(numericValue, min), max);
}

function toIsoDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}

function hexToRgb(hex) {
  const normalized = hex.replace("#", "");
  const pairs = normalized.length === 3
    ? normalized.split("").map((char) => `${char}${char}`)
    : normalized.match(/.{1,2}/g);

  return pairs.map((pair) => Number.parseInt(pair, 16));
}

function hexToRgba(hex, alpha) {
  return `rgba(${hexToRgb(hex).join(", ")}, ${alpha})`;
}

function getImageType(dataUrl) {
  if (dataUrl.startsWith("data:image/png")) {
    return "PNG";
  }

  if (dataUrl.startsWith("data:image/jpeg") || dataUrl.startsWith("data:image/jpg")) {
    return "JPEG";
  }

  if (dataUrl.startsWith("data:image/webp")) {
    return "WEBP";
  }

  return null;
}

function splitText(doc, text, maxWidth = 42) {
  const lines = String(text)
    .split("\n")
    .flatMap((part) => doc.splitTextToSize(part || " ", maxWidth));

  return lines;
}

function sanitizeFilename(value) {
  return value.replace(/[^a-z0-9-_]+/gi, "-").replace(/^-+|-+$/g, "") || "invoice";
}
