import streamlit as st
from PIL import Image
import pickle
import sqlite3

conn = sqlite3.connect('loan_details.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS loan_details
             (Account_No INTEGER PRIMARY KEY, Full_Name TEXT, Loan_Status TEXT, Reason TEXT)''')

model = pickle.load(open('./Model/ML_Model.pkl', 'rb'))

def run():
    st.title("Bank Loan Prediction System")
    st.sidebar.text("Welcome to our loan prediction app.")

    img1 = Image.open('bank.png')
    img1 = img1.resize((156, 145))
    st.image(img1, use_column_width=False)

    st.markdown(
        """
        <style>
        .title {
            text-align: center;
        }
        .sidebar {
            text-align: left;
        }
        .centered {
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="centered">Use the form below to check your loan eligibility.</p>', unsafe_allow_html=True)

    account_no = st.text_input('Account number')
    if not account_no.isnumeric():
        st.error("Account number should be numeric.")

    fn = st.text_input('Full Name')
    gen_display = ('Female', 'Male')
    gen_options = list(range(len(gen_display)))
    gen = st.selectbox("Gender", gen_options, format_func=lambda x: gen_display[x])

    mar_display = ('No', 'Yes')
    mar_options = list(range(len(mar_display)))
    mar = st.selectbox("Marital Status", mar_options, format_func=lambda x: mar_display[x])

    dep_display = ('No', 'One', 'Two', 'More than Two')
    dep_options = list(range(len(dep_display)))
    dep = st.selectbox("Dependents", dep_options, format_func=lambda x: dep_display[x])

    edu_display = ('Not Graduate', 'Graduate')
    edu_options = list(range(len(edu_display)))
    edu = st.selectbox("Education", edu_options, format_func=lambda x: edu_display[x])

    emp_display = ('Job', 'Business')
    emp_options = list(range(len(emp_display)))
    emp = st.selectbox("Employment Status", emp_options, format_func=lambda x: emp_display[x])

    prop_display = ('Rural', 'Semi-Urban', 'Urban')
    prop_options = list(range(len(prop_display)))
    prop = st.selectbox("Property Area", prop_options, format_func=lambda x: prop_display[x])

    cred_display = ('Between 300 to 500', 'Above 500')
    cred_options = list(range(len(cred_display)))
    cred = st.selectbox("Credit Score", cred_options, format_func=lambda x: cred_display[x])

    mon_income = st.number_input("Applicant's Monthly Income($)", value=0)
    co_mon_income = st.number_input("Co-Applicant's Monthly Income($)", value=0)
    loan_amt = st.number_input("Loan Amount (Thousand $)", value=0)

    dur_display = ['2 Month', '6 Month', '8 Month', '1 Year', '16 Month']
    dur_options = range(len(dur_display))
    dur = st.selectbox("Loan Duration", dur_options, format_func=lambda x: dur_display[x])

    if st.button("Submit"):
        c.execute("SELECT * FROM loan_details WHERE Account_No=?", (account_no,))
        existing_data = c.fetchone()
        if existing_data:
            st.error("An entry with this account number already exists.")
        else:
            duration = 0
            if dur == 0:
                duration = 60
            if dur == 1:
                duration = 180
            if dur == 2:
                duration = 240
            if dur == 3:
                duration = 360
            if dur == 4:
                duration = 480
            features = [[gen, mar, dep, edu, emp, mon_income, co_mon_income, loan_amt, duration, cred, prop]]
            prediction = model.predict(features)
            lc = [str(i) for i in prediction]
            ans = int("".join(lc))
            reason = ""
            if ans == 0:
                reason = "Insufficient Credit Score or Income"
                st.error(
                    f"Hello: {fn} || Account number: {account_no} || According to our Calculations, you will not get the loan from the bank. Reason: {reason}"
                )
                c.execute("INSERT INTO loan_details (Account_No, Full_Name, Loan_Status, Reason) VALUES (?, ?, ?, ?)",
                          (account_no, fn, 'Rejected', reason))
                conn.commit()
            else:
                reason = "N/A"
                st.success(
                    f"Hello: {fn} || Account number: {account_no} || Congratulations!! You will get the loan from the bank."
                )
                c.execute("INSERT INTO loan_details (Account_No, Full_Name, Loan_Status, Reason) VALUES (?, ?, ?, ?)",
                          (account_no, fn, 'Approved', reason))
                conn.commit()

    if st.button("Show Loan Details"):
        display_loan_details()

    st.text_input("Enter Password to Delete Entry", type="password", key='password')
    delete_account_no = st.text_input('Account number to delete')
    if st.button("Delete Entry"):
        if st.session_state.password == '1234':
            c.execute("DELETE FROM loan_details WHERE Account_No=?", (delete_account_no,))
            conn.commit()
            st.write(f"Entry with Account No. {delete_account_no} deleted.")
        else:
            st.write("Incorrect password. Entry not deleted.")


def display_loan_details():
    st.write("### Loan Details:")
    c.execute("SELECT * FROM loan_details")
    data = c.fetchall()
    if len(data) > 0:
        st.table(data)
    else:
        st.write("No loan details to display")


if __name__ == '__main__':
    run()