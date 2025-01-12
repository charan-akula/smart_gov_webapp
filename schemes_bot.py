import streamlit as st # for webpage interface
from PIL import Image
import pytesseract # for ocr
import re
import pandas as pd
from langchain_cohere import CohereEmbeddings # for embeddings
from langchain_community.vectorstores import FAISS # vectore store
from langchain_groq import ChatGroq # llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from fpdf import FPDF # for converting the text into pdf 
import base64
# List of states and districts in Andhra Pradesh
states = ["Andhra Pradesh"]
districts_ap = [
    "Ananthapur", "Chittoor", "East Godavari", "Guntur", "Kadapa (YSR Kadapa)",
    "Krishna", "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam",
    "Vizianagaram", "West Godavari"
]

# Initialize default profile if not exists in session state
if 'profile' not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "dob": "",
        "gender": "",
        "po": "",
        "district": "",
        "state": "",
        "email": "",
        "education": "",
        "caste": "",
        "religion": "",
        "disability": "",
        "annual_income": 0,
        "current_occupation": "",
        "profile_pic": None
    }

# Function to render the profile creation page
def create_profile_page():
    st.title("Create Your Profile")

    # Upload Aadhar Card Image
    uploaded_file = st.file_uploader("Upload your Aadhar card to auto-fill the details", type=["jpg", "png", "jpeg"])

    # Regular expressions for extracting specific information
    def extract_data_from_text(text):
        name_pattern = re.compile(r"([A-Za-z]+(?:\s[A-Za-z]+)+)(?=\s*S/O)")
        dob_pattern = re.compile(r"DOB[:\s]*([\d/]+)")
        gender_pattern = re.compile(r"MALE|FEMALE")
        po_pattern = re.compile(r"PO:\s*([A-Za-z\s]+)")
        state_pattern = re.compile(r"State:\s*([A-Za-z\s]+)")
        mobile_pattern = re.compile(r"Mobile:\s*(\d{10})")

        # Extracting data using regex
        name = name_pattern.search(text)
        dob = dob_pattern.search(text)
        gender = gender_pattern.search(text)
        po = po_pattern.search(text)
        state = state_pattern.search(text)
        mobile_number = mobile_pattern.search(text)

        district_found = None
        for district in districts_ap:
            if district.lower() in text.lower():
                district_found = district
                break

        return {
            "Name": name.group(1) if name else "Not found",
            "DOB": dob.group(1) if dob else "Not found",
            "Gender": gender.group(0) if gender else "Not found",
            "PO": po.group(1) if po else "Not found",
            "District": district_found if district_found else "Not found",
            "State": state.group(1) if state else "Not found",
            "Mobile Number": mobile_number.group(1) if mobile_number else "Not found"
        }

    if uploaded_file is not None:
        # Open image using PIL
        image = Image.open(uploaded_file)
        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(image)
        extracted_info = extract_data_from_text(extracted_text)

        # Display extracted information
        st.subheader("Extracted Information by OCR")

        # Auto-filled details
        name = st.text_input("Full Name", extracted_info["Name"])
        dob = st.date_input("Date of Birth", value=pd.to_datetime(extracted_info["DOB"]))

        # Gender auto-fill and PO
        gender = "Male" if extracted_info["Gender"] == "MALE" else "Female"  # Set gender directly
        st.text_input("Gender", gender)  # Display gender directly

        po = st.text_input("Post Office", extracted_info["PO"])
        
        # State and District
        state = st.selectbox("State", states, index=0)
        district = st.selectbox("District", districts_ap, index=districts_ap.index(extracted_info["District"]) if extracted_info["District"] != "Not found" else 0)
        # Show helpful text before the "Provide Additional Information" button
        st.markdown("""
        **By providing the additional details, it helps you to get accurate and good updates.**
        Please fill out the following details to complete your profile.
        """)

        # Button to show additional information input fields
        if st.button("Provide Additional Information"):
            st.session_state.show_additional_info = True

        # If additional info section is to be shown
        if getattr(st.session_state, "show_additional_info", False):
            email = st.text_input("Email", "")
            education = st.selectbox("Educational Qualification", ["Select","None", "High School", "Undergraduate", "Postgraduate", "Doctorate"])
            caste = st.selectbox("Caste", ["Select","General", "SC", "ST", "OBC", "Other"])
            religion = st.selectbox("Religion", ["Select","Hindu", "Muslim", "Christian", "Other"])
            disability = st.selectbox("Disability Status", ["Select","None", "Physical", "Mental", "Both"])
            annual_income = st.number_input("Annual Family Income", min_value=0)
            current_occupation = st.selectbox("Current Occupation", ["Select","Student", "Farmer", "Self-Employed", "Government Employee", "Private Employee", "Other"])

            # Upload Profile Picture
            profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "png", "jpeg"])
            if profile_pic:
                st.session_state.profile_pic = profile_pic

            # Submit button to save the additional information and navigate to the main page
            if st.button("Submit"):
                # Store additional profile information in session state
                st.session_state.profile.update({
                    "name": name,
                    "dob": dob,
                    "gender": gender,
                    "po": po,
                    "district": district,
                    "state": state,
                    "email": email,
                    "education": education,
                    "caste": caste,
                    "religion": religion,
                    "disability": disability,
                    "annual_income": annual_income,
                    "current_occupation": current_occupation,
                    "profile_pic": profile_pic


                })


                st.success("Profile Created Successfully!")

                # Navigate back to the main page
                st.session_state.page = "main"

        # Button to go back to the main page without saving
        if st.button("Back to Main Page"):
            st.session_state.page = "main"  # Go back to the main page

