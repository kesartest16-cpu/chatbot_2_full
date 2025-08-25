const API_URL = "/api/chat";
const inputEl = document.getElementById("input");
const clearEl = document.getElementById("clear");


function addMsg(text, role = "bot") {
const wrap = document.createElement("div");
wrap.className = `msg ${role}`;
wrap.textContent = text;
messagesEl.appendChild(wrap);
messagesEl.scrollTop = messagesEl.scrollHeight;
}


function addMeta(text) {
const el = document.createElement("div");
el.className = "msg meta";
el.textContent = text;
messagesEl.appendChild(el);
messagesEl.scrollTop = messagesEl.scrollHeight;
}


async function sendMessage(text) {
addMsg(text, "user");
addMeta("…");


try {
const res = await fetch(API_URL, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ message: text, session_id: sessionId }),
});
const data = await res.json();
messagesEl.lastChild.remove(); // remove meta dots
addMsg(data.reply, "bot");
} catch (e) {
messagesEl.lastChild.remove();
addMsg("⚠️ Network error. Is the server running?", "bot");
}
}


formEl.addEventListener("submit", (e) => {
e.preventDefault();
const text = inputEl.value.trim();
if (!text) return;
inputEl.value = "";
sendMessage(text);
});


clearEl.addEventListener("click", () => {
messagesEl.innerHTML = "";
});


// Greet on first load
addMsg("👋 Hi! I'm chatbot_2. You can say things like: 'help', 'my name is Alex', 'what time is it', or just 'hi'.", "bot");