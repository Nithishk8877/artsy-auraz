let currentProduct = null;

const modal = document.getElementById("order-modal");
const form = document.getElementById("order-form");
const formView = document.getElementById("form-view");
const successView = document.getElementById("success-view");
const errorBox = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");
const totalSpan = document.getElementById("order-total");

function openOrderModal(product) {
  currentProduct = product;
  form.reset();
  errorBox.textContent = "";
  document.getElementById("modal-product").textContent =
    product.name + " - ₹" + product.price;
  formView.hidden = false;
  successView.hidden = true;
  modal.hidden = false;
  updateTotal();
}

function closeOrderModal() {
  modal.hidden = true;
}

function updateTotal() {
  const qty = parseInt(form.elements["quantity"].value, 10) || 1;
  totalSpan.textContent = "₹" + currentProduct.price * qty;
}

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

form.elements["quantity"].addEventListener("input", updateTotal);
document.getElementById("modal-close").onclick = closeOrderModal;
document.getElementById("success-close").onclick = closeOrderModal;

modal.addEventListener("click", (e) => {
  if (e.target === modal) closeOrderModal();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBox.textContent = "";

  const fd = new FormData(form);
  const address = fd.get("address").trim();

  const payload = {
    customer: {
      name: fd.get("name").trim(),
      phone: fd.get("phone").trim(),
      address: address,
    },
    delivery_address: address,
    items: [
      {
        product_id: currentProduct.id,
        quantity: parseInt(fd.get("quantity"), 10),
        customization_note: fd.get("note").trim(),
      },
    ],
  };

  submitBtn.disabled = true;
  try {
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      errorBox.textContent = data.error || "Something went wrong";
      return;
    }

    document.getElementById("s-id").textContent = "#" + data.id;
    document.getElementById("s-total").textContent = "₹" + data.total_amount;
    document.getElementById("s-date").textContent = formatDate(data.expected_delivery);
    formView.hidden = true;
    successView.hidden = false;
  } catch (err) {
    errorBox.textContent = "Server not reachable. Please try again.";
  } finally {
    submitBtn.disabled = false;
  }
});