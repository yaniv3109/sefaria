import streamlit as st
import requests
import os

# הגדרות reCAPTCHA
RECAPTCHA_SITE_KEY = "6LeGFqAqAAAAAEG7EXLK37JlBOduC1VMdcURUEc4"
RECAPTCHA_SECRET_KEY = "6LeGFqAqAAAAABMOo58R88MARg3kunsGRrpSChrx"

# משתנים לקביעת תצורת הבוט
temperature = 0.2
max_tokens = 100

# מפתח API של OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

# קריאת תוכן קובץ ההנחיות (prompt)
prompt_file_name = "prompt_he.txt"
content = ""
current_dir = os.getcwd()
file_path = os.path.join(current_dir, prompt_file_name)

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
except FileNotFoundError:
    print(f"שגיאה: הקובץ '{prompt_file_name}' לא נמצא בתיקייה {current_dir}.")
except Exception as e:
    print(f"שגיאה: {e}")

# פונקציה לאימות reCAPTCHA
def verify_recaptcha(response_token):
    """
    Verify the reCAPTCHA response token with Google's API.
    """
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response_token}
    verification_response = requests.post(url, data=data)
    result = verification_response.json()
    return result.get("success", False)

# אפליקציה ב-Streamlit
st.title("שו\"ת עם הדרשן הדיגיטלי")

# HTML להטמעת reCAPTCHA v3
st.markdown(
    f"""
    <script src="https://www.google.com/recaptcha/api.js?render={RECAPTCHA_SITE_KEY}"></script>
    <script>
    function sendTokenToStreamlit() {{
        grecaptcha.ready(function() {{
            grecaptcha.execute('{RECAPTCHA_SITE_KEY}', {{action: 'submit'}}).then(function(token) {{
                const inputField = document.getElementById('recaptcha-token');
                inputField.value = token;
                const event = new Event('input', {{ bubbles: true }});
                inputField.dispatchEvent(event);
            }});
        }});
    }}
    </script>
    <input type="hidden" id="recaptcha-token" value="" oninput="streamlit.setComponentValue(this.value)" />
    <button onclick="sendTokenToStreamlit()">לחץ כאן לאימות</button>
    """,
    unsafe_allow_html=True,
)

# שדה לקבלת הטוקן
recaptcha_token = st.text_input("Recaptcha Token", type="password")

# קלט לשאלה
user_question = st.text_input("מהי שאלתך?")

# כפתור שליחה
if st.button("לקבלת תשובה"):
    if not recaptcha_token:
        st.error("לא התקבל טוקן reCAPTCHA. רענן את הדף ונסה שוב.")
    elif not verify_recaptcha(recaptcha_token):
        st.error("אימות reCAPTCHA נכשל. נסה שוב.")
    elif user_question:
        try:
            # קריאה לבוט (לדוגמה בלבד)
            st.success("תשובת הבוט:")
            st.write("הבוט עונה: תשובה לדוגמה...")
        except Exception as e:
            st.error(f"אירעה שגיאה: {e}")
    else:
        st.warning("אנא הכנס שאלה.")

