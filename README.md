# Guide to Run a Flask App

Follow these steps to set up and run your Flask application.

### 1. Create a Virtual Environment

Open your terminal or command prompt and run the following command to create a virtual environment:

```bash
python -m venv .venv
```
### 2. Activate the Virtual Environment

* For Linux/macOS:

    ```bash
    source .venv/bin/activate
    ```
* For Windows:

    ```bash
    .venv\Scripts\activate
    ```

### 3. Install Dependencies

Next, install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the .env.example file and rename to .env:

### 5. Configure the .env File

Open the .env file and fill in the missing fields as required for your environment.

### 6. Run the Application
```bash
python main.py
```