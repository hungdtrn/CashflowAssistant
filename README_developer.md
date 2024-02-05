# Technical document for developers

This AI system contains two servers: 
- Streamlit front-end application server
- Flask back-end server

## Local installation and run the system

### Prerequisites
- Open AI API Key: [Visit here](https://platform.openai.com/api-keys)
- Recent version of Python 3.10.x (tested)

### Local Installation 
The following installation commands have been tested on Linux 
```
git clone git@github.com:hungdtrn/cashflow_assistant.git
cd cashflow_assistant
python -m venv venv_aide
source venv_aide/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Your Python virtual environment should now be ready to support both Back-end and Front-end servers.

### Run the Backend server on your local system

Current working directory: Top-level of the cashflow_assistant repository
```
cd server
export OPENAI_API_KEY=sk-.....
export OPENAI_MODEL="gpt-3.5-turbo"
bash ./start_server.sh
```

### Run the Streamlit UI server on your local system
Current working directory: Top-level of the cashflow_assistant repository
```
cd client
export SERVER_URL="http://0.0.0.0:8080"
streamlit run home.py --server.port 8888
```

### Deploy on GCP
To be written soon!