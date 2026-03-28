# test_rag.py
from rag import get_vectorstore, answer_question

print("=" * 60)
print("TESTING RAG PIPELINE")
print("=" * 60)

# build or load vectorstore
vectorstore = get_vectorstore()

# test questions
questions = [
    "What is NAV?",
    "What is SIP?",
    "What is Sharpe ratio?",
    "Why do you rank funds by Sharpe ratio?",
    "What is CAGR?",
    "Is my money safe in mutual funds?",
    "What is the weather today?",  # should say I don't know
]

print("\n--- TESTING QUESTIONS ---\n")
for q in questions:
    print(f"Q: {q}")
    answer = answer_question(q, vectorstore)
    print(f"A: {answer}")
    print("-" * 40)