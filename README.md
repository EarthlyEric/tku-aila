# TKU AI Learning Assistant
A conversational AI Agent assistant designed to help Tamkang University students.

## Features
There are 3 types of agents available:
1. **Course Information Agent**: Provides information about courses offered at Tamkang University.
2. **Problem Solving Agent**: Assists with programming and math tasks and questions.
3. **Exam Preparation Agent**: Helps students prepare for exams by answering questions and providing study materials.

## Setup development environment 
1. Install uv as package manager if you don't have it:
2. Install dependencies:
   ```bash
    uv sync
    ```

3. Create a `.env` file from `example.env` in the root directory and edit it with your configuration.
4. Run the bot:
   ```bash
   uv run bot.py
   ```
## Deployment
Recommended to use Docker for deployment. Pull the latest image from Github Packages and run it with your environment variables.
```bash
docker pull ghcr.io/earthlyeric/tku-aila:latest
```
cofigure `docker-compose.example.yml` as needed and rename it to `docker-compose.yml`, then run:
```bash
docker-compose up -d
```
Oh, everything should be up and running!
### discord bot permissions integer
2252334537500736