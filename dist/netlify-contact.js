/* Netlify handles submissions on the deployed site; never simulate receipt. */
(() => {
  const form = document.getElementById("enquiry-form");
  if (!form) return;
  const button = form.querySelector('button[type="submit"]');
  const status = document.getElementById("form-status");
  let submitting = false;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submitting || !form.reportValidity()) return;
    submitting = true;
    button.disabled = true;
    button.textContent = "Sending…";
    form.setAttribute("aria-busy", "true");
    status.textContent = "Sending your enquiry…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const data = new FormData(form);
      data.set("form-name", "contact");
      const response = await fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(data).toString(),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error("Submission was not accepted");
      form.reset();
      status.textContent = "Thank you. Your enquiry has been submitted to Crownwing.";
    } catch (_error) {
      status.textContent = "We couldn’t send your enquiry. Please try again or email Crownwing using the contact details on this page.";
    } finally {
      clearTimeout(timeout);
      submitting = false;
      button.disabled = false;
      button.textContent = "Send enquiry";
      form.removeAttribute("aria-busy");
    }
  });
})();