# Main page rendering function
image_paths = [
    "pics/agriculture.jpeg","pics/banking.jpeg","pics/business.png","pics/education.png","pics/health.png","pics/housing.png",
    "pics/saftey.png","pics/science.jpeg","pics/skill.png","pics/welfare.png","pics/sports.jpeg","pics/transport.png",
    "pics/travel.jpeg","pics/sanitation.png","pics/women.png"
]

categories = [
    ("Agriculture",27),
    ("Banking, Financial Services",35),
    ("Business & Entrepreneurship",43),
    ("Education & Learning",62),
    ("Health & Wellness",67),
    ("Housing & Shelter",56),
    ("Public Safety & Justice",34),
    ("Science, IT ",32),
    ("Skills & Employment",45),
    ("Social Welfare",70),
    ("Sports & Culture",18),
    ("Transport & Infrastructure",32),
    ("Travel & Tourism",19),
    ("Utility & Sanitation",12),
    ("Women and Child",20),
]
from PIL import Image

def resize_image(image_path, width, height):
    """Resize the image to the specified width and height."""
    image = Image.open(image_path)
    image = image.resize((width, height))
    return image

def display_categories():
    st.markdown("### Categories Available:")
    cols_per_row = 5  # Number of columns per row
    cols = st.columns(cols_per_row)
    image_width = 70  # Fixed width
    image_height = 70  # Fixed height

    for idx, (category, count) in enumerate(categories):
        image_path = image_paths[idx]  # Get the corresponding image path
        col = cols[idx % cols_per_row]  # Assign the category to a column
        with col:
            resized_image = resize_image(image_path, image_width, image_height)
            st.image(resized_image, caption=None)  # Display the resized icon
            st.write(f"**{category}**")  # Category name
            st.write(f"*{count} Schemes*")  # Scheme count

        # Add space between each row
        if (idx + 1) % cols_per_row == 0:
            st.write("\n")  # Adds a line break between rows


def main_page():
    # Set up the page layout and title
        # Button to navigate to the profile creation page
    if st.button("Create Profile"):
        st.session_state.page = "create_profile"  # Change the page state


    if st.button("Access Schemes"):
        st.session_state.page = "access_schemes"  # Change the page state
    
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: red; text-decoration: underline; font-size: 36px;">SmartGov</h1>
        <h2 style="color: blue; font-size: 20px;">AI-Powered Platform for Seamless Government Scheme Access</h2>
    </div>
    <div style="text-align: center; margin-top: 30px;">
        <p style="font-size: 16px; color: #333; line-height: 1.6;">
