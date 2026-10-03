const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("dist/netlify-contact.js", "utf8");

function harness(fetchImpl, valid = true) {
  const button = { disabled: false, textContent: "Send enquiry" };
  const status = { textContent: "" };
  const calls = [];
  let submit, timer, resets = 0;
  const fields = new Map([
    ["form-name", "contact"], ["bot-field", ""], ["name", "QA Test"],
    ["email", "qa@example.invalid"], ["species", "African Grey Parrots"],
    ["message", "Care & housing + costs? café"],
  ]);
  const form = {
    fields,
    querySelector: () => button,
    reportValidity: () => valid,
    addEventListener: (type, fn) => { assert.equal(type, "submit"); submit = fn; },
    setAttribute: (key, value) => { form[key] = value; },
    removeAttribute: (key) => { delete form[key]; },
    reset: () => { resets++; },
  };
  class FormData extends Map {
    constructor(target) { super(target.fields); }
  }
  vm.runInNewContext(source, {
    document: { getElementById: (id) => id === "enquiry-form" ? form : status },
    FormData, URLSearchParams, AbortController,
    fetch: async (...args) => { calls.push(args); return fetchImpl(...args); },
    setTimeout: (fn) => { timer = fn; return 1; },
    clearTimeout: () => { timer = null; },
  });
  return {
    button, status, calls, form,
    submit: () => submit({ preventDefault() {} }),
    timeout: () => timer(),
    resets: () => resets,
    hasTimer: () => timer !== null,
  };
}

(async () => {
  const success = harness(async () => ({ ok: true }));
  await success.submit();
  assert.equal(success.calls.length, 1);
  const [url, options] = success.calls[0];
  assert.equal(url, "/");
  assert.equal(options.method, "POST");
  assert.equal(options.headers["Content-Type"], "application/x-www-form-urlencoded");
  const data = new URLSearchParams(options.body);
  for (const [name, value] of success.form.fields) assert.equal(data.get(name), value);
  assert.match(success.status.textContent, /submitted to Crownwing/);
  assert.equal(success.resets(), 1);
  assert.equal(success.button.disabled, false);
  assert.equal(success.button.textContent, "Send enquiry");
  assert.equal(success.form["aria-busy"], undefined);
  assert.equal(success.hasTimer(), false);

  for (const failure of [
    async () => ({ ok: false, status: 404 }),
    async () => ({ ok: false, status: 405 }),
    async () => ({ ok: false, status: 500 }),
    async () => { throw new Error("Offline"); },
  ]) {
    const failed = harness(failure);
    await failed.submit();
    assert.match(failed.status.textContent, /couldn’t send/);
    assert.equal(failed.resets(), 0, "Failed enquiries must retain entered details");
    assert.equal(failed.button.disabled, false);
    assert.equal(failed.hasTimer(), false);
    await failed.submit();
    assert.equal(failed.calls.length, 2, "Retry must remain possible");
  }

  let release;
  const pending = harness(() => new Promise((resolve) => { release = resolve; }));
  const first = pending.submit();
  assert.equal(pending.button.disabled, true);
  assert.equal(pending.form["aria-busy"], "true");
  await pending.submit();
  assert.equal(pending.calls.length, 1, "Prevent simultaneous duplicate submissions");
  release({ ok: true });
  await first;
  assert.equal(pending.button.disabled, false);

  const invalid = harness(async () => ({ ok: true }), false);
  await invalid.submit();
  assert.equal(invalid.calls.length, 0);
  assert.equal(invalid.resets(), 0);

  const timeout = harness((_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener("abort", () => reject(new Error("Timed out")));
  }));
  const waiting = timeout.submit();
  timeout.timeout();
  await waiting;
  assert.match(timeout.status.textContent, /couldn’t send/);
  assert.equal(timeout.resets(), 0);
  assert.equal(timeout.button.disabled, false);

  vm.runInNewContext(source, { document: { getElementById: () => null } });
  console.log("Netlify submission tests passed: encoding, success, HTTP errors, offline, retry, duplicates, validation, timeout and no-form pages.");
})().catch((error) => { console.error(error); process.exitCode = 1; });