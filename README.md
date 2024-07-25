# dt4h-coverage-dash

This is a dashboard for the DT4H project that shows the coverage of the variables in the data (distemist, symptemist and medprocner). The dashboard is built using Dash and Plotly.

## Installation

To install the dashboard, you need to have Python 3.10.12 installed on your machine. You can download Python from [here](https://www.python.org/downloads/).

```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

To run the dashboard, you need to run the following command:

```bash
python app.py
```

The dashboard will be available at http://127.0.0.1:8001/coverage/ in your browser. The port can be changed using the parameter `--port`.

```bash
python app.py --port 8003
```

