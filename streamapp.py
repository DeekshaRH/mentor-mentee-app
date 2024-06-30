import streamlit as st
import pandas as pd
import hashlib

# Utility functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Save user data
def save_user_data(user_data, filename='user_data.csv'):
    try:
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([user_data])
    df.to_csv(filename, index=False)

# Load user data
def load_user_data(filename='user_data.csv'):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame()

# Save feedback data
def save_feedback(feedback_data, filename='feedback_data.csv'):
    try:
        df = pd.read_csv(filename)
        df = pd.concat([df, pd.DataFrame([feedback_data])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([feedback_data])
    df.to_csv(filename, index=False)

# Load feedback data
def load_feedback(filename='feedback_data.csv'):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame(columns=['mentor_username', 'student_username', 'feedback'])

# Streamlit app
def main():
    # Custom CSS for styling
    st.markdown("""
        <style>
            .main { background-color: #f5f5f5; }
            h1 { color: #0073e6; font-family: 'Arial Black', Gadget, sans-serif; }
            h2 { color: #0073e6; }
            .stButton > button { background-color: #0073e6; color: white; }
            .stTextInput > label { color: #0073e6; }
            .stTextArea > label { color: #0073e6; }
            .stSelectbox > label { color: #0073e6; }
            .stSidebar .stSelectbox > label { color: #0073e6; }
        </style>
    """, unsafe_allow_html=True)

    st.title("Mentor-Mentee App")

    # Initialize session state variables
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False
        st.session_state['username'] = ''
        st.session_state['role'] = ''
    if 'selected_student' not in st.session_state:
        st.session_state['selected_student'] = None
    if 'subjects' not in st.session_state:
        st.session_state['subjects'] = [{'subject': '', 'marks': ''}]

    def go_to_page(page_name):
        st.session_state['page'] = page_name
        st.experimental_rerun()

    if st.session_state['page'] == 'Home':
        st.subheader("Home")
        st.write("Welcome to the Mentor-Mentee Matching App.")
        if st.button("Go to Login"):
            go_to_page('Login')
        if st.button("Go to SignUp"):
            go_to_page('SignUp')

    elif st.session_state['page'] == 'SignUp':
        st.subheader("Create New Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Role", ["Mentor", "Student"])
        
        if st.button("Signup"):
            hashed_password = make_hashes(password)
            user_data = {'username': username, 'password': hashed_password, 'role': role}
            save_user_data(user_data)
            st.success("You have successfully created an account")
            st.info("Go to Login Menu to login")
        if st.button("Back to Home"):
            go_to_page('Home')

    elif st.session_state['page'] == 'Login':
        st.subheader("Login Section")
        
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        role = st.selectbox("Role", ["Mentor", "Student"])
        
        if st.button("Login"):
            user_data = load_user_data()
            hashed_password = make_hashes(password)

            if username in user_data['username'].values and check_hashes(password, user_data[user_data['username'] == username]['password'].values[0]):
                st.session_state['login_status'] = True
                st.session_state['username'] = username
                st.session_state['role'] = role
                st.success(f"Logged In as {role}")
                if role == 'Student':
                    go_to_page('Student')
                elif role == 'Mentor':
                    go_to_page('Mentor')
            else:
                st.warning("Incorrect Username/Password")
        if st.button("Back to Home"):
            go_to_page('Home')

    if st.session_state['login_status']:
        if st.session_state['page'] == 'Student':
            st.subheader("Student Details Form")
            name = st.text_input("Name")
            roll_no = st.text_input("Roll Number")
            phone = st.text_input("Phone Number")

            st.subheader("Test Marks")
            subjects = st.session_state['subjects']

            for i, subject in enumerate(subjects):
                cols = st.columns([3, 2, 1])
                with cols[0]:
                    subject['subject'] = st.text_input(f"Subject {i+1}", subject['subject'], key=f"subject_{i}")
                with cols[1]:
                    subject['marks'] = st.text_input(f"Marks {i+1}", subject['marks'], key=f"marks_{i}")
                with cols[2]:
                    if st.button(f"Remove {i+1}", key=f"remove_{i}"):
                        subjects.pop(i)
                        st.experimental_rerun()

            if st.button("Add Subject"):
                subjects.append({'subject': '', 'marks': ''})

            st.session_state['subjects'] = subjects

            certifications = st.text_area("Certifications")
            projects = st.text_area("Projects")
            academic_issues = st.text_area("Academic Issues")
            
            if st.button("Submit Details"):
                test_marks = {sub['subject']: sub['marks'] for sub in subjects if sub['subject'] and sub['marks']}
                student_data = {
                    'username': st.session_state['username'],
                    'name': name,
                    'roll_no': roll_no,
                    'phone': phone,
                    'test_marks': test_marks,
                    'certifications': certifications,
                    'projects': projects,
                    'academic_issues': academic_issues
                }
                save_user_data(student_data, filename='students_data.csv')
                st.success("Details Submitted")

            st.subheader("Mentor Feedback")
            feedback_data = load_feedback()
            if not feedback_data[feedback_data['student_username'] == st.session_state['username']].empty:
                feedback = feedback_data[feedback_data['student_username'] == st.session_state['username']]['feedback'].values[0]
                st.write(feedback)
            else:
                st.write("No feedback yet")
            if st.button("Logout"):
                st.session_state['login_status'] = False
                go_to_page('Home')

        elif st.session_state['page'] == 'Mentor':
            if st.session_state['selected_student'] is None:
                st.subheader("Select a Student")
                students_data = load_user_data(filename='students_data.csv')
                student_usernames = students_data['username'].tolist()
                selected_student = st.selectbox("Select Student", student_usernames)
                
                if st.button("View Student Details"):
                    st.session_state['selected_student'] = selected_student
                    go_to_page('Mentor')
            else:
                selected_student = st.session_state['selected_student']
                students_data = load_user_data(filename='students_data.csv')
                student_data = students_data[students_data['username'] == selected_student].iloc[0]

                st.subheader("Student Details")
                st.write(f"**Name**: {student_data['name']}")
                st.write(f"**Roll Number**: {student_data['roll_no']}")
                st.write(f"**Phone**: {student_data['phone']}")
                st.write(f"**Test Marks**: {student_data['test_marks']}")
                st.write(f"**Certifications**: {student_data['certifications']}")
                st.write(f"**Projects**: {student_data['projects']}")
                st.write(f"**Academic Issues**: {student_data['academic_issues']}")

                feedback = st.text_area("Feedback", key="feedback")
                if st.button("Submit Feedback"):
                    feedback_data = {
                        'mentor_username': st.session_state['username'],
                        'student_username': selected_student,
                        'feedback': feedback
                    }
                    save_feedback(feedback_data)
                    st.success("Feedback submitted")
                
                if st.button("Back to Student List"):
                    st.session_state['selected_student'] = None
                    go_to_page('Mentor')
                
            if st.button("Logout"):
                st.session_state['login_status'] = False
                st.session_state['selected_student'] = None
                go_to_page('Home')

if __name__ == '__main__':
    main()
