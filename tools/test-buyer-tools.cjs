const assert = require("node:assert/strict");
const { calculateBudget, validateComparisonSelection } = require("../site/buyer-tools.js");

const complete = {
  purchase: "100.25",
  cage: "200.50",
  initialEquipment: "25.25",
  transport: "10",
  food: "12.50",
  toys: "7.25",
  veterinarySaving: "20",
  insurance: "0",
  emergencyReserve: "300",
};

function test(name, fn) {
  try {
    fn();
    console.log(`ok - ${name}`);
  } catch (error) {
    console.error(`not ok - ${name}`);
    throw error;
  }
}

test("required blank fields are invalid rather than treated as free", () => {
  const result = calculateBudget({ ...complete, purchase: "" });
  assert.equal(result.valid, false);
  assert.match(result.errors.join(" "), /purchase is required/i);
});

test("all required fields must be supplied", () => {
  const { food, ...missingFood } = complete;
  const result = calculateBudget(missingFood);
  assert.equal(result.valid, false);
  assert.match(result.errors.join(" "), /food is required/i);
});

test("Infinity and non-finite values are rejected", () => {
  for (const value of ["Infinity", Infinity, NaN]) {
    assert.equal(calculateBudget({ ...complete, cage: value }).valid, false);
  }
});

test("negative amounts are rejected", () => {
  const result = calculateBudget({ ...complete, toys: "-0.01" });
  assert.equal(result.valid, false);
  assert.match(result.errors.join(" "), /cannot be negative/i);
});

test("zero and valid pence increments are accepted", () => {
  const result = calculateBudget({
    purchase: "0",
    cage: "0.01",
    initialEquipment: "0",
    transport: "0",
    food: "0",
    toys: "0.02",
    veterinarySaving: "0",
    insurance: "",
    emergencyReserve: "0",
  });
  assert.equal(result.valid, true);
  assert.deepEqual(result.totals, {
    setupSpend: 0.01,
    monthlyOngoing: 0.02,
    firstYearPlannedSpend: 0.25,
    startingCash: 0.01,
    emergencyReserve: 0,
  });
});

test("amounts beyond penny precision are rejected", () => {
  assert.equal(calculateBudget({ ...complete, food: "1.001" }).valid, false);
});

test("setup, monthly and first-year estimates sum correctly", () => {
  const result = calculateBudget(complete);
  assert.equal(result.valid, true);
  assert.deepEqual(result.totals, {
    setupSpend: 336,
    monthlyOngoing: 39.75,
    firstYearPlannedSpend: 813,
    startingCash: 636,
    emergencyReserve: 300,
  });
});

test("the emergency reserve is ring-fenced, added to starting cash, and excluded from planned spend", () => {
  const withoutReserve = calculateBudget({ ...complete, emergencyReserve: "0" });
  const withReserve = calculateBudget(complete);
  assert.equal(withReserve.totals.emergencyReserve, 300);
  assert.equal(withReserve.totals.startingCash - withoutReserve.totals.startingCash, 300);
  assert.equal(withReserve.totals.firstYearPlannedSpend, withoutReserve.totals.firstYearPlannedSpend);
});

test("insurance is optional and defaults to zero when omitted", () => {
  const { insurance, ...noInsurance } = complete;
  const result = calculateBudget(noInsurance);
  assert.equal(result.valid, true);
  assert.equal(result.totals.monthlyOngoing, 39.75);
});

test("comparison selection requires two different groups", () => {
  assert.equal(validateComparisonSelection([]).valid, false);
  assert.equal(validateComparisonSelection(["macaws", ""]).valid, false);
  assert.equal(validateComparisonSelection(["macaws", "macaws"]).valid, false);
  assert.equal(validateComparisonSelection(["macaws", "caiques"]).valid, true);
});

console.log("Buyer tool tests passed.");