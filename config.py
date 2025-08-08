import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Airtable Configuration
    AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '500'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.3'))
    
    # Table Names
    APPLICANTS_TABLE = 'Applicants'
    PERSONAL_DETAILS_TABLE = 'Personal Details'
    WORK_EXPERIENCE_TABLE = 'Work Experience'
    SALARY_PREFERENCES_TABLE = 'Salary Preferences'
    SHORTLISTED_LEADS_TABLE = 'Shortlisted Leads'
    
    # Field Names
    APPLICANT_ID_FIELD = 'Applicant ID'
    COMPRESSED_JSON_FIELD = 'Compressed JSON'
    SHORTLIST_STATUS_FIELD = 'Shortlist Status'
    LLM_SUMMARY_FIELD = 'LLM Summary'
    LLM_SCORE_FIELD = 'LLM Score'
    LLM_FOLLOW_UPS_FIELD = 'LLM Follow-Ups'
    
    # Shortlist Criteria
    TIER_1_COMPANIES = ['Google', 'Meta', 'OpenAI', 'Microsoft', 'Apple', 'Amazon', 'Netflix']
    ELIGIBLE_LOCATIONS = ['US', 'Canada', 'UK', 'Germany', 'India']
    MAX_HOURLY_RATE = 100
    MIN_AVAILABILITY_HOURS = 20
    MIN_EXPERIENCE_YEARS = 4
