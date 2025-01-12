# smart_gov_app
 ## Overview
  
Smart Gov is a web application designed specifically for the people of Andhra Pradesh to help them access and stay informed about government schemes. The app enables users to easily create profiles, access relevant schemes, and receive personalized notifications about new opportunities. By leveraging advanced technologies like OCR (Optical Character Recognition) and powerful machine learning models, the app aims to enhance the accessibility and user experience for citizens.

## Key Features
- OCR for Automatic Profile Creation: Users can upload their Aadhar card, and the app automatically extracts relevant information using OCR to streamline profile creation.
- Personalized Scheme Suggestions: Based on the user's profile, the app suggests relevant government schemes.
- Chatbot for Scheme Access: A user-friendly chatbot that interacts with users to provide scheme information and answer questions.
- Scheme Notification via Email: Once a profile is created, users can receive notifications about relevant schemes directly to their registered email.
- Chat History Download: Users can download their entire interaction history with the chatbot for reference or record-keeping.
- Detailed Scheme Information: For each scheme, the app provides detailed descriptions, eligibility criteria, required documents, and benefits.
- Fast Data Retrieval: User data and scheme details are stored in a vector store locally, ensuring quick access and response times for the chatbot.
- LLM-Powered Responses: The app utilizes Meta's Llama 3.2 70B model for generating intelligent responses based on the user profile and retrieved data chunks.

## How It Works

#### Main Page
- The main page provides an overview of the app and the different categories of government schemes available.
- Users can either click on **Create Profile** or **Access Schemes** to proceed.

#### Profile Creation
- Clicking on **Create Profile** leads to a profile creation page where users upload their Aadhar card.
- OCR is used to automatically extract relevant details from the Aadhar card.
- Users then manually fill in any additional information to complete their profile.

#### Accessing Schemes
- Clicking on **Access Schemes** takes users to a chatbot interface.
- The chatbot is designed to interact with the user and provide scheme recommendations.
- Users can click on **Suggest Schemes**, and the app will automatically suggest schemes based on the user's profile.
- Users can also click on **Notify Schemes** to receive scheme notifications on their registered email.
- The **Download History** button allows users to download their chat history.

#### Detailed Scheme Information
- For each scheme, users can get in-depth details including eligibility criteria, required documents, and benefits.

  
## Technology Stack
  - Frontend: streamlit.
  - Backend: Python.
  - OCR: Tesseract.
  - AI Model: Meta's Llama 3.2 70B (for natural language processing and intelligent responses).
  - Database: Local vector store for fast data retrieval.
  - Email Service: For sending scheme notifications to users' email addresses(not fully included ).
