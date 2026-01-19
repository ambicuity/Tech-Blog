---
layout: page
icon: fas fa-envelope
order: 3
title: Newsletter
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
    
    // REPLACE THIS URL with your actual Namecheap VPS URL
    const API_URL = 'https://YOUR_VPS_DOMAIN.com/subscribe.php'; 

    btn.disabled = true;
    btn.innerText = 'Sending...';
    msg.innerText = '';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (response.ok) {
            msg.style.color = '#4caf50'; // Green
            msg.innerText = '✅ ' + data.message;
            document.getElementById('email').value = '';
            document.getElementById('form-title').innerText = 'Welcome Aboard! 🚀';
        } else {
            throw new Error(data.message || 'Subscription failed');
        }
    } catch (error) {
        msg.style.color = '#ff5252'; // Red
        msg.innerText = '❌ Error: ' + error.message;
        
        if (API_URL.includes('YOUR_VPS_DOMAIN')) {
             msg.innerText = '❌ Configuration Error: Please update the API URL in subscribe.md';
        }
    } finally {
        btn.disabled = false;
        btn.innerText = 'Subscribe';
    }
});
</script>

> **Note:** Access the [Archive](/archives/) to read past issues.
