import streamlit as st
import requests

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
st.title("דוגמה ל-reCAPTCHA ב-Streamlit Cloud")

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

# טופס קלט
user_input = st.text_input("הכנס טקסט:")

# כפתור שליחה
if st.button("שלח"):
    if recaptcha_token:
        if verify_recaptcha(recaptcha_token):
            st.success("אימות reCAPTCHA הצליח!")
            st.write(f"הטקסט שהוזן: {user_input}")
        else:
            st.error("אימות reCAPTCHA נכשל. נסה שוב.")
    else:
        st.error("לא התקבל טוקן reCAPTCHA. רענן את הדף ונסה שוב.")
