# TKU AI Learning Assistant
A conversational AI assistant designed to help Tamkang University students.

## Setup development environment 
1. Install uv as package manager if you don't have it:
2. Install dependencies:
   ```bash
    uv sync
    uv run playwright install chromium
    ```

3. Create a `.env` file from `example.env` in the root directory and edit it with your configuration.
4. Run the bot:
   ```bash
   uv run bot.py
   ```
### Discord bot permissions integer
2252334537500736