# AI News Summarizer Workflow

**1. Problem Statement:**
In the era of information overload, staying updated with the latest news is time-consuming.Users often come across lengthy articles but lack the time or attention span to read them in their entirety.There is a clear need for a tool that can instantly process web content and distill it into essential facts.

---

## 2. Technical Solution 
The application is built using a modular Python architecture consisting of two primary files:
* **`utils.py`**: The backend engine responsible for data extraction and AI processing.
* **`app.py`**: The frontend user interface.
---


### Content Extraction Engine (`utils.py`)
To prepare web data for the AI, the system performs the following steps:
* **Fetching**: Uses the `requests` library to retrieve raw HTML from any user-provided URL.
* **Cleaning**: Employs `BeautifulSoup` to strip away non-content elements like `<script>`, `<style>`, navigation bars, and footers.
* **Sanitization**: Cleans up whitespace to produce a raw text block, truncated to **5,000 characters** for efficient token usage and processing.

### AI Processing & Reliability
The system is designed for high availability and robust performance:
* **Multi-Model Strategy**: It attempts generation using a prioritized list of Google Gemini models (e.g., `gemini-2.0-flash-lite`, `gemini-2.0-flash`, and `gemini-2.5-flash`).
* **Automatic Fallback**: If a prioritized model is busy or fails, the system automatically transitions to the next available model.
* **Intelligent Retries**: Built with the `tenacity` library, the system uses **exponential backoff** to handle Rate Limits (429 errors), retrying up to 3 times before failing.

---

## 3. User Interface (`app.py`)
The interface focuses on a "Minimalist Design" to maximize user efficiency:
* **Simple Input**: A clean field for URL entry and a clear output area.
* **Feedback Loops**: A simple "Analyzing..." spinner hides background retry complexity while providing detailed error messages if the API is unreachable or the URL is invalid.

---

## 4. Workflow Diagram

<img width="1404" height="694" alt="image" src="https://github.com/user-attachments/assets/3368e861-6a63-49ae-bafa-f80b345798d6" />


