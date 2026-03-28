const LOAN_TYPES = {
  mortgage: { label: "Mortgage", minYears: 5, maxYears: 30 },
  personal: { label: "Personal Loan", minYears: 1, maxYears: 10 },
  auto: { label: "Auto Loan", minYears: 1, maxYears: 8 },
};

const FREQUENCIES = {
  monthly: { label: "Monthly", periodsPerYear: 12, accelerated: false },
  semiMonthly: { label: "Semi-Monthly", periodsPerYear: 24, accelerated: false },
  biWeekly: { label: "Bi-Weekly", periodsPerYear: 26, accelerated: false },
  acceleratedBiWeekly: { label: "Accelerated Bi-Weekly", periodsPerYear: 26, accelerated: true },
  weekly: { label: "Weekly", periodsPerYear: 52, accelerated: false },
};

const CMHC_RATE_TABLE = [
  { maxLtv: 0.85, rate: 0.028 },
  { maxLtv: 0.9, rate: 0.031 },
  { maxLtv: 0.95, rate: 0.04 },
];

const refs = {
  form: document.querySelector("#calculator-form"),
  loanType: document.querySelector("#loan-type"),
  paymentFrequency: document.querySelector("#payment-frequency"),
  interestRate: document.querySelector("#interest-rate"),
  amortizationYears: document.querySelector("#amortization-years"),
  homePrice: document.querySelector("#home-price"),
  downPaymentAmount: document.querySelector("#down-payment-amount"),
  downPaymentPercent: document.querySelector("#down-payment-percent"),
  firstTimeBuyer: document.querySelector("#first-time-buyer"),
  newBuild: document.querySelector("#new-build"),
  loanAmount: document.querySelector("#loan-amount"),
  loanAmountLabel: document.querySelector("#loan-amount-label"),
  extraPayment: document.querySelector("#extra-payment"),
  annualLumpSum: document.querySelector("#annual-lump-sum"),
  mortgageFields: document.querySelector("#mortgage-fields"),
  loanFields: document.querySelector("#loan-fields"),
  compoundingTitle: document.querySelector("#compounding-title"),
  compoundingCopy: document.querySelector("#compounding-copy"),
  cmhcTitle: document.querySelector("#cmhc-title"),
  cmhcCopy: document.querySelector("#cmhc-copy"),
  stressTitle: document.querySelector("#stress-title"),
  stressCopy: document.querySelector("#stress-copy"),
  warningsList: document.querySelector("#warnings-list"),
  summaryGrid: document.querySelector("#summary-grid"),
  yearlyChart: document.querySelector("#yearly-chart"),
  scheduleHead: document.querySelector("#schedule-head"),
  scheduleBody: document.querySelector("#schedule-body"),
  tableViewButtons: Array.from(document.querySelectorAll("[data-table-view]")),
  downloadCsv: document.querySelector("#download-csv"),
  downloadPdf: document.querySelector("#download-pdf"),
  resetButton: document.querySelector("#reset-calculator"),
};

let state = createDefaultState();
let currentMetrics = null;

init();

function init() {
  syncFormFromState();
  render();
  bindEvents();
}

function bindEvents() {
  refs.form.addEventListener("input", handleInputChange);
  refs.form.addEventListener("change", handleInputChange);

  refs.tableViewButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.tableView = button.dataset.tableView;
      renderScheduleTable();
      renderTableViewButtons();
    });
  });

  refs.downloadCsv.addEventListener("click", downloadCsv);
  refs.downloadPdf.addEventListener("click", downloadPdf);
  refs.resetButton.addEventListener("click", resetCalculator);
}

