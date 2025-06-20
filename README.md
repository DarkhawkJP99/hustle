# Hustle. – AI-Powered Lead Generation Engine 🚀

![License](https://img.shields.io/badge/license-MIT-green)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/hustle)

Hustle. automates Twitter lead discovery, GPT-based scoring, Stripe payments, and branded fulfillment emails.

---

## 🔧 Quick Start

1. Click **Deploy to Render** above
2. Add your environment variables in the Render dashboard
3. Watch your AI hustle engine go live

---

## 🔐 Required Environment Variables

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `TWITTER_BEARER_TOKEN`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

---

## 🧠 Powered by:
- OpenAI GPT-4
- Stripe Checkout + Webhooks
- FastAPI
- Docker + Render Hosting

---

## 📂 Project Structure

- `ai_hustle_automator.py` – Backend engine
- `Dockerfile` – For full container support
- `render.yaml` – Render.com deploy config
- `.github/workflows/test.yml` – Syntax tests on push
