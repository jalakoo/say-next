import streamlit as st
from firebase_utils import FirebaseConnection
from neo4j_utils import Neo4jConnection
import constants

firebase = FirebaseConnection(st.secrets['firebase_api_key'])
iso_languages = constants.ISO_LANGUAGES
# st.session_state['current_phrase'] = ''
data = Neo4jConnection(st.secrets['neo4j_uri'], st.secrets['neo4j_user'], st.secrets['neo4j_password'])

# HEADER
def header():
    st.title('SayNext')
    st.text("""
        This app allows you to simulate possible foreign language 
        conversations by traversing a tree of phrases.
        """)
    with st.expander('Instructions'):
        st.text("""
        After selecting an initial phrase you will be presented 
        with possible phrases that follow it.\n
        These next phrases may be statements that can contextually
        accompanies, follows, or answers the selected phrase.\n
        After selecting a phrase, new follow up phrases will be
        presented.\n
        You may add new phrases. When doing so, selecting the 
        'follows <phrase>' will add that as a new next phrase
        option to <phrase>.
        """)
    st.markdown('--------\n')

# DASHBOARD
def dashboard():
    st.header('1. Select languages')

    col1, col2 = st.columns(2)
    with col1:
        user_language_code_key = st.selectbox('Your language', iso_languages.keys())
        user_language_code = iso_languages[user_language_code_key]
    with col2:
        language_code_key = st.selectbox('Learning', iso_languages.keys())
        language_code = iso_languages[language_code_key]
    print(f'language_code selected: {language_code}')

    st.markdown('--------\n')

    phrases = data.get_phrases(st.session_state['current_phrase'])
    if len(phrases) != 0:
        current_phrase = st.selectbox('Select a Phrase', phrases)
        st.session_state['current_phrase'] = current_phrase
        st.header('2. Next Phrases')
    else:
        st.header('2. New language')
        st.text("""
        No phrases yet for your selected learning language. 
        Start by adding new phrase below:
        """)
        
    st.markdown('--------\n')

    with st.form(key="new_phrase"):
        new_phrase = st.text_input('Add New Phrase')
        if 'current_phrase' in locals():
            should_link = st.checkbox(f'Follows "{current_phrase}"')
        add_button = st.form_submit_button(label='Add')


# SIDEBAR
st.sidebar.title("SayNext App")
st.sidebar.subheader("Sign in to access your personalized language learning simulation")
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
elif choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = firebase.sign_in(email,password)
        header()
        dashboard()
    else:
        st.text('Please login to access') 
else:
    header()
    st.text('Please login to access')
 
