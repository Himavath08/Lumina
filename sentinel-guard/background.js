chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete" && tab.url) {

        fetch("http://127.0.0.1:8000/analyze-url", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: tab.url })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "suspicious") {
                chrome.tabs.sendMessage(tabId, {
                    action: "showWarning",
                    reasons: data.reasons
                });
            }
        })
        .catch(error => console.error("API error:", error));
    }
});