function handleInputChange(event) {
  const target = event.target;

  switch (target.id) {
    case "loan-type":
      state.loanType = target.value;
      break;
    case "payment-frequency":
      state.paymentFrequency = target.value;
      break;
    case "interest-rate":
      state.interestRate = clampNumber(target.value, 0, 100);
      break;
    case "amortization-years":
      state.amortizationYears = clampNumber(target.value, 1, 40);
      break;
    case "home-price":
      state.homePrice = clampNumber(target.value, 0);
      if (state.downPaymentMode === "percent") {
        state.downPaymentAmount = state.homePrice * (state.downPaymentPercent / 100);
      } else {
        state.downPaymentPercent = state.homePrice ? (state.downPaymentAmount / state.homePrice) * 100 : 0;
      }
      break;
    case "down-payment-amount":
      state.downPaymentMode = "amount";
      state.downPaymentAmount = clampNumber(target.value, 0);
      state.downPaymentPercent = state.homePrice ? (state.downPaymentAmount / state.homePrice) * 100 : 0;
      break;
    case "down-payment-percent":
      state.downPaymentMode = "percent";
      state.downPaymentPercent = clampNumber(target.value, 0, 100);
      state.downPaymentAmount = state.homePrice * (state.downPaymentPercent / 100);
      break;
    case "first-time-buyer":
      state.firstTimeBuyer = target.checked;
      break;
    case "new-build":
      state.newBuild = target.checked;
      break;
    case "loan-amount":
      state.loanAmount = clampNumber(target.value, 0);
      break;
    case "extra-payment":
      state.extraPayment = clampNumber(target.value, 0);
      break;
    case "annual-lump-sum":
      state.annualLumpSum = clampNumber(target.value, 0);
      break;
    default:
      return;
  }

  normalizeState();
  syncFormFromState();
  render();
}

function render() {
  currentMetrics = calculateMetrics();
  renderVisibility();
  renderInsights();
  renderSummaryCards();
  renderChart();
  renderScheduleTable();
  renderTableViewButtons();
}

function renderVisibility() {
  const isMortgage = state.loanType === "mortgage";
  refs.mortgageFields.classList.toggle("is-hidden", !isMortgage);
  refs.loanFields.classList.toggle("is-hidden", isMortgage);
  refs.loanAmountLabel.textContent = state.loanType === "auto" ? "Vehicle loan amount" : "Loan amount";
}

function renderInsights() {
  if (!currentMetrics) {
    return;
  }

  if (state.loanType === "mortgage") {
    refs.compoundingTitle.textContent = "Semi-annual mortgage compounding";
    refs.compoundingCopy.textContent =
      "This calculator uses the Canadian semi-annual formula: (1 + r/2)^2 - 1 for the effective annual rate, then converts it to your selected payment frequency.";
  } else {
    refs.compoundingTitle.textContent = "Monthly-style loan compounding";
    refs.compoundingCopy.textContent =
      "Personal and auto loan scenarios here use monthly compounding converted to your selected payment frequency.";
  }

  if (state.loanType !== "mortgage") {
    refs.cmhcTitle.textContent = "Not used";
    refs.cmhcCopy.textContent = "CMHC mortgage loan insurance only applies to insured mortgage scenarios.";
    refs.stressTitle.textContent = "Not used";
    refs.stressCopy.textContent = "The mortgage stress test is only shown for mortgage scenarios.";
  } else if (currentMetrics.mortgage.isInvalidMinimumDown) {
    refs.cmhcTitle.textContent = "Below minimum down payment";
    refs.cmhcCopy.textContent = `Minimum down payment for this home price is ${formatMoney(currentMetrics.mortgage.minimumDownPayment)}.`;
    refs.stressTitle.textContent = `Qualify at ${formatPercent(currentMetrics.mortgage.qualifyingRate)}`;
    refs.stressCopy.textContent = `Rule used: higher of contract + 2% or 5.25%. Selected frequency qualifying payment: ${formatMoney(currentMetrics.mortgage.qualifyingPayment)}.`;
  } else if (currentMetrics.mortgage.requiresInsurance) {
    refs.cmhcTitle.textContent = `${formatPercent(currentMetrics.mortgage.cmhcRate * 100)} premium`;
    refs.cmhcCopy.textContent = `Premium added to the mortgage: ${formatMoney(currentMetrics.mortgage.cmhcPremium)}. Insured amortization cap in this scenario: ${currentMetrics.mortgage.maxAmortizationYears} years.`;
    refs.stressTitle.textContent = `Qualify at ${formatPercent(currentMetrics.mortgage.qualifyingRate)}`;
    refs.stressCopy.textContent = `Rule used: higher of contract + 2% or 5.25%. Selected frequency qualifying payment: ${formatMoney(currentMetrics.mortgage.qualifyingPayment)}.`;
  } else {
    refs.cmhcTitle.textContent = "No insurance premium";
    refs.cmhcCopy.textContent = "With 20%+ down, this is treated as a conventional mortgage with no CMHC premium added.";
    refs.stressTitle.textContent = `Qualify at ${formatPercent(currentMetrics.mortgage.qualifyingRate)}`;
    refs.stressCopy.textContent = `Rule used: higher of contract + 2% or 5.25%. Selected frequency qualifying payment: ${formatMoney(currentMetrics.mortgage.qualifyingPayment)}.`;
  }

  const warnings = currentMetrics.warnings.length ? currentMetrics.warnings : ["Using the current rule set referenced below."];
  refs.warningsList.innerHTML = warnings
    .map((item) => {
      const className = item.includes("Current rule") ? "warning-item warning-neutral" : "warning-item";
      return `<div class="${className}">${escapeHtml(item)}</div>`;
    })
    .join("");
}

function renderSummaryCards() {
  if (!currentMetrics) {
    return;
  }

  const cards = [
    {
      label: "Regular Payment",
      value: formatMoney(currentMetrics.schedule.regularPayment),
      note: `${FREQUENCIES[state.paymentFrequency].label} payment`,
    },
    {
      label: "Financed Principal",
      value: formatMoney(currentMetrics.principal),
      note: state.loanType === "mortgage" && currentMetrics.mortgage.cmhcPremium
        ? `Includes ${formatMoney(currentMetrics.mortgage.cmhcPremium)} CMHC premium`
        : "Amount financed before interest",
    },
    {
      label: "Total Interest",
      value: formatMoney(currentMetrics.schedule.totalInterest),
      note: `Over ${formatDuration(currentMetrics.schedule.rows.length, currentMetrics.schedule.periodsPerYear)}`,
    },
    {
      label: "Mortgage-Free / Paid Off",
      value: formatDuration(currentMetrics.schedule.rows.length, currentMetrics.schedule.periodsPerYear),
      note: `${currentMetrics.schedule.rows.length} payments`,
    },
    {
      label: "Interest Savings",
      value: formatMoney(currentMetrics.savings.interestSaved),
      note: currentMetrics.savings.interestSaved > 0 ? "From extra payments and lump sums" : "No prepayment savings yet",
    },
    {
      label: "Time Saved",
      value: currentMetrics.savings.periodsSaved > 0
        ? formatDuration(currentMetrics.savings.periodsSaved, currentMetrics.schedule.periodsPerYear)
        : "0",
      note: currentMetrics.savings.periodsSaved > 0 ? "Earlier than the no-prepayment plan" : "Add prepayments to shorten the loan",
    },
  ];

  if (state.loanType === "mortgage") {
    cards.push({
      label: "Stress Test Payment",
      value: formatMoney(currentMetrics.mortgage.qualifyingPayment),
      note: `At ${formatPercent(currentMetrics.mortgage.qualifyingRate)}`,
    });
  }

  refs.summaryGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="summary-card">
          <p>${escapeHtml(card.label)}</p>
          <strong>${escapeHtml(card.value)}</strong>
          <span>${escapeHtml(card.note)}</span>
        </article>
      `
    )
    .join("");
}

function renderChart() {
  if (!currentMetrics || !currentMetrics.yearlySummary.length) {
    refs.yearlyChart.innerHTML = "";
    return;
  }

  refs.yearlyChart.innerHTML = currentMetrics.yearlySummary
    .map((year) => {
      const total = year.principal + year.interest;
      const principalWidth = total ? (year.principal / total) * 100 : 0;
      const interestWidth = 100 - principalWidth;

      return `
        <div class="chart-row">
          <div class="chart-label">Year ${year.year}</div>
          <div class="chart-stack">
            <span class="chart-principal" style="width:${principalWidth}%"></span>
            <span class="chart-interest" style="width:${interestWidth}%"></span>
          </div>
          <div class="chart-meta">
            <span>Principal ${formatMoney(year.principal)}</span>
            <span>Interest ${formatMoney(year.interest)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderScheduleTable() {
  if (!currentMetrics) {
    return;
  }

  if (state.tableView === "summary") {
    refs.scheduleHead.innerHTML = `
      <tr>
        <th>Year</th>
        <th>Payments</th>
        <th>Principal</th>
        <th>Interest</th>
        <th>Ending Balance</th>
      </tr>
    `;

    refs.scheduleBody.innerHTML = currentMetrics.yearlySummary
      .map(
        (row) => `
          <tr>
            <td>Year ${row.year}</td>
            <td>${formatMoney(row.payments)}</td>
            <td>${formatMoney(row.principal)}</td>
            <td>${formatMoney(row.interest)}</td>
            <td>${formatMoney(row.balance)}</td>
          </tr>
        `
      )
      .join("");
    return;
  }

  const rows = state.tableView === "first24"
    ? currentMetrics.schedule.rows.slice(0, 24)
    : currentMetrics.schedule.rows;

  refs.scheduleHead.innerHTML = `
    <tr>
      <th>Period</th>
      <th>Year</th>
      <th>Payment</th>
      <th>Extra</th>
      <th>Lump Sum</th>
      <th>Principal</th>
      <th>Interest</th>
      <th>Ending Balance</th>
    </tr>
  `;

  refs.scheduleBody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.period}</td>
          <td>${row.year}</td>
          <td>${formatMoney(row.payment)}</td>
          <td>${formatMoney(row.extraPerPeriod)}</td>
          <td>${formatMoney(row.lumpSum)}</td>
          <td>${formatMoney(row.principal)}</td>
          <td>${formatMoney(row.interest)}</td>
          <td>${formatMoney(row.balance)}</td>
        </tr>
      `
    )
    .join("");
}

function renderTableViewButtons() {
  refs.tableViewButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.tableView === state.tableView);
  });
}

function calculateMetrics() {
  const warnings = [];
  let principal;
  let mortgageMetrics = {
    minimumDownPayment: 0,
    requiresInsurance: false,
    cmhcRate: 0,
    cmhcPremium: 0,
    qualifyingRate: 0,
    qualifyingPayment: 0,
    maxAmortizationYears: LOAN_TYPES.mortgage.maxYears,
    isInvalidMinimumDown: false,
  };

  if (state.loanType === "mortgage") {
    const downPaymentAmount = Math.min(state.downPaymentAmount, state.homePrice);
    const downPaymentPercent = state.homePrice ? downPaymentAmount / state.homePrice : 0;
    const minimumDownPayment = calculateMinimumDownPayment(state.homePrice);
    const baseMortgage = Math.max(state.homePrice - downPaymentAmount, 0);
    const requiresInsurance = downPaymentPercent < 0.2;
    const exceedsInsurablePrice = state.homePrice > 1500000 && requiresInsurance;
    const isInvalidMinimumDown = requiresInsurance && downPaymentAmount < minimumDownPayment;
    const maxAmortizationYears = requiresInsurance
      ? (state.firstTimeBuyer || state.newBuild ? 30 : 25)
      : 30;
    let cmhcRate = 0;
    let cmhcPremium = 0;

    if (requiresInsurance && !exceedsInsurablePrice && !isInvalidMinimumDown && baseMortgage > 0) {
      cmhcRate = getCmhcRate(baseMortgage / state.homePrice);
      cmhcPremium = baseMortgage * cmhcRate;
    }

    principal = baseMortgage + cmhcPremium;

    if (exceedsInsurablePrice) {
      warnings.push("Homes above $1.5 million need at least 20% down to qualify.");
    }

    if (isInvalidMinimumDown) {
      warnings.push(`Minimum down payment for this home price is ${formatMoney(minimumDownPayment)}.`);
    }

    if (requiresInsurance) {
      const insuredRule = state.firstTimeBuyer || state.newBuild
        ? "Current rule set: insured mortgages can amortize up to 30 years for first-time buyers and many new builds."
        : "Current rule set: insured mortgages are capped at 25 years in this scenario.";
      warnings.push(insuredRule);
    } else {
      warnings.push("Conventional mortgage scenario: 20%+ down, so no default-insurance premium is added.");
    }

    const qualifyingRate = Math.max(state.interestRate + 2, 5.25);
    const qualifyingPayment = calculateRegularPayment(principal, qualifyingRate, state.amortizationYears, state.paymentFrequency, state.loanType);

    mortgageMetrics = {
      minimumDownPayment,
      requiresInsurance,
      cmhcRate,
      cmhcPremium,
      qualifyingRate,
      qualifyingPayment,
      maxAmortizationYears,
      isInvalidMinimumDown,
    };
  } else {
    principal = state.loanAmount;
    warnings.push("Mortgage-only rules such as CMHC insurance and the stress test are disabled for this loan type.");
  }

  const baseSchedule = buildSchedule({
    principal,
    annualRate: state.interestRate,
    amortizationYears: state.amortizationYears,
    paymentFrequency: state.paymentFrequency,
    loanType: state.loanType,
    extraPayment: 0,
    annualLumpSum: 0,
  });

  const currentSchedule = buildSchedule({
    principal,
    annualRate: state.interestRate,
    amortizationYears: state.amortizationYears,
    paymentFrequency: state.paymentFrequency,
    loanType: state.loanType,
    extraPayment: state.extraPayment,
    annualLumpSum: state.annualLumpSum,
  });

  return {
    principal,
    warnings,
    mortgage: mortgageMetrics,
    schedule: currentSchedule,
    yearlySummary: summarizeByYear(currentSchedule.rows),
    savings: {
      interestSaved: Math.max(baseSchedule.totalInterest - currentSchedule.totalInterest, 0),
      periodsSaved: Math.max(baseSchedule.rows.length - currentSchedule.rows.length, 0),
    },
  };
}

function buildSchedule({ principal, annualRate, amortizationYears, paymentFrequency, loanType, extraPayment, annualLumpSum }) {
  const frequency = FREQUENCIES[paymentFrequency];
  const periodsPerYear = frequency.periodsPerYear;
  const regularPayment = calculateRegularPayment(principal, annualRate, amortizationYears, paymentFrequency, loanType);
  const periodRate = getPeriodRate(annualRate / 100, periodsPerYear, loanType);
  const rows = [];
  let balance = principal;
  let totalInterest = 0;
  let totalPaid = 0;
  let period = 0;
  const maxPeriods = Math.max(periodsPerYear * amortizationYears * 2, 1);

  while (balance > 0.005 && period < maxPeriods) {
    period += 1;
    const interest = balance * periodRate;
    const scheduledLump = annualLumpSum > 0 && period % periodsPerYear === 0 ? annualLumpSum : 0;
    const plannedPayment = regularPayment + extraPayment + scheduledLump;
    const totalDue = balance + interest;
    const payment = Math.min(plannedPayment, totalDue);
    const regularUsed = Math.min(regularPayment, payment);
    const extraUsed = Math.min(extraPayment, Math.max(payment - regularUsed, 0));
    const lumpUsed = Math.max(payment - regularUsed - extraUsed, 0);
    const principalPaid = payment - interest;

    balance = Math.max(balance - principalPaid, 0);
    totalInterest += interest;
    totalPaid += payment;

    rows.push({
      period,
      year: Math.ceil(period / periodsPerYear),
      payment,
      extraPerPeriod: extraUsed,
      lumpSum: lumpUsed,
      principal: principalPaid,
      interest,
      balance,
    });
  }

  return {
    regularPayment,
    periodRate,
    periodsPerYear,
    rows,
    totalInterest,
    totalPaid,
  };
}

function summarizeByYear(rows) {
  const summary = [];

  rows.forEach((row) => {
    const index = row.year - 1;

    if (!summary[index]) {
      summary[index] = {
        year: row.year,
        payments: 0,
        principal: 0,
        interest: 0,
        balance: row.balance,
      };
    }

    summary[index].payments += row.payment;
    summary[index].principal += row.principal;
    summary[index].interest += row.interest;
    summary[index].balance = row.balance;
  });

  return summary;
}

function calculateRegularPayment(principal, annualRate, amortizationYears, paymentFrequency, loanType) {
  if (principal <= 0) {
    return 0;
  }

  const frequency = FREQUENCIES[paymentFrequency];

  if (frequency.accelerated) {
    const monthlyRate = getPeriodRate(annualRate / 100, 12, loanType);
    const monthlyPayment = calculateFixedPayment(principal, monthlyRate, amortizationYears * 12);
    return monthlyPayment / 2;
  }

  const periodRate = getPeriodRate(annualRate / 100, frequency.periodsPerYear, loanType);
  return calculateFixedPayment(principal, periodRate, amortizationYears * frequency.periodsPerYear);
}

function calculateFixedPayment(principal, periodRate, periods) {
  if (!periods) {
    return 0;
  }

  if (periodRate === 0) {
    return principal / periods;
  }

  const growth = Math.pow(1 + periodRate, periods);
  return principal * ((periodRate * growth) / (growth - 1));
}

function getPeriodRate(annualRateDecimal, periodsPerYear, loanType) {
  const compoundingPeriods = loanType === "mortgage" ? 2 : 12;
  return Math.pow(1 + annualRateDecimal / compoundingPeriods, compoundingPeriods / periodsPerYear) - 1;
}

function calculateMinimumDownPayment(homePrice) {
  if (homePrice <= 0) {
    return 0;
  }

  if (homePrice <= 500000) {
    return homePrice * 0.05;
  }

  if (homePrice <= 1500000) {
    return 25000 + (homePrice - 500000) * 0.1;
  }

  return homePrice * 0.2;
}

function getCmhcRate(ltvRatio) {
  const match = CMHC_RATE_TABLE.find((entry) => ltvRatio <= entry.maxLtv);
  return match ? match.rate : 0;
}

function normalizeState() {
  if (state.loanType === "mortgage") {
    state.homePrice = clampNumber(state.homePrice, 0);
    state.downPaymentAmount = clampNumber(state.downPaymentAmount, 0, state.homePrice || Number.POSITIVE_INFINITY);
    state.downPaymentPercent = state.homePrice ? (state.downPaymentAmount / state.homePrice) * 100 : 0;

    const insuredCap = state.downPaymentPercent < 20
      ? (state.firstTimeBuyer || state.newBuild ? 30 : 25)
      : 30;

    state.amortizationYears = clampNumber(
      state.amortizationYears,
      LOAN_TYPES.mortgage.minYears,
      insuredCap
    );
  } else {
    const loanMeta = LOAN_TYPES[state.loanType];
    state.loanAmount = clampNumber(state.loanAmount, 0);
    state.amortizationYears = clampNumber(state.amortizationYears, loanMeta.minYears, loanMeta.maxYears);
  }
}

function syncFormFromState() {
  const loanMeta = LOAN_TYPES[state.loanType];
  const maxYears = state.loanType === "mortgage"
    ? (state.downPaymentPercent < 20 ? (state.firstTimeBuyer || state.newBuild ? 30 : 25) : 30)
    : loanMeta.maxYears;
  const minYears = loanMeta.minYears;

  rebuildAmortizationOptions(minYears, maxYears, state.amortizationYears);

  refs.loanType.value = state.loanType;
  refs.paymentFrequency.value = state.paymentFrequency;
  refs.interestRate.value = formatInputNumber(state.interestRate);
  refs.amortizationYears.value = String(state.amortizationYears);
  refs.homePrice.value = formatInputNumber(roundTo(state.homePrice, 2));
  refs.downPaymentAmount.value = formatInputNumber(roundTo(state.downPaymentAmount, 2));
  refs.downPaymentPercent.value = formatInputNumber(roundTo(state.downPaymentPercent, 4));
  refs.firstTimeBuyer.checked = state.firstTimeBuyer;
  refs.newBuild.checked = state.newBuild;
  refs.loanAmount.value = formatInputNumber(roundTo(state.loanAmount, 2));
  refs.extraPayment.value = formatInputNumber(roundTo(state.extraPayment, 2));
  refs.annualLumpSum.value = formatInputNumber(roundTo(state.annualLumpSum, 2));
}

function rebuildAmortizationOptions(minYears, maxYears, selectedYears) {
  refs.amortizationYears.innerHTML = "";

  for (let year = minYears; year <= maxYears; year += 1) {
    const option = document.createElement("option");
    option.value = String(year);
    option.textContent = `${year} years`;
    if (year === selectedYears) {
      option.selected = true;
    }
    refs.amortizationYears.append(option);
  }
}

function downloadCsv() {
  if (!currentMetrics) {
    return;
  }

  const header = [
    "Period",
    "Year",
    "Payment",
    "Extra Per Period",
    "Annual Lump Sum",
    "Principal",
    "Interest",
    "Ending Balance",
  ];
  const rows = currentMetrics.schedule.rows.map((row) => [
    row.period,
    row.year,
    row.payment,
    row.extraPerPeriod,
    row.lumpSum,
    row.principal,
    row.interest,
    row.balance,
  ]);
  const csv = [header, ...rows]
    .map((row) => row.map((value) => `"${String(value)}"`).join(","))
    .join("\n");

  downloadBlob(csv, "text/csv;charset=utf-8;", `${state.loanType}-schedule.csv`);
}

function downloadPdf() {
  if (!currentMetrics) {
    return;
  }

  if (!window.jspdf || typeof window.jspdf.jsPDF !== "function") {
    window.alert("jsPDF did not load. Check your connection and try again.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "pt", format: "a4" });

  if (typeof doc.autoTable !== "function") {
    window.alert("autoTable did not load. Check your connection and try again.");
    return;
  }

  const accent = [29, 75, 69];
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 40;

  doc.setFillColor(...accent);
  doc.rect(0, 0, pageWidth, 18, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(...accent);
  doc.text("Canadian Loan Summary", margin, 54);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(88, 94, 98);
  doc.text("Estimate only. Review lender-specific details before making decisions.", margin, 72);

  const inputRows = buildPdfInputRows();
  doc.autoTable({
    startY: 92,
    head: [["Input", "Value"]],
    body: inputRows,
    theme: "plain",
    headStyles: {
      fillColor: [220, 239, 235],
      textColor: accent,
      fontStyle: "bold",
    },
    bodyStyles: {
      textColor: [36, 40, 44],
      fontSize: 10,
    },
    margin: { left: margin, right: margin },
  });

  const summaryStartY = doc.lastAutoTable.finalY + 20;
  doc.autoTable({
    startY: summaryStartY,
    head: [["Year", "Payments", "Principal", "Interest", "Ending Balance"]],
    body: currentMetrics.yearlySummary.map((row) => [
      `Year ${row.year}`,
      formatMoney(row.payments),
      formatMoney(row.principal),
      formatMoney(row.interest),
      formatMoney(row.balance),
    ]),
    theme: "striped",
    headStyles: {
      fillColor: accent,
      textColor: [255, 255, 255],
    },
    bodyStyles: {
      fontSize: 10,
      textColor: [36, 40, 44],
    },
    alternateRowStyles: {
      fillColor: [248, 245, 239],
    },
    margin: { left: margin, right: margin },
  });

  doc.save(`${state.loanType}-summary.pdf`);
}

function buildPdfInputRows() {
  const rows = [
    ["Loan type", LOAN_TYPES[state.loanType].label],
    ["Payment frequency", FREQUENCIES[state.paymentFrequency].label],
    ["Interest rate", formatPercent(state.interestRate)],
    ["Amortization", `${state.amortizationYears} years`],
  ];

  if (state.loanType === "mortgage") {
    rows.push(["Home price", formatMoney(state.homePrice)]);
    rows.push(["Down payment", `${formatMoney(state.downPaymentAmount)} (${formatPercent(state.downPaymentPercent)})`]);
    rows.push(["Financed principal", formatMoney(currentMetrics.principal)]);
    rows.push(["CMHC premium", formatMoney(currentMetrics.mortgage.cmhcPremium)]);
    rows.push(["Stress test rate", formatPercent(currentMetrics.mortgage.qualifyingRate)]);
  } else {
    rows.push(["Loan amount", formatMoney(state.loanAmount)]);
  }

  rows.push(["Extra payment per period", formatMoney(state.extraPayment)]);
  rows.push(["Annual lump sum", formatMoney(state.annualLumpSum)]);
  rows.push(["Regular payment", formatMoney(currentMetrics.schedule.regularPayment)]);
  rows.push(["Total interest", formatMoney(currentMetrics.schedule.totalInterest)]);
  rows.push(["Interest savings", formatMoney(currentMetrics.savings.interestSaved)]);

  return rows;
}

function resetCalculator() {
  state = createDefaultState();
  syncFormFromState();
  render();
}

function createDefaultState() {
  return {
    loanType: "mortgage",
    paymentFrequency: "monthly",
    interestRate: 5.25,
    amortizationYears: 25,
    homePrice: 650000,
    downPaymentAmount: 65000,
    downPaymentPercent: 10,
    downPaymentMode: "amount",
    loanAmount: 28000,
    extraPayment: 0,
    annualLumpSum: 0,
    firstTimeBuyer: false,
    newBuild: false,
    tableView: "summary",
  };
}

function downloadBlob(content, type, filename) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(value || 0);
}

function formatPercent(value) {
  const safe = Number.isFinite(value) ? value : 0;
  return `${safe.toFixed(safe % 1 === 0 ? 0 : 2)}%`;
}

function formatDuration(periods, periodsPerYear) {
  if (!periodsPerYear || !periods) {
    return "0";
  }

  const months = Math.round((periods / periodsPerYear) * 12);
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;

  if (years && remainingMonths) {
    return `${years}y ${remainingMonths}m`;
  }

  if (years) {
    return `${years}y`;
  }

  return `${remainingMonths}m`;
}

function formatInputNumber(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return String(roundTo(value, 4));
}

function roundTo(value, digits) {
  const factor = 10 ** digits;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

function clampNumber(value, min = 0, max = Number.POSITIVE_INFINITY) {
  const number = Number.parseFloat(value);
  if (Number.isNaN(number)) {
    return min;
  }
  return Math.min(Math.max(number, min), max);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
