import streamlit as st
from firebase_utils import FirebaseConnection
# from neo4j_utils import Neo4jConnection
import constants

firebase = FirebaseConnection(st.secrets['firebase_api_key'])
iso_languages = constants.ISO_LANGUAGES

# DASHBOARD
def dashboard():
    # st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    # bio = st.radio('Jump to',['Home','Feeds', 'Settings'])
    language_code_key = st.selectbox('Select Language', iso_languages.keys())
    language_code = iso_languages[language_code_key]
    print(f'language_code selected: {language_code}')

# SIDEBAR
st.sidebar.title("Say Next App")
st.sidebar.subheader("Sign in to access your personalized language simulation")
st.sidebar.markdown("-----")

# AUTHENTICATION
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password',type = 'password')

# Sign up Block
if choice == 'Sign up':
    # handle = st.sidebar.text_input(
    #     'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = firebase.new_user(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in?
        # user = sign_in(email, password)
        # db.child(user['localId']).child("Handle").set(handle)
        # db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome')
        st.info('Login via login drop down selection')

# Login Block**
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = firebase.sign_in(email,password)
        dashboard()

 
