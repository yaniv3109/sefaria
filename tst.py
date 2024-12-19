import streamlit as st
from openai import OpenAI
import requests
import os

temperature = 0.2
max_tokens = 100  ##

# מפתח API
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt_file_name = "prompt_he.txt"
content = ""

# מוודאים שהקובץ נמצא בתיקייה הנוכחית
current_dir = os.getcwd()  # מחזיר את הנתיב לתיקייה הנוכחית
file_path = os.path.join(current_dir, prompt_file_name)

try:
    # קריאת תוכן הקובץ
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
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stTextInput label {
        float: right;
    }
    .stButton button {
        float: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# הגדרות reCAPTCHA
RECAPTCHA_SITE_KEY = "6LeGFqAqAAAAAEG7EXLK37JlBOduC1VMdcURUEc4"
RECAPTCHA_SECRET_KEY = "6LeGFqAqAAAAABMOo58R88MARg3kunsGRrpSChrx"

# פונקציה לאימות reCAPTCHA
def verify_recaptcha(response_token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response_token}
    response = requests.post(url, data=data)
    result = response.json()
    return result.get("success", False)

# אפליקציית Streamlit
st.title('שו"ת עם הדרשן הדיגיטלי')

# משתנה פנימי לאחסון טוקן reCAPTCHA
recaptcha_token = st.session_state.get("recaptcha_token", "")

# קוד JavaScript להפקת טוקן reCAPTCHA
st.markdown(
    f"""
    <script src="https://www.google.com/recaptcha/api.js?render={RECAPTCHA_SITE_KEY}"></script>
    <script>
        grecaptcha.ready(function() {{
            grecaptcha.execute('{RECAPTCHA_SITE_KEY}', {{action: 'submit'}}).then(function(token) {{
                const tokenInput = document.getElementById('recaptcha-token');
                tokenInput.value = token;
                const event = new Event('input', {{ bubbles: true }});
                tokenInput.dispatchEvent(event);
            }});
        }});
    </script>
    <input type="hidden" id="recaptcha-token" oninput="streamlit.setComponentValue(this.value)" />
    """,
    unsafe_allow_html=True,
)

# קבלת שאלה מהמשתמש
user_question = st.text_input("מהי שאלתך?")

# הצגת טקסט מ-Sefaria
if st.button("קבלת טקסט מ-Sefaria"):
    sefaria_text = fetch_sefaria_text()
    st.write("תוכן מ-Sefaria:")
    st.write(sefaria_text)

# קבלת תשובה מהבוט
if st.button("לקבלת תשובה"):
    if recaptcha_token:
        if verify_recaptcha(recaptcha_token):
            st.success("אימות reCAPTCHA הצליח!")
            if user_question:
                try:
                    answer = ask_gpt(user_question)
                    st.success("תשובת הבוט:")
                    st.write(answer)
                except Exception as e:
                    st.error(f"אירעה שגיאה: {e}")
            else:
                st.warning("אנא הכנס שאלה.")
        else:
            st.error("אימות reCAPTCHA נכשל. נסה שוב.")
    else:
        st.error("לא התקבל טוקן reCAPTCHA. רענן את הדף ונסה שוב.")


