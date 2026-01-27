// chatbot.js (DYNAMIC STATIC CHATBOT LOGIC)

function sendMessage(){
    var input = document.getElementById("userMessage");
    var text = input.value.trim();
    if(text === "") return;

    var chat = document.getElementById("chat-body");

    // User message
    var userDiv = document.createElement("div");
    userDiv.className = "user";
    userDiv.innerText = text;
    chat.appendChild(userDiv);

    input.value = "";

    // Bot reply logic (STATIC BUT DYNAMIC BEHAVIOR)
    var reply = "I'm here to help with event planning.";

    var msg = text.toLowerCase();

    if(msg.includes("vendor")){
        reply = "Vendors can manage services, bookings, and view reviews from the Vendor Dashboard.";
    }
    else if(msg.includes("customer")){
        reply = "Customers can browse vendors, book services, and give feedback.";
    }
    else if(msg.includes("book")){
        reply = "To book a service, go to the Vendors page and select a vendor.";
    }
    else if(msg.includes("login")){
        reply = "First select your role, then login to continue.";
    }
    else if(msg.includes("feedback")){
        reply = "Feedback helps maintain quality. Customers can submit reviews after events.";
    }
    else if(msg.includes("hello") || msg.includes("hi")){
        reply = "Hello 👋 How can I assist you today?";
    }

    setTimeout(function(){
        var botDiv = document.createElement("div");
        botDiv.className = "bot";
        botDiv.innerText = reply;
        chat.appendChild(botDiv);
        chat.scrollTop = chat.scrollHeight;
    }, 500);
}
