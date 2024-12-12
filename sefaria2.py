import streamlit as st
from openai import OpenAI
import requests

# יצירת מפתח API של OpenAI
client = OpenAI(api_key='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')

def fetch_sefaria_text():
    
    base_url = "https://www.sefaria.org/api/index"
    #url = f"{base_url}{reference.replace(' ', '_')}"
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
        model="gpt-4",
        messages=[
            {"role": "system", "content": "אתה בוט שעונה רק על מידע מספרא."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

#sefaria_text = fetch_sefaria_text("Genesis 1")


# אפליקציית Streamlit
st.title("צ'אטבוט חכם ספרא")

# קבלת שאלה מהמשתמש
user_question = st.text_input("הכנס שאלה על תוכן מספרא")

# קבלת תשובה מהבוט
if st.button("קבל תשובה"):
    if user_question:
        try:
            answer = ask_gpt(user_question)
            st.success("תשובת הבוט:")
            st.write(answer)
        except Exception as e:
            st.error(f"אירעה שגיאה: {e}")
    else:
        st.warning("אנא הכנס שאלה.")
