"""Run the assigned questions and save actual answers for review."""
import json
import os
import time
from common import ROOT
from main import load, ask

QUESTIONS = [
    "How many days of Privilege Leave (PL) does a permanent employee get per year?",
    "What is the probation period for employees up to Senior Manager?",
    "What is the company's health-insurance premium amount?",
    "What is the current GST rate in India?",
    "How many days of maternity leave are given?",
    "What is the company's policy for employee travel to Mars?",
]

def main():
    store, llm = load()
    (ROOT / "data").mkdir(exist_ok=True)
    results = []
    for question in QUESTIONS:
        print(f"\nQuestion: {question}", flush=True)
        for attempt in range(4):
            try:
                answer = ask(question, store, llm)
                break
            except Exception as exc:
                if "429" not in str(exc) or attempt == 3:
                    raise
                print("Rate limit: waiting 55 seconds.", flush=True)
                time.sleep(55)
        print(answer, flush=True)
        results.append({"question": question, "response": answer})
        (ROOT / "data" / "evaluation.json").write_text(json.dumps(results, indent=2))
        time.sleep(float(os.getenv("EVALUATION_PAUSE", "20")))

if __name__ == "__main__":
    main()
