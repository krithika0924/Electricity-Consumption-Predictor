# ⚡ Electricity Consumption Predictor
**AI-Powered Energy Management & Analytics Dashboard**

> **A Final Year BCA Project by Krithika **

This project is a full-stack, predictive SaaS (Software as a Service) application designed to forecast residential electricity consumption and calculate exact billing costs. Instead of relying on static formulas, it utilizes a Machine Learning engine to learn a household's unique behavioral patterns based on seasonal changes and temperature fluctuations.

---

## 🚀 Core Features

* **Advanced AI Forecasting:** Uses a `RandomForestRegressor` (100 estimators) to prevent data overfitting and generate generalized, realistic consumption predictions based on temperature and seasonal inputs.
* **Deterministic Billing Engine:** Pipes the AI's predicted units into a secondary algorithm that calculates exact local utility costs, including tiered telescopic slab rates, fixed charges, customer charges, and electricity duty.
* **Multi-Page Dashboard Architecture:** Features a sleek, modern UI with seamless routing between the **Predictor Engine**, **Advanced Analytics**, and **Account Profile** pages.
* **Secure Local Authentication:** Implements a custom JSON-based user database featuring encrypted-style credential matching, Two-Factor account recovery (Security Questions), and URL parameter-based session persistence.
* **Automated Data Processing:** Translates raw textual data into machine-readable formats using Categorical Label Encoding (`cat.codes`) for seamless model training.

---

## 🛠️ Technology Stack

* **Frontend / UI:** Streamlit, Streamlit Option Menu, Custom CSS (Glassmorphism design)
* **Backend Logic:** Python 3
* **Machine Learning:** Scikit-Learn (`RandomForestRegressor`)
* **Data Manipulation:** Pandas
* **Data Visualization:** Matplotlib
* **Database & Authentication:** Firebase (Firestore / Realtime Database & Firebase Auth)

---

## ⚙️ Installation & Setup

Follow these steps to run the application on your local machine. Open your terminal and run the following commands sequentially:

```bash
# 1. Clone the repository
git clone https://github.com/krithika0924/Electricity-Consumption-Predictor.git

# 2. Navigate into the project folder
cd Electricity-Consumption-Predictor

# 3. Install the required dependencies
pip install -r requirements.txt

🔐 Firebase Configuration
Before running the app, you need to connect it to your Firebase project:

Go to your Firebase Console and generate a new private key from your Project Settings (Service Accounts).

Download the JSON file and rename it to firebase_credentials.json (or whatever name your app.py script is looking for).

Place this JSON file in the root directory of your project. (Note: Ensure this file is added to your .gitignore so you don't accidentally push your private keys to GitHub).

# 4. Run the application
streamlit run app.py

Access the Dashboard: Once the server starts, open your web browser and navigate to  
 http://localhost:8501.


##  How to Use the Predictor
    
To get highly accurate predictions, the AI needs to learn from actual historical data.

Register/Login to the application.

Open the sidebar and expand the "Need a template?" section.

Download the electricity_bills.csv template.

Open the file in Excel or Notepad and replace the dummy consumption numbers with your actual monthly usage.

Upload the updated CSV file via the sidebar to instantly unlock the AI Predictor and Analytics dashboards.

Select an upcoming month and adjust the expected temperature to generate your detailed bill breakdown!
