const form = document.getElementById("upload-form");
const imageInput = document.getElementById("image");
const cityInput = document.getElementById("city");
const preview = document.getElementById("preview");
const loading = document.getElementById("loading");
const dropZone = document.getElementById("drop-zone");

// Restore previous city
cityInput.value = localStorage.getItem("userCity") || "";

// 🌿 DRAG & DROP UPLOAD
dropZone.addEventListener("click", () => imageInput.click());

["dragenter", "dragover"].forEach(event => {
  dropZone.addEventListener(event, e => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add("drag-over");
  });
});

["dragleave", "drop"].forEach(event => {
  dropZone.addEventListener(event, e => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove("drag-over");
  });
});

dropZone.addEventListener("drop", e => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    imageInput.files = e.dataTransfer.files;
    showPreview(file);
  } else {
    alert("Please drop a valid image file.");
  }
});

imageInput.addEventListener("change", e => {
  const file = e.target.files[0];
  if (file) showPreview(file);
});

function showPreview(file) {
  preview.src = URL.createObjectURL(file);
  document.getElementById("preview-card").classList.remove("hidden");
}

// 🌱 FORM SUBMISSION
form.addEventListener("submit", async e => {
  e.preventDefault();

  const file = imageInput.files[0];
  const city = cityInput.value.trim();

  if (!file) return alert("Please select or drop an image!");
  if (!city) return alert("Please enter your city!");

  localStorage.setItem("userCity", city);

  // Reset & show loading
  loading.classList.add("hidden");
  loading.innerHTML = `Analyzing<span class="dots"></span>`;
  animateDots();

  ["weather-card", "disease-card", "advice-card"].forEach(id =>
    document.getElementById(id).classList.add("hidden")
  );

  const formData = new FormData();
  formData.append("image", file);
  formData.append("city", city);

  try {
    const res = await fetch("/api/advice/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    loading.classList.add("hidden");
    console.log(data);

    // WEATHER
    if (data.weather) {
      document.getElementById("weather-card").classList.remove("hidden");
      document.getElementById("weather-content").innerHTML = `
        <b>City:</b> ${city}<br>
        <b>Temperature:</b> ${data.weather.main.temp || "N/A"} °C<br>
        <b>Condition:</b> ${data.weather.weather[0].description || "N/A"}<br>
        <b>Humidity:</b> ${data.weather.main.humidity || "N/A"}%
      `;
    }

    // DISEASE
    if (data.disease) {
      const { predicted_label, confidence, probabilities } = data.disease;
      document.getElementById("disease-card").classList.remove("hidden");
      document.getElementById("predicted_crop").innerText = data.crop || "Unknown";
      document.getElementById("predicted_label").innerText = data.disease.predicted_label || "Unknown";
      document.getElementById("confidence").innerText =
        data.disease.confidence ? `${(data.disease.confidence * 100).toFixed(2)}%` : "N/A";

      const probsDiv = document.getElementById("probabilities");
      probsDiv.innerHTML = "";
      if (probabilities) {
        for (const [label, prob] of Object.entries(probabilities)) {
          const bar = document.createElement("div");
          bar.classList.add("prob-bar");
          bar.innerHTML = `
            <div class="prob-fill" style="width:${(prob * 100).toFixed(1)}%">
              ${(prob * 100).toFixed(1)}%
            </div>
            <small>${label}</small>`;
          probsDiv.appendChild(bar);
        }
      }
    }

    // ADVICE
    if (data.advice) {
      document.getElementById("advice-card").classList.remove("hidden");
      document.getElementById("advice-text").innerText = data.advice;
    }

    // Handle partial errors gracefully
    if (data.warning) {
      alert("⚠️ Some modules failed: " + data.warning);
    }

  } catch (err) {
    console.error("❌ Error:", err);
    alert("Failed to connect to the backend. Please check your connection.");
  }
});

// 🌼 Animated dots for “Analyzing...”
function animateDots() {
  const dots = document.querySelector(".dots");
  if (!dots) return;
  let count = 0;
  setInterval(() => {
    dots.textContent = ".".repeat(count % 4);
    count++;
  }, 400);
}
