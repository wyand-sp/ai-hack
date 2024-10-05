// Listen for the content from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Check if the message contains the page content
    if (message.content) {
        // Send the content to your API endpoint
        fetch('https://aibudy.tabcrunch.com/consume_browser', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: sender.tab.url,   // Send the URL of the page
                content: message.content  // Send the HTML content of the page
            })
        })
        .then(response => response.json())
        .then(data => console.log("Data sent successfully:", data))
        .catch(error => console.error("Error sending data:", error));
    }
});

// Listen for tab updates (when a user navigates or refreshes a page)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // We check if the page is fully loaded
    if (changeInfo.status === 'complete' && /^http/.test(tab.url)) {
        // Inject content script to capture page content
        chrome.scripting.executeScript({
            target: {tabId: tabId},
            function: capturePageContent
        });
    }
});

// Function to capture page content and send it to the API
function capturePageContent() {
    // Get the entire HTML content of the page
    const pageContent = document.body.innerText;

    // Send the captured content back to the background script
    chrome.runtime.sendMessage({content: pageContent});
}
