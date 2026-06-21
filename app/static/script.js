const form = document.getElementById("shorten-form");
const urlInput = document.getElementById("target-url");
const resultDiv = document.getElementById("result");
const errorDiv = document.getElementById("error");
const shortLinkEl = document.getElementById("short-link");
const clickCountEl = document.getElementById("click-count");
const copyBtn = document.getElementById("copy-btn");
const refreshBtn = document.getElementById("refresh-btn");

let currentShortCode = null;

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    resultDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");

    const targetUrl = urlInput.value.trim();

    try {
        const response = await fetch("/shorten", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target_url: targetUrl }),
        });

        if (!response.ok) {
            if (response.status === 429) {
                throw new Error("Too many requests — please wait a minute and try again.");
            }
            throw new Error("Something went wrong. Please check the URL and try again.");
        }

        const data = await response.json();

        const shortUrl = `${window.location.origin}/${data.short_code}`;
        shortLinkEl.textContent = shortUrl;
        shortLinkEl.href = shortUrl;
        clickCountEl.textContent = data.total_clicks;
        currentShortCode = data.short_code;

        resultDiv.classList.remove("hidden");
        urlInput.value = "";
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove("hidden");
    }
});

copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(shortLinkEl.href).then(() => {
        copyBtn.textContent = "Copied!";
        setTimeout(() => {
            copyBtn.textContent = "Copy";
        }, 1500);
    });
});

refreshBtn.addEventListener("click", async () => {
    if (!currentShortCode) return;

    try {
        const response = await fetch(`/${currentShortCode}/stats`);
        const data = await response.json();
        clickCountEl.textContent = data.total_clicks;

        refreshBtn.textContent = "✓ Updated";
        setTimeout(() => {
            refreshBtn.textContent = "⟳ Refresh";
        }, 1200);
    } catch (err) {
        console.error("Failed to refresh stats", err);
    }
});