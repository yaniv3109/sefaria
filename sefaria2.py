import streamlit as st
from openai import OpenAI
import requests
import os

temperature = 0.2
max_tokens = 500

# מפתח API
openai_api_key = os.getenv("OPENAI_API_KEY")

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
            {"role": "system", "content": """
            אתה בוט שעונה על שאלות ממאגר המידע של Sefaria.
            Sefaria הוא מאגר דיגיטלי מקיף לטקסטים יהודיים.
            המאגר כולל: תנ"ך, תלמוד בבלי וירושלמי, מדרשים, ספרי הלכה, ספרי מחשבה וקבלה, פירושים ותוספות, תרגומים וחיבורים מודרניים כמו מאמרים.
            מדובר בטקסטים היסטוריים ותורניים.
            בתשבותך תכלול פירושים ממקורות שונים, קשרים בין טקסטים שונים והפניות צולבות.
             """},
            {"role": "user", "content": prompt}
        ],
        temperature = temperature,
        max_tokens = max_tokens
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

# אפליקציית Streamlit
st.title('שו"ת עם הדרשן הדיגיטלי')

# קבלת שאלה מהמשתמש
user_question = st.text_input("מהי שאלתך?")

# קבלת תשובה מהבוט
if st.button("לקבלת תשובה"):
    if user_question:
        try:
            answer = ask_gpt(user_question)
            st.success("תשובת הבוט:")
            st.write(answer)
        except Exception as e:
            st.error(f"אירעה שגיאה: {e}")
    else:
        st.warning("אנא הכנס שאלה.")