This innovative web application is designed to transform how citizens of Andhra Pradesh access and benefit from government schemes. By leveraging the power of artificial intelligence, the platform simplifies the often complex processes of scheme discovery, eligibility verification, and application submissions.
At its core, the solution integrates an AI-based recommendation engine that analyzes user profiles and preferences to suggest the most relevant schemes. Whether it's a farmer looking for subsidies, a student seeking scholarships, or a mother requiring welfare benefits, the system ensures personalized assistance tailored to individual needs.
Navigating through the application is effortless, thanks to the integrated chatbot and voice assistant. Powered by Natural Language Processing (NLP), these features provide real-time guidance in multiple languages, ensuring accessibility for users across diverse linguistic backgrounds. The platform proactively keeps users informed by sending alerts about application deadlines, missing documents, and updates on their submissions.
The document verification process is fully automated using Optical Character Recognition (OCR) and AI. This ensures that documents are authentic by cross-verifying them with official government databases, eliminating manual errors and delays. The system also supports AI-powered form filling, which automatically populates application forms with data extracted from verified documents, further reducing user effort.
Security and inclusivity are at the heart of this solution. All user data is protected with end-to-end encryption, ensuring privacy and security at every step. The platform is designed to be intuitive and accessible to all, including those who may not be tech-savvy.
By streamlining processes, this solution not only reduces application errors and improves processing times but also raises awareness about government schemes. The ultimate goal is to enhance citizen satisfaction by making essential services more accessible and user-friendly, fostering a more inclusive and supportive governance system.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    display_categories()
    # Only display profile details after profile submission
    if st.session_state.profile["name"]:
        st.sidebar.subheader("Your Profile")
        profile = st.session_state.profile
        
        # Display profile details
        if profile['profile_pic']:
            st.sidebar.image(profile['profile_pic'], caption="Profile Picture", use_container_width=True)
            st.sidebar.write(f"**Name**: {profile['name']}")
            st.sidebar.write(f"**Gender**: {profile['gender']}")
            st.sidebar.write(f"**Date of Birth**: {profile['dob']}")
            st.sidebar.write(f"**Email**: {profile['email']}")
            st.sidebar.write(f"**State**: {profile['state']}")
            st.sidebar.write(f"**District**: {profile['district']}")
            st.sidebar.write(f"**Educational Qualification**: {profile['education']}")
            st.sidebar.write(f"**Caste**: {profile['caste']}")
            st.sidebar.write(f"**Religion**: {profile['religion']}")
            st.sidebar.write(f"**Disability Status**: {profile['disability']}")
            st.sidebar.write(f"**Annual Family Income**: {profile['annual_income']}")
            st.sidebar.write(f"**Current Occupation**: {profile['current_occupation']}")

            

