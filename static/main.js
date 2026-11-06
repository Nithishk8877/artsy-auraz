let selectedCategory = "";

const categoriesBox = document.getElementById("categories");
const productsBox = document.getElementById("products");
const emptyMsg = document.getElementById("empty");
const searchInput = document.getElementById("search");

async function loadCategories() {
  const res = await fetch("/api/categories");
  const categories = await res.json();

  categoriesBox.innerHTML = "";
  categoriesBox.appendChild(makeCatButton("All", ""));
  categories.forEach(c => categoriesBox.appendChild(makeCatButton(c.name, c.id)));
}

function makeCatButton(label, id) {
  const btn = document.createElement("button");
  btn.className = "cat-btn" + (String(id) === String(selectedCategory) ? " active" : "");
  btn.textContent = label;
  btn.onclick = () => {
    selectedCategory = id;
    loadCategories();
    loadProducts();
  };
  return btn;
}

async function loadProducts() {
  const params = new URLSearchParams();
  if (selectedCategory) params.append("category_id", selectedCategory);
  if (searchInput.value.trim()) params.append("search", searchInput.value.trim());

  const res = await fetch("/api/products?" + params.toString());
  const products = await res.json();

  productsBox.innerHTML = "";
  emptyMsg.hidden = products.length > 0;

  products.filter(p => p.is_available).forEach(p => {
    const card = document.createElement("div");
    card.className = "card";

    const img = document.createElement("div");
    img.className = "img";
    if (p.image_url) {
      const im = document.createElement("img");
      im.src = p.image_url;
      im.alt = p.name;
      img.appendChild(im);
    } else {
      img.textContent = "🎁";
    }

    const body = document.createElement("div");
    body.className = "body";

    const cat = document.createElement("div");
    cat.className = "cat";
    cat.textContent = p.category || "";

    const title = document.createElement("h3");
    title.textContent = p.name;

    const desc = document.createElement("p");
    desc.className = "desc";
    desc.textContent = p.description || "";

    const price = document.createElement("div");
    price.className = "price";
    price.textContent = "₹" + p.price;

        const orderBtn = document.createElement("button");
    orderBtn.className = "order-btn";
    orderBtn.textContent = "Order Now";
    orderBtn.onclick = () => openOrderModal(p);

    body.append(cat, title, desc, price, orderBtn);
    card.append(img, body);
    productsBox.appendChild(card);
  });
}

searchInput.addEventListener("input", loadProducts);

loadCategories();
loadProducts();