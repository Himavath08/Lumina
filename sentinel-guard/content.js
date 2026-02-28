chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "showWarning") {

        const overlay = document.createElement("div");
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.backgroundColor = "rgba(0,0,0,0.85)";
        overlay.style.color = "white";
        overlay.style.zIndex = "999999";
        overlay.style.display = "flex";
        overlay.style.flexDirection = "column";
        overlay.style.alignItems = "center";
        overlay.style.justifyContent = "center";
        overlay.style.fontSize = "20px";
        overlay.innerHTML = `
            <h1>⚠️ Suspicious Website Detected</h1>
            <p>This page may be a phishing attempt.</p>
            <p><strong>Reasons:</strong></p>
            <ul>
                ${message.reasons.map(r => `<li>${r}</li>`).join("")}
            </ul>
            <button id="proceedBtn" style="padding:10px 20px; margin-top:20px;">
                I Understand the Risk
            </button>
        `;

        document.body.appendChild(overlay);

        document.getElementById("proceedBtn").onclick = () => {
            overlay.remove();
        };
    }
})