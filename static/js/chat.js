const messages = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const clearButton = document.getElementById("btn-clear");
const learnMode = document.getElementById("learn-mode");

function addMessage(sender, text) {
    const row = document.createElement("div");
    row.className = `msg msg-${sender}`;
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.textContent = text;
    row.appendChild(bubble);
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
}

async function requestJson(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || `Permintaan gagal (${response.status})`);
    }
    return data;
}

async function loadHistory() {
    try {
        const history = await requestJson(`/api/history/${encodeURIComponent(THEME.id)}`);
        if (history.length) {
            history.forEach((item) => addMessage(item.sender, item.text));
        } else {
            addMessage("bot", THEME.greeting);
        }
    } catch (error) {
        addMessage("bot", `Riwayat gagal dimuat: ${error.message}`);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage("user", message);
    input.value = "";
    try {
        const result = await requestJson("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ theme: THEME.id, message })
        });
        addMessage("bot", result.reply);
        if (learnMode?.checked) {
            const explanation = await requestJson("/api/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ theme: THEME.id, message })
            });
            const candidates = explanation.candidates
                .map((item) => `${item.intent}: ${item.score}`)
                .join("\n");
            addMessage("bot", `Kandidat intent:\n${candidates || "Tidak ada kandidat."}`);
        }
    } catch (error) {
        addMessage("bot", `Pesan gagal diproses: ${error.message}`);
    }
});

document.querySelectorAll(".chip").forEach((button) => {
    button.addEventListener("click", () => {
        input.value = button.textContent.trim();
        form.requestSubmit();
    });
});

clearButton?.addEventListener("click", async () => {
    try {
        await requestJson(`/api/history/${encodeURIComponent(THEME.id)}`, { method: "DELETE" });
        messages.replaceChildren();
        addMessage("bot", THEME.greeting);
    } catch (error) {
        addMessage("bot", `Riwayat gagal dihapus: ${error.message}`);
    }
});

loadHistory();
