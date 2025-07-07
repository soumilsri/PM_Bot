# Product Management Bot

This bot helps automate product management workflows by connecting to Aha!, grooming stories, and preparing roadmaps.

## Setup

1. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set your Aha! API key in your environment:
   ```powershell
   $env:AHA_API_KEY="your_actual_api_key_here"
   ```
4. Run the bot:
   ```powershell
   python main.py
   ```

## Features
- Fetches stories from Aha!
- Grooms stories (summarizes, categorizes, prioritizes)
- Prepares for roadmap automation 