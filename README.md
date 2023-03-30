# AgriBuddyWebAPI

A backend API for AgriBuddy project built with Python 3 and FastAPI.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


### Installing

1. Clone the repository and change into the project directory

```bash
git clone https://github.com/SftwreDev/agribuddywebapi.git
cd agribuddywebapi
cd app
```

2. Create virtual environment

```bash
python -m virtualenv venv
```

3. Activate virtual environment

```bash
.\venv\Scripts\activate
```

4. Install requirements

```bash
pip install -r requirements.txt
```

5. Run FASTAPI Server

```bash
uvicorn main:app --reload
```
