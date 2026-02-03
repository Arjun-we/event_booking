function sendMessage(){

    

    const input = document.getElementById("userMessage");
    const message = input.value.trim();
    if(message === "") return;
        

    const chat = document.getElementById("chat-body");

    // Show user message
    chat.innerHTML += `<div class="user">${message}</div>`;
    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    // Send to backend
    fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        chat.innerHTML += `<div class="bot">${data.reply}</div>`;
        chat.scrollTop = chat.scrollHeight;
    })
    .catch(() => {
        chat.innerHTML += `<div class="bot">
            ⚠ Unable to connect to AI service.
        </div>`;
        chat.scrollTop = chat.scrollHeight;
    });
}
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("userMessage");

    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});
