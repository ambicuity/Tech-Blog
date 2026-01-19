---
layout: page
icon: fas fa-envelope
order: 6
title: Newsletter
permalink: /newsletter/
---

## 📩 Software Engineering Weekly

Join 1,000+ engineers receiving my weekly insights on:

- 🐳 **Kubernetes & Cloud Native**
- 🐍 **Python & Scalable Architecture**
- 🔧 **DevOps Best Practices**
- 💡 **Career Growth for Engineers**

No spam, just code and architecture. Unsubscribe at any time.

---

<div id="newsletter-form" style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
    <h3 id="form-title">Join the Inner Circle</h3>
    <br>
    
    <form id="subscribeForm">
        <input type="email" id="email" placeholder="email@address.com" required style="padding: 12px; width: 60%; border-radius: 4px; border: 1px solid #555; background: #222; color: #fff; margin-right: 10px;">
        <button type="submit" id="submitBtn" style="padding: 12px 25px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background 0.3s;">Subscribe</button>
    </form>
    
    <div id="message" style="margin-top: 15px; font-weight: bold; min-height: 24px;"></div>
    
    <p style="margin-top: 1rem; font-size: 0.8em; opacity: 0.6;">Hosted on Private Infrastructure</p>
</div>

<script>
document.getElementById('subscribeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const btn = document.getElementById('submitBtn');
    const msg = document.getElementById('message');
    
    // ⚠️ IMPORTANT: Replace with your actual VPS URL
    // e.g., 'https://api.yourdomain.com/subscribe.php'
    const API_URL = 'https://riteshrana.engineer/subscribe.php'; 

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    msg.innerText = '';
    
    // Check if user forgot to update the URL
    if (API_URL.includes('YOUR_VPS_DOMAIN')) {

        msg.style.color = '#ff9800';
        msg.innerText = '⚠️ Setup Required: Please update the API URL in subscribe.md';
        btn.disabled = false;
        btn.innerText = 'Subscribe';
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        });
        
        let data;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await response.json();
        } else {
             // Handle non-JSON response gracefully
             const text = await response.text();
             console.error("Non-JSON response:", text);
             throw new Error("Server returned an unexpected response.");
        }

        if (response.ok) {
            msg.style.color = '#4caf50';
            msg.innerText = '✅ ' + (data.message || 'Subscribed successfully!');
            document.getElementById('email').value = '';
            document.getElementById('form-title').innerText = 'Welcome Aboard! 🚀';
        } else {
            throw new Error(data.message || 'Subscription failed');
        }
    } catch (error) {
        msg.style.color = '#ff5252';
        msg.innerText = '❌ Error: ' + error.message;
        console.error('Subscription Error:', error);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Subscribe';
    }
});
</script>

> **Note:** Access the [Archive](/archives/) to read past issues.
