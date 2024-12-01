# Technical document for developers

This AI system contains two servers: 
- Streamlit front-end application server
- Flask back-end server
https://docs.google.com/presentation/d/14ksVlbg3tV1rETHpiqgD1U41WMcqrPBvExYm-WMfSF4/edit?usp=drivesdk
## Local installation and run the system

### Prerequisites
- Open AI API Key: [Visit here](https://platform.openai.com/api-keys)
- Recent version of Python 3.10.x (tested)

### Local Installation 
The following installation commands have been tested on Linux 
```
git clone git@github.com:hungdtrn/CashflowAssistant.git
cd CashflowAssistant
conda create -n cashflow python=3.10
conda activate cashflow
pip install -r requirements.txt
```

Your Python virtual environment should now be ready to support both Back-end and Front-end servers.

### Run the Backend server on your local system

Current working directory: Top-level of the CashflowAssistant repository
```
cd server
export OPENAI_API_KEY=sk-.....
export OPENAI_MODEL="gpt-3.5-turbo"
bash ./start_server.sh
```

### Run the Streamlit UI server on your local system
Current working directory: Top-level of the CashflowAssistant repository
```
cd client
export SERVER_URL="http://0.0.0.0:8080"
streamlit run home.py --server.port 8888
```

### Deploy on GCP
To be written soon!
