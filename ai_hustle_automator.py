# ai_hustle_automator.py – Hustle. v2.2
# FastAPI webhook + GPT scoring + Stripe Checkout + Email

from fastapi import FastAPI, Request, Header
import uvicorn, json, os, stripe, openai, asyncio, random, smtplib, aiohttp
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime

app = FastAPI()

TWITTER_BEARER = os.getenv("TWITTER_BEARER_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
BRAND_NAME = "Hustle."
PRODUCT_URL = "https://hustle.ai/products/ai-pack"
HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER}"}
SEARCH_QUERY = "(need OR looking) (content OR resume OR website) lang:en -is:retweet"
MIN_SCORE_FOR_DM = 0.65

openai.api_key = OPENAI_KEY
stripe.api_key = STRIPE_KEY

@app.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(...)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email", "unknown@user.com")
        print(json.dumps({"type": "order", "email": customer_email, "amount": 49.00}), flush=True)
        send_email(customer_email, f"Your {BRAND_NAME} Content is Ready", f"Download here: {PRODUCT_URL}")
    return {"status": "success"}

def send_email(to_email: str, subject: str, content_text: str):
    html = f"""<html><body><h2>Thanks for purchasing from <strong>{BRAND_NAME}</strong>!</h2>
    <p>Your content is ready. <a href='{PRODUCT_URL}'>Click here to download</a>.</p></body></html>"""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{BRAND_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg.set_content(content_text)
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(json.dumps({"type": "error", "msg": f"Email failed: {str(e)}"}), flush=True)

async def fetch_tweets():
    url = f"https://api.twitter.com/2/tweets/search/recent?query={SEARCH_QUERY}&max_results=10&tweet.fields=author_id,text"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as r:
            return (await r.json()).get("data", [])

async def gpt_score_lead(text: str) -> float:
    try:
        prompt = f"Given this tweet: '{text}', rate its business intent (0.0–1.0):"
        resp = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10, temperature=0.3
        )
        return min(1.0, max(0.0, float(resp.choices[0].message.content.strip())))
    except:
        return random.uniform(0.4, 0.6)

async def gpt_generate_dm(text: str) -> str:
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Custom AI Content'},
                'unit_amount': 4900
            },
            'quantity': 1
        }],
        mode='payment',
        success_url='https://hustle.ai/success',
        cancel_url='https://hustle.ai/cancel',
    )
    link = session.url
    prompt = f"Respond to: '{text}'. Offer $49 custom AI content. Payment link: {link}"
    resp = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=90, temperature=0.7
    )
    return resp.choices[0].message.content.strip()

async def lead_pipeline():
    tweets = await fetch_tweets()
    for tweet in tweets:
        text = tweet["text"]
        score = await gpt_score_lead(text)
        print(json.dumps({"type": "lead", "text": text, "score": score}), flush=True)
        if score >= MIN_SCORE_FOR_DM:
            dm = await gpt_generate_dm(text)
            await asyncio.sleep(random.uniform(1, 2))
            print(json.dumps({"type": "dm_sent", "msg": dm}), flush=True)

if __name__ == '__main__':
    import sys
    if "--json-stream" in sys.argv:
        asyncio.run(lead_pipeline())
    elif "--webhook" in sys.argv:
        uvicorn.run("ai_hustle_automator:app", host="0.0.0.0", port=8000)
    else:
        print("Use --json-stream or --webhook")
