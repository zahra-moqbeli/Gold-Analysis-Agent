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

st.title("🥇 Gold Analysis Agent")

st.markdown(
"""
### سامانه هوشمند تحلیل بازار طلا

این سامانه با استفاده از:

- قیمت لحظه‌ای اونس جهانی
- اخبار روز
- هوش مصنوعی

بازار طلا را تحلیل می‌کند.
"""
)

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