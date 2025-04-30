# CSV Analysis Agent

A powerful AI-powered CSV analysis tool that allows users to interact with their CSV data using natural language queries. The application uses OpenAI's GPT-4 model to understand and process complex queries about the data.

## Features

- Upload and process CSV files
- Natural language querying of CSV data
- Statistical analysis of datasets
- Date range filtering
- Interactive Streamlit interface
- Real-time data visualization
- Example queries sidebar

## Prerequisites

- Python 3.9 or higher (for local development)
- Poetry for dependency management
- OpenAI API key
- Modern web browser
- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Local Installation with Poetry

1. Clone the repository:
```bash
git clone <repository-url>
cd csv-analysis-agent
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
poetry run streamlit run src/app.py
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd csv-analysis-agent
```

2. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Build and run using Docker Compose:
```bash
docker-compose up --build
```

## Usage

### Local Development with Poetry

1. Activate the Poetry environment:
```bash
poetry shell
```

2. Start the Streamlit application:
```bash
streamlit run src/app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

### Docker Deployment

1. The application will be available at http://localhost:8501 after running:
```bash
docker-compose up --build
```

2. To stop the application:
```bash
docker-compose down
```

3. To view logs:
```bash
docker-compose logs -f
```

## Example Queries

- "How many rows are in the dataset?"
- "What is the average value of each numeric column?"
- "Show me the distribution of values in column X"
- "How many items were ordered between June 13th and July 14th?"
- "What is the total sum of column Y?"
- "Show me the top 5 most frequent values in column Z"

## Project Structure

```
csv-analysis-agent/
├── src/
│   ├── agents/
│   │   └── csv_agent.py
│   └── app.py
├── uploads/
├── pyproject.toml
├── poetry.lock
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

## Features in Detail

### Data Upload
- Supports any CSV file format
- Automatic data type detection
- Preview of uploaded data
- Basic dataset statistics

### Query Interface
- Natural language query processing
- Real-time response
- Error handling and validation
- Example queries sidebar

### Data Analysis
- Statistical calculations
- Date range filtering
- Data aggregation
- Pattern recognition
- Custom analysis requests

## Error Handling

The application includes comprehensive error handling for:
- File upload issues
- Invalid CSV formats
- Query processing errors
- API rate limiting
- Data type mismatches

## Security Considerations

- API keys are stored securely in environment variables
- File uploads are validated and sanitized
- Temporary files are automatically cleaned up
- Input validation is performed on all user queries

## Docker Configuration

The application includes Docker support with the following features:
- Poetry-based dependency management
- Multi-stage build for optimized image size
- Volume mounting for persistent uploads
- Environment variable management
- Automatic container restart
- Port mapping for easy access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 