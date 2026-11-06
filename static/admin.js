const STATUSES = ["Pending Payment", "Paid", "In Making", "Shipped", "Delivered", "Cancelled"];

const ordersBox = document.getElementById("orders");
const ordersEmpty = document.getElementById("orders-empty");
const statusFilter = document.getElementById("status-filter");
const productsBox = document.getElementById("admin-products");
const categorySelect = document.getElementById("p-category");
const productForm = document.getElementById("product-form");
const productMsg = document.getElementById("product-msg");

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function el(tag, className, text) {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (text !== undefined) e.textContent = text;
  return e;
}

/* ---------- Orders ---------- */

function renderOrder(o) {
  const card = el("div", "order-card");

  const head = el("div", "order-head");
  head.appendChild(el("strong", "", "Order #" + o.id));
  head.appendChild(
    el("span", "badge " + (o.payment_status === "Paid" ? "paid" : "unpaid"), o.payment_status)
  );
  card.appendChild(head);

  const c = o.customer || {};
  card.appendChild(el("p", "", c.name + " | " + c.phone));
  card.appendChild(el("p", "muted", o.delivery_address || ""));

  const list = el("ul", "items");
  o.items.forEach((i) => {
    const li = el("li", "", i.product_name + " x " + i.quantity + " (₹" + i.price + ")");
    if (i.customization_note) {
      li.appendChild(el("div", "note", "Note: " + i.customization_note));
    }
    list.appendChild(li);
  });
  card.appendChild(list);

  card.appendChild(
    el("p", "", "Total: ₹" + o.total_amount + " | Expected delivery: " + (o.expected_delivery || "-"))
  );
  if (o.upi_reference) {
    card.appendChild(el("p", "muted", "UPI ref: " + o.upi_reference));
  }

  const actions = el("div", "actions");

  const sel = el("select");
  STATUSES.forEach((s) => {
    const opt = el("option", "", s);
    opt.value = s;
    if (s === o.status) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.onchange = async () => {
    try {
      await api("PUT", "/api/orders/" + o.id + "/status", { status: sel.value });
      loadOrders();
    } catch (e) {
      alert(e.message);
    }
  };
  actions.appendChild(sel);

  if (o.payment_status !== "Paid") {
    const btn = el("button", "btn", "Mark Paid");
    btn.onclick = async () => {
      const ref = prompt("UPI reference number (optional):");
      if (ref === null) return;
      try {
        await api("PUT", "/api/orders/" + o.id + "/payment", { upi_reference: ref });
        loadOrders();
      } catch (e) {
        alert(e.message);
      }
    };
    actions.appendChild(btn);
  }

  card.appendChild(actions);
  return card;
}

async function loadOrders() {
  const q = statusFilter.value ? "?status=" + encodeURIComponent(statusFilter.value) : "";
  const orders = await api("GET", "/api/orders" + q);

  ordersBox.innerHTML = "";
  ordersEmpty.hidden = orders.length > 0;
  orders.forEach((o) => ordersBox.appendChild(renderOrder(o)));
}

/* ---------- Products ---------- */

async function loadCategories() {
  const cats = await api("GET", "/api/categories");
  categorySelect.innerHTML = "";
  cats.forEach((c) => {
    const opt = el("option", "", c.name);
    opt.value = c.id;
    categorySelect.appendChild(opt);
  });
}

async function loadProducts() {
  const products = await api("GET", "/api/products");
  productsBox.innerHTML = "";

  products.forEach((p) => {
    const row = el("div", "prod-row");

    const info = el("div", "prod-info");
    info.appendChild(el("strong", "", p.name));
    info.appendChild(el("div", "muted", p.category + " | ₹" + p.price));
    row.appendChild(info);

    row.appendChild(
      el("span", "badge " + (p.is_available ? "paid" : "unpaid"),
         p.is_available ? "Available" : "Unavailable")
    );

    const toggle = el("button", "btn gray", p.is_available ? "Make Unavailable" : "Make Available");
    toggle.onclick = async () => {
      try {
        await api("PUT", "/api/products/" + p.id, { is_available: !p.is_available });
        loadProducts();
      } catch (e) {
        alert(e.message);
      }
    };
    row.appendChild(toggle);

    const del = el("button", "btn danger", "Delete");
    del.onclick = async () => {
      if (!confirm("Delete " + p.name + "?")) return;
      try {
        const data = await api("DELETE", "/api/products/" + p.id);
        alert(data.message);
        loadProducts();
      } catch (e) {
        alert(e.message);
      }
    };
    row.appendChild(del);

    productsBox.appendChild(row);
  });
}

productForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  productMsg.textContent = "";
   const fd = new FormData(productForm);

  try {
    let imageUrl = null;
    const file = fd.get("image");
    if (file && file.size > 0) {
      const upData = new FormData();
      upData.append("image", file);
      const upRes = await fetch("/api/upload", { method: "POST", body: upData });
      const upJson = await upRes.json();
      if (!upRes.ok) throw new Error(upJson.error || "Upload failed");
      imageUrl = upJson.url;
    }

    await api("POST", "/api/products", {
      name: fd.get("name").trim(),
      category_id: parseInt(fd.get("category_id"), 10),
      price: parseFloat(fd.get("price")),
      description: fd.get("description").trim(),
      image_url: imageUrl,
    });
    productForm.reset();
    productMsg.textContent = "Product added!";
    loadProducts();
  } catch (err) {
    productMsg.textContent = err.message;
  }
});

/* ---------- Start ---------- */

function setupFilter() {
  const all = el("option", "", "All orders");
  all.value = "";
  statusFilter.appendChild(all);
  STATUSES.forEach((s) => {
    const opt = el("option", "", s);
    opt.value = s;
    statusFilter.appendChild(opt);
  });
  statusFilter.onchange = loadOrders;
}

setupFilter();
loadCategories();
loadProducts();
loadOrders();