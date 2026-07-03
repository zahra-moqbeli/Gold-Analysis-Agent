# ============================================================
# IMPORTS
# ============================================================

import streamlit as st
import requests
import yfinance as yf
import matplotlib.pyplot as plt

from openai import OpenAI


# ============================================================
# API KEYS
# ============================================================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]


client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# CHAT MEMORY
# ============================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_history = st.session_state.chat_history


# ============================================================
# GOLD PRICE
# ============================================================

def get_gold_price():

    gold = yf.Ticker("GC=F")

    data = gold.history(period="2d")

    current_price = float(data["Close"].iloc[-1])

    previous_price = float(data["Close"].iloc[-2])

    change = current_price - previous_price

    percent = (change / previous_price) * 100

    return current_price, change, percent


# ============================================================
# GOLD CHART
# ============================================================

def plot_gold():

    gold = yf.Ticker("GC=F")

    data = gold.history(period="1mo")

    fig, ax = plt.subplots(figsize=(20,3))

    ax.plot(data.index, data["Close"], color="#FFD700", linewidth=3)

    ax.set_title("Gold Price (Last Month)")

    ax.set_xlabel("Date")

    ax.set_ylabel("USD")

    ax.grid(True)

    return fig


# ============================================================
# NEWS
# ============================================================

def get_news():

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=gold&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = data.get("articles", [])

    titles = []

    for article in articles[:10]:

        titles.append(article["title"])

    return titles


# ============================================================
# FILTER NEWS
# ============================================================

def filter_news(news):

    keywords = [

        "gold",

        "inflation",

        "interest",

        "fed",

        "dollar",

        "economy"

    ]

    filtered = []

    for n in news:

        if any(k.lower() in n.lower() for k in keywords):

            filtered.append(n)

    if len(filtered) == 0:

        filtered = news[:5]

    return filtered


# ============================================================
# DETECT INTENT
# ============================================================

def detect_intent(question):

    q = question.lower()

    if "قیمت" in q:

        return "price"

    elif "خبر" in q or "اخبار" in q:

        return "news"

    elif "خرید" in q or "بخر" in q:

        return "buy"

    else:

        return "analysis"
# ============================================================
# ANALYZE WITH AI
# ============================================================

def analyze(price, news):

    news_text = "\n".join(news)

    prompt = f"""
You are a professional Gold Market Analyst.

Current Gold Price:
{price:.2f} USD

Today's News:
{news_text}

Respond ONLY in Persian.

Use this format:

 روند کلی بازار

 مهم‌ترین عوامل موثر

 ریسک‌های بازار

جمع‌بندی

این پاسخ صرفاً جهت اطلاع‌رسانی است و توصیه مالی محسوب نمی‌شود.
"""

    response = client.chat.completions.create(

        model="mistralai/mistral-small-3.2-24b-instruct",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# ============================================================
# MAIN AGENT
# ============================================================

def gold_agent(user_question):

    intent = detect_intent(user_question)

    price, change, percent = get_gold_price()

    news = filter_news(get_news())

    chat_history.append({
        "role": "user",
        "content": user_question
    })

    # ======================
    # PRICE
    # ======================

    if intent == "price":

        answer = f"""
🌍 قیمت لحظه‌ای اونس جهانی طلا (XAU/USD)

💰 قیمت:
{price:.2f} دلار

📈 تغییر روزانه:
{change:.2f} دلار

({percent:.2f}%)
"""

    # ======================
    # NEWS
    # ======================

    elif intent == "news":

        answer = "📰 مهم‌ترین اخبار امروز\n\n"

        for i, item in enumerate(news, start=1):

            answer += f"{i}. {item}\n"

    # ======================
    # BUY
    # ======================

    elif intent == "buy":

        news_text = "\n".join(news)

        prompt = f"""
You are a professional Gold Investment Advisor.

Gold Price:
{price:.2f} USD

Today's News:
{news_text}

Question:
{user_question}

Respond ONLY in Persian.

Use this structure:

 وضعیت بازار

دلایل موافق خرید

 ریسک‌های خرید

 پیشنهاد نهایی

این پاسخ صرفاً جهت اطلاع‌رسانی است و توصیه مالی محسوب نمی‌شود.
"""

        response = client.chat.completions.create(

            model="mistralai/mistral-small-3.2-24b-instruct",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content

    # ======================
    # FULL ANALYSIS
    # ======================

    else:

        answer = analyze(price, news)

    chat_history.append({

        "role": "assistant",

        "content": answer

    })

    return answer
# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="Gold Analysis Agent",
    page_icon="🥇",
    layout="wide"
)
st.markdown("""
<style>

/* ==============================
   Background
============================== */

.stApp{

    background:#0b0b0b;

    background-image:
    radial-gradient(circle at top right,#b88a1a22,transparent 25%),
    radial-gradient(circle at bottom left,#ffffff08,transparent 25%);

}

/* ==============================
   Font
============================== */

html, body, [class*="css"]{

    font-family:'Segoe UI',sans-serif;

}

/* ==============================
   Main Title
============================== */

.main-title{

    font-size:48px;

    font-weight:700;

    color:#f6d365;

    text-align:center;

    margin-top:10px;

    text-shadow:0px 0px 18px rgba(246,211,101,.35);

}

/* ==============================
   Subtitle
============================== */

.sub-title{

    color:#d9d9d9;

    text-align:center;

    font-size:18px;

    margin-bottom:35px;

}

/* ==============================
   Card
============================== */

.glass{

    background:rgba(255,255,255,.05);

    backdrop-filter:blur(12px);

    border:1px solid rgba(255,255,255,.08);

    border-radius:18px;

    padding:25px;

    box-shadow:0 8px 25px rgba(0,0,0,.45);

    margin-bottom:25px;

}

/* ==============================
   Button
============================== */

.stButton>button{

    width:100%;

    height:55px;

    border-radius:15px;

    border:none;

    background:linear-gradient(90deg,#f6d365,#d4af37);

    color:black;

    font-weight:bold;

    font-size:18px;

    transition:.3s;

}

.stButton>button:hover{

    transform:scale(1.02);

    box-shadow:0px 0px 18px #d4af37;

}

/* ==============================
Text Input
============================== */

.stTextInput input{

    border-radius:14px;

    border:1px solid #444;

    background:#181818;

    color:white;

}

</style>
""", unsafe_allow_html=True)
st.title("🥇 Gold Analysis Agent")

st.markdown("""

<div style="padding-top:20px;padding-bottom:35px;">

<h1 class="main-title">

🥇 GOLD AI AGENT

</h1>

<p class="sub-title">

Smart Gold Market Analysis

<br>

با قدرت هوش مصنوعی، اخبار لحظه‌ای و قیمت جهانی

</p>

</div>

""", unsafe_allow_html=True)
st.markdown("""

<div class="glass">

<h3 style="color:#f6d365;">

🚀 Intelligent Gold Analysis Platform

</h3>

<p style="font-size:17px;color:#d9d9d9;line-height:1.8">

این سامانه با استفاده از

<b>OpenRouter AI</b>

،

<b>Yahoo Finance</b>

و

<b>NewsAPI</b>

قیمت لحظه‌ای طلا، اخبار مهم و تحلیل هوشمند بازار را ارائه می‌کند.

</p>

</div>

""", unsafe_allow_html=True)

st.divider()

# ===============================
# PRICE CARD
# ===============================

price, change, percent = get_gold_price()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        " قیمت اونس جهانی",
        f"{price:.2f} USD"
    )

with col2:

    st.metric(
        " تغییر روزانه",
        f"{change:.2f}",
        delta=f"{percent:.2f}%"
    )

with col3:

    st.metric(
        " اخبار",
        len(filter_news(get_news()))
    )

st.divider()

# ===============================
# CHART
# ===============================

st.subheader(" نمودار قیمت طلا")

fig = plot_gold()

st.pyplot(fig)

st.divider()

# ===============================
# NEWS
# ===============================

st.subheader(" آخرین اخبار")

for item in filter_news(get_news()):

    st.write("•", item)

st.divider()

# ===============================
# QUESTION
# ===============================

question = st.text_input(
    "سوال خود را درباره بازار طلا بنویس..."
)
st.caption("مثال:")

st.caption("• آیا الان زمان مناسبی برای خرید طلاست؟")

st.caption("• اخبار مهم امروز طلا")

st.caption("• قیمت لحظه‌ای اونس جهانی")

if st.button("🔍 تحلیل"):

    if question.strip() == "":

        st.warning("لطفاً سوالی وارد کنید.")

    else:

        with st.spinner("در حال تحلیل..."):

            answer = gold_agent(question)

        st.success("تحلیل آماده شد")

        st.markdown(answer)

# ===============================
# CHAT HISTORY
# ===============================

if len(chat_history) > 0:

    st.divider()

    st.subheader("💬 تاریخچه گفتگو")

    for item in reversed(chat_history):

        if item["role"] == "user":

            st.info("👤 " + item["content"])

        else:

            st.success(item["content"])

st.divider()

st.caption("Gold Analysis Agent v1.0")

st.caption("Powered by Streamlit • OpenRouter • Yahoo Finance • NewsAPI")