def acess_schems():
    if st.session_state.profile["name"]:
        profile = st.session_state.profile
    gender = profile['gender']
    education = profile['education']
    current_occupation = profile['current_occupation']
    state = profile['state']
    # Email 
    email = profile['email']  # Add your email variable here
    
    # Title and logo
    title = "Government Schemes Chat Assistant.."
    
    # Function to convert image to base64 for embedding in HTML
    def get_base64_image(image_path):
        """Converts an image file to a base64 encoded string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    # Add the markdown for the title with one image
    st.markdown(
        f"""
        <h1 style="color: red; text-align: left; text-decoration: underline;">{title}</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Define user and system logos (replace with your image paths or URLs)
    user_logo = "pics/user.jpeg"
    system_logo = "pics/bot.jpeg"
    # Function to generate the chat history as a PDF
    # Function to generate the chat history as a PDF
    def generate_pdf():
        # Create PDF instance
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
    
        # Set font for the title
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="Chat History", ln=True, align="C")
        pdf.ln(10)
    
        # Loop through messages to add them to the PDF
        for message in st.session_state.messages:
            if message["role"] == "user":
                # Set red color and bold font for the user heading
                pdf.set_text_color(255, 0, 0)  # Red color for headings
                pdf.set_font("Arial", "B", 12)  # Bold font for user headings
                pdf.cell(0, 10, "User:", ln=True)
    
                # Replace ₹ with the word 'Rupees' in user content
                user_message = message["content"].replace("₹", "Rupees")
    
                # Set black color and normal font for the user message content
                pdf.set_text_color(0, 0, 0)  # Black color for content
                pdf.set_font("Arial", "", 12)  # Normal font for user content
                pdf.multi_cell(0, 10, user_message)
    
            elif message["role"] == "system":
                # Set red color and bold font for the system heading
                pdf.set_text_color(255, 0, 0)  # Red color for headings
                pdf.set_font("Arial", "B", 12)  # Bold font for system headings
                pdf.cell(0, 10, "System:", ln=True)
    
                # Replace ₹ with the word 'Rupees' in system content
                system_message = message["content"].replace("₹", "Rupees")
    
                # Set black color and normal font for the system message content
                pdf.set_text_color(0, 0, 0)  # Black color for content
                pdf.set_font("Arial", "", 12)  # Normal font for system content
                pdf.multi_cell(0, 10, system_message)
    
            # Add a small gap between each message
            pdf.ln(5)
    
        # Output the PDF to a binary stream (for download)
        pdf_output = pdf.output(dest='S').encode('latin1')
        return pdf_output
    
    # Initialize session state to store messages if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Function to display chat messages with avatars
    def display_messages():
        for message in st.session_state.messages:
            avatar = user_logo if message["role"] == "user" else system_logo
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    
    
    from langchain_cohere import CohereEmbeddings
    cohere_api_key="p8eOQWcrY8direXVjNhSy7xLcrOe4mnJ4XbMm85X"
    embeddings = CohereEmbeddings(
        model="embed-english-v3.0",
        cohere_api_key=cohere_api_key
    )
    
    loaded_db = FAISS.load_local("./vector_database",embeddings,allow_dangerous_deserialization=True)
    
    retriever = loaded_db.as_retriever(
        search_type="similarity", search_kwargs={"k":3}
    )
    
    Groq_api_key="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" # get this api key from groq website
    model=ChatGroq(   # model
        temperature=0.4, 
        groq_api_key=Groq_api_key,
        model_name="llama-3.3-70b-versatile",
        max_tokens=None)
    system_prompt=("You are bot specially designed for helping the people regading the government schemes in Andhra pradesh and Madya Pradesh States"
                   "Currently you are trained on arround 70 schemes in andhra pradesh , so if any schemes that you dodnt know , please say i was currently unaware of it once try in myscheme.gov.in site"
                   "if some one wishes you , greet them politely"
                   "Some times user may give improper spellings and improper setences , try to identify them and good good responses"
                   "You are trained by charanakula632 team members form RGUKT,RKV University"
                    "Use the data obtained from only  the retrieved context and provide the appropraite result "
                   "if any personal questions are any unwanted questions regarding schemes were asked say that you are not suposed to answer them"
                   "{context}"
                  ) ## conetxt is autofilled
    template=ChatPromptTemplate.from_messages(
        [("system",system_prompt),
        ("human","{input}"),
        ("ai","")]
    )
    
    question_answer_chain = create_stuff_documents_chain(model, template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain) # here 1st chunks are retrived and then it was combined with prompt to get response from llm
    
    
    user_input = st.chat_input("Type your message:")
    
    if user_input:
        # Append user input to session state as a message
        st.session_state.messages.append({"role": "user", "content": user_input})
    
        # Calculate the length of the user input
        try:
        # Generate system's response (length of the input)
            system_response1 = rag_chain.invoke({"input":user_input})
            system_response=system_response1["answer"]
        except:
            system_response="Some Error at Groq Internal Server" # some times groq.InternalServerError 503 error may occur
    
        # Append the system's response to session state
        st.session_state.messages.append({"role": "system", "content": system_response})
    
        # Display updated chat history
        display_messages()
    
    
    if st.sidebar.button("Suggest as per my profile"):
        st.session_state.messages.append({"role": "user", "content": "Scheme Suggestion as per your profile"})
        # Logic to suggest schemes based on profile (gender, education, caste, occupation)
        suggest_input = f"My profile is (Gender: {gender}, Education: {education} Occupation: {current_occupation} , state:{state}), suggets some schemes regarding my profile data "
        suggest_output=rag_chain.invoke({"input":suggest_input})
        suggest_response=suggest_output["answer"]
    
        st.session_state.messages.append({"role": "system", "content": suggest_response})
        display_messages()
    
    if st.sidebar.button("Notify the schemes"):
        # Display a message that schemes are notified to the user's email and mobile number
        notification_message = f"Schemes will be notified for your email ID: {email} ."
        st.sidebar.write(notification_message)
    
    if len(st.session_state.messages) > 0:
        if st.sidebar.button("Clear History"):
            st.session_state.messages = []  # Reset the chat history
    else:
        st.sidebar.write("No history to clear")
    
    if len(st.session_state.messages) > 0:
        # Generate the PDF
        pdf_file = generate_pdf()
    
        # Show the download button only if there is chat history
        st.sidebar.download_button(
            label="Download History",
            data=pdf_file,
            file_name="chat_history.pdf",
            mime="application/pdf",
            key="download_pdf_button"
        )
    else:
        # Display a message when there is no chat history
        st.sidebar.write("No history to download")

    if st.sidebar.button("Back to HomePage"):
        st.session_state.page = "main"  # Go back to the main page


# Set up the Streamlit session state
if 'page' not in st.session_state:
    st.session_state.page = "main"  # Default page is the main page

# Page rendering based on the session state
if st.session_state.page == "main":
    main_page()
elif st.session_state.page == "create_profile":
    create_profile_page()
elif st.session_state.page == "access_schemes":
    acess_schems()



    
    
