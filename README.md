# FinSight AI — Mutual Fund Intelligence That Doesn't Guess

**Live App → [Click to Open](https://mutual-fund-advisor-6rjbwjswc8hvqxcqkwmoyw.streamlit.app/)**

Most financial tools either show you a hardcoded list of "top funds" or let an AI guess recommendations out of thin air. FinSight AI does neither. Every recommendation is backed by real math. Every explanation is grounded in real data. The AI never makes a single decision — it only explains what the numbers mean.

---

## What Makes This Different

There is one core design principle behind this project — **the LLM is a translator, not a decision maker.**

Here is what that means in practice:

We fetch 3 years of real NAV data directly from AMFI (the official government source for Indian mutual funds). We calculate three metrics — CAGR, Volatility, and Sharpe Ratio — entirely through code, with no AI involved. We then rank funds by Sharpe Ratio and pick the top 3. Only after all of this does the LLM see the results — and its only job is to explain those numbers in plain English.

The AI cannot change which funds are recommended. It cannot add information it doesn't have. It cannot predict the future. If it doesn't know something, it says so.

This architecture eliminates hallucination by design.

---

## How the Metrics Work

**CAGR (Compound Annual Growth Rate)**
Tells you how much a fund grew per year on average over 3 years. Calculated as `(End NAV / Start NAV)^(1/3) - 1`. Higher is better.

**Volatility**
Tells you how much the fund's value fluctuated. Calculated as the annualised standard deviation of daily returns `× √252`. Lower means a smoother, more stable ride.

**Sharpe Ratio**
The most important metric. Tells you how much return the fund gave per unit of risk taken. Calculated as `(CAGR - 6.5%) / Volatility` where 6.5% is the RBI repo rate proxy. We rank every fund by this number because it punishes both low returns and high volatility at the same time.

The fund with the highest Sharpe Ratio wins — not the one with the highest returns.

---

## The RAG Layer — No Hallucination, By Design

The Q&A section of the app is powered by Retrieval Augmented Generation (RAG). This means when you ask a question, the system searches through two verified documents — the official SEBI Mutual Fund FAQ (August 2024) and our internal methodology document — and answers strictly from what it finds there.

If your question is not covered in those documents, the system says "I don't have information on this in my knowledge base" rather than making something up.

This is what separates a reliable AI system from one that confidently gives wrong answers.

---

## The Fund Universe

We do not work with a hardcoded list of 10 funds. We fetch the complete list of active mutual funds from AMFI — over 1,400 schemes — filter to 795 Direct Growth funds, and categorize them by type. When you select a risk level, the system samples from the matching categories, calculates metrics for each, and returns the best performers.

Low risk maps to Large Cap, Liquid, and Debt funds.
Medium risk maps to Flexi Cap, Hybrid, and ELSS funds.
High risk maps to Mid Cap and Small Cap funds.

The recommendations change based on real market data. Not our preferences.

---

## Age-Aware Explanations

We don't just recommend funds — we explain them in the context of who you are. A 23-year-old and a 55-year-old might get the same top 3 funds, but the explanation they receive is different. Younger investors are told they have time to recover from market swings. Older investors are reminded that stability matters more at their stage. This context comes from the LLM, guided strictly by the user's age — not from any hardcoded text.

---

## Tech Stack

Built with Python and Streamlit for the UI, Pandas and NumPy for metric calculations, Groq (Llama 3.3 70B) as the LLM, LangChain and FAISS for the RAG pipeline, and HuggingFace embeddings for semantic search. NAV data is fetched directly from AMFI. Regulatory knowledge comes from the official SEBI FAQ document.

---

## Run It Yourself

```bash
git clone https://github.com/Sravanip2165/mutual-fund-advisor.git
cd mutual-fund-advisor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your free Groq API key from [console.groq.com](https://console.groq.com):
```
GROQ_API_KEY=your-key-here
```

Then build the fund universe and launch:
```bash
python build_universe.py
streamlit run app.py
```

---

## Disclaimer

FinSight AI is an educational project. All metrics are calculated from historical NAV data. Past performance does not guarantee future returns. This is not a SEBI registered investment advisory service. Please consult a qualified financial advisor before making investment decisions.
