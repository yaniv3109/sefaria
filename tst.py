import streamlit as st
from openai import OpenAI
import requests
import os

# reCAPTCHA keys (replace with your keys from Google reCAPTCHA Admin Console)
RECAPTCHA_SITE_KEY = "6LeGFqAqAAAAAEG7EXLK37JlBOduC1VMdcURUEc4"
RECAPTCHA_SECRET_KEY = "6LeGFqAqAAAAABMOo58R88MARg3kunsGRrpSChrx"

# הגדרות OpenAI
temperature = 0.2
max_tokens = 100

# מפתח API
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt_file_name = "prompt_he.txt"
content = ""

# מוודאים שהקובץ נמצא בתיקייה הנוכחית
current_dir = os.getcwd()
file_path = os.path.join(current_dir, prompt_file_name)

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
except FileNotFoundError:
    print(f"שגיאה: הקובץ '{prompt_file_name}' לא נמצא בתיקייה {current_dir}.")
except Exception as e:
    print(f"שגיאה: {e}")

print(content)

# יצירת מפתח API של OpenAI
client = OpenAI(api_key=openai_api_key)

# פונקציה למשיכת טקסט מ-Sefaria
def fetch_sefaria_text():
    base_url = "https://www.sefaria.org/api/index"
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("he", "טקסט לא נמצא")
    else:
        return f"שגיאה בקבלת נתונים: {response.status_code}"

# פונקציה לאימות reCAPTCHA
def verify_recaptcha(response_token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response_token}
    verification_response = requests.post(url, data=data)
    result = verification_response.json()
    return result.get("success", False)

# פונקציה לשליחת שאלה ל-GPT
def ask_gpt(user_question):
    prompt = f"השאלה: {user_question}\nענה בהתבסס על הטקסט בלבד."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# הוספת CSS לעמוד עבור RTL
st.markdown(
    f"""
    <style>
    body {{
        direction: rtl;
        text-align: right;
    }}
    .stTextInput label {{
        float: right;
    }}
    .stButton button {{
        float: right;
    }}
    </style>
    <script src="https://www.google.com/recaptcha/api.js?render={RECAPTCHA_SITE_KEY}"></script>
    <script>
        function getRecaptchaToken(action, callback) {{
            grecaptcha.ready(function() {{
                grecaptcha.execute("{RECAPTCHA_SITE_KEY}", {{action: action}}).then(function(token) {{
                    callback(token);
                }});
            }});
        }}
    </script>
    """,
    unsafe_allow_html=True,
)

# אפליקציית Streamlit
st.title('שו"ת עם הדרשן הדיגיטלי')

# קבלת שאלה מהמשתמש
user_question = st.text_input("מהי שאלתך?")

# JavaScript להפעלת reCAPTCHA וקריאת הפונקציה מהצד הלקוח
if st.button("לקבלת תשובה"):
    if user_question:
        # Get the reCAPTCHA token from the client
        recaptcha_token = st.experimental_get_query_params().get("g-recaptcha-response", [None])[0]

        if recaptcha_token and verify_recaptcha(recaptcha_token):
            try:
                answer = ask_gpt(user_question)
                st.success("תשובת הבוט:")
                st.write(answer)
            except Exception as e:
                st.error(f"אירעה שגיאה: {e}")
        else:
            st.error("אימות reCAPTCHA נכשל. נסה שוב.")
    else:
        st.warning("אנא הכנס שאלה.")
