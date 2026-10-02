(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  }
  if (typeof document !== "undefined") {
    api.initBuyerTools(document);
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const REQUIRED_BUDGET_FIELDS = [
    "purchase",
    "cage",
    "initialEquipment",
    "transport",
    "food",
    "toys",
    "veterinarySaving",
    "emergencyReserve",
  ];
  const ALL_BUDGET_FIELDS = REQUIRED_BUDGET_FIELDS.concat("insurance");

  function readPence(value, field, required) {
    if (value === undefined || value === null || (typeof value === "string" && value.trim() === "")) {
      return required ? { error: `${field} is required.` } : { pence: 0 };
    }
    if (typeof value !== "number" && typeof value !== "string") {
      return { error: `${field} must be a finite amount of £0.00 or more.` };
    }
    const amount = typeof value === "number" ? value : Number(value);
    if (!Number.isFinite(amount)) {
      return { error: `${field} must be a finite amount of £0.00 or more.` };
    }
    if (amount < 0) {
      return { error: `${field} cannot be negative.` };
    }
    const pence = Math.round(amount * 100);
    if (!Number.isSafeInteger(pence)) {
      return { error: `${field} is too large for an accurate pounds-and-pence calculation.` };
    }
    if (Math.abs(amount * 100 - pence) > 1e-7) {
      return { error: `${field} must use increments of £0.01.` };
    }
    return { pence };
  }

  function calculateBudget(values) {
    if (!values || typeof values !== "object") {
      return { valid: false, errors: ["Enter your estimates before calculating."] };
    }
    const amounts = {};
    const errors = [];
    ALL_BUDGET_FIELDS.forEach((field) => {
      const result = readPence(values[field], field, REQUIRED_BUDGET_FIELDS.includes(field));
      if (result.error) errors.push(result.error);
      else amounts[field] = result.pence;
    });
    if (errors.length) return { valid: false, errors };

    const setupPence = amounts.purchase + amounts.cage + amounts.initialEquipment + amounts.transport;
    const monthlyPence = amounts.food + amounts.toys + amounts.veterinarySaving + amounts.insurance;
    const reservePence = amounts.emergencyReserve;
    return {
      valid: true,
      totals: {
        setupSpend: setupPence / 100,
        monthlyOngoing: monthlyPence / 100,
        firstYearPlannedSpend: (setupPence + monthlyPence * 12) / 100,
        startingCash: (setupPence + reservePence) / 100,
        emergencyReserve: reservePence / 100,
      },
    };
  }

  function validateComparisonSelection(selected) {
    if (!Array.isArray(selected) || selected.length !== 2 || !selected[0] || !selected[1]) {
      return { valid: false, message: "Choose two parrot groups to compare." };
    }
    if (selected[0] === selected[1]) {
      return { valid: false, message: "Choose two different groups to compare." };
    }
    return { valid: true, message: "Showing the two selected groups." };
  }

  function formatGBP(value) {
    return new Intl.NumberFormat("en-GB", {
      style: "currency",
      currency: "GBP",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  }

  function initComparison(documentRef) {
    const section = documentRef.getElementById("group-comparison");
    if (!section) return;
    const controls = section.querySelector(".comparison-controls");
    const first = section.querySelector("#comparison-first");
    const second = section.querySelector("#comparison-second");
    const message = section.querySelector("[data-comparison-message]");
    const showButton = section.querySelector("[data-comparison-show]");
    const resetButton = section.querySelector("[data-comparison-reset]");
    if (!controls || !first || !second || !showButton || !resetButton) return;

    controls.hidden = false;
    function reset() {
      section.querySelectorAll("[data-group]").forEach((cell) => {
        cell.hidden = false;
      });
      first.value = "";
      second.value = "";
      message.textContent = "Showing all eight groups.";
    }
    showButton.addEventListener("click", function () {
      const selection = validateComparisonSelection([first.value, second.value]);
      if (!selection.valid) {
        message.textContent = selection.message;
        return;
      }
      const visible = new Set([first.value, second.value]);
      section.querySelectorAll("[data-group]").forEach((cell) => {
        cell.hidden = !visible.has(cell.getAttribute("data-group"));
      });
      message.textContent = `Showing ${first.options[first.selectedIndex].text} and ${second.options[second.selectedIndex].text}.`;
    });
    resetButton.addEventListener("click", reset);
    first.addEventListener("change", function () {
      message.textContent = "";
    });
    second.addEventListener("change", function () {
      message.textContent = "";
    });
  }

  function initBudget(documentRef) {
    const form = documentRef.querySelector("[data-budget-form]");
    const results = documentRef.querySelector("[data-budget-results]");
    const error = documentRef.querySelector("[data-budget-error]");
    if (!form || !results || !error) return;

    form.noValidate = false;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      error.textContent = "";
      results.hidden = true;
      if (!form.reportValidity()) return;

      const values = {};
      ALL_BUDGET_FIELDS.forEach((field) => {
        const input = form.elements.namedItem(field);
        values[field] = input ? input.value : undefined;
      });
      const calculation = calculateBudget(values);
      if (!calculation.valid) {
        error.textContent = calculation.errors.join(" ");
        return;
      }
      Object.keys(calculation.totals).forEach((key) => {
        const output = results.querySelector(`[data-result="${key}"]`);
        if (output) output.textContent = formatGBP(calculation.totals[key]);
      });
      results.hidden = false;
    });

    form.addEventListener("reset", function () {
      error.textContent = "";
      results.hidden = true;
      results.querySelectorAll("[data-result]").forEach((output) => {
        output.textContent = "—";
      });
    });

    form.addEventListener("input", function () {
      if (error.textContent) error.textContent = "";
    });
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = false;
  }

  function initBuyerTools(documentRef) {
    initComparison(documentRef);
    initBudget(documentRef);
  }

  return {
    calculateBudget,
    validateComparisonSelection,
    initBuyerTools,
  };
});