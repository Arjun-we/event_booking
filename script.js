/* ROLE SELECT → LOGIN */
function goVendorLogin() {
    window.location.href = "vendor-login.html";
}

function goCustomerLogin() {
    window.location.href = "customer-login.html";
}

/* LOGIN → DASHBOARD / VENDORS */
function vendorLogin() {
    window.location.href = "vendor-dashboard.html";
    return false;
}

function customerLogin() {
    window.location.href = "vendors.html";
    return false;
}

/* FEEDBACK NAV */
function vendorFeedback() {
    window.location.href = "vendor-feedback.html";
}

function customerFeedback() {
    window.location.href = "customer-feedback.html";
}
// chatbot.js (STATIC CHATBOT LOGIC)

function sendMessage() {
    var input = document.getElementById("userMessage");
    var msg = input.value.trim();
    if (msg === "") return;

    var chat = document.getElementById("chat-body");

    // User message
    var userDiv = document.createElement("div");
    userDiv.className = "user";
    userDiv.innerText = msg;
    chat.appendChild(userDiv);

    input.value = "";

    // Static responses
    var reply = "I can help you with vendors, bookings, and feedback.";

    msg = msg.toLowerCase();

    if (msg.includes("vendor")) {
        reply = "Vendors can manage services, view bookings, and check reviews in the Vendor Dashboard.";
    } 
    else if (msg.includes("customer")) {
        reply = "Customers can browse vendors, book services, and submit feedback.";
    }
    else if (msg.includes("book")) {
        reply = "To book a service, browse vendors and select the one you like.";
    }
    else if (msg.includes("login")) {
        reply = "Please select your role first, then login to continue.";
    }
    else if (msg.includes("feedback")) {
        reply = "Customers can submit feedback after using a vendor’s service.";
    }

    setTimeout(() => {
        var botDiv = document.createElement("div");
        botDiv.className = "bot";
        botDiv.innerText = reply;
        chat.appendChild(botDiv);
        chat.scrollTop = chat.scrollHeight;
    }, 400);
}
// ADD to script.js (SIGNUP FLOW)

function vendorSignup(){
    alert("Vendor account created successfully (Mock)");
    window.location.href = "vendor-login.html";
    return false;
}

function customerSignup(){
    alert("Customer account created successfully (Mock)");
    window.location.href = "customer-login.html";
    return false;
}
