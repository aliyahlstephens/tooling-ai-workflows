from pyairtable import Api, Base, Table
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from config import Config

class AirtableClient:
    def __init__(self):
        self.api = Api(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN)
        self.base = Base(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID)
        
        # Initialize table references
        self.applicants_table = Table(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID, Config.APPLICANTS_TABLE)
        self.personal_details_table = Table(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID, Config.PERSONAL_DETAILS_TABLE)
        self.work_experience_table = Table(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID, Config.WORK_EXPERIENCE_TABLE)
        self.salary_preferences_table = Table(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID, Config.SALARY_PREFERENCES_TABLE)
        self.shortlisted_leads_table = Table(Config.AIRTABLE_PERSONAL_ACCESS_TOKEN, Config.AIRTABLE_BASE_ID, Config.SHORTLISTED_LEADS_TABLE)
    
    def get_applicant_by_id(self, applicant_id: str) -> Optional[Dict]:
        """Get applicant record by ID"""
        records = self.applicants_table.all(formula=f"{{{Config.APPLICANT_ID_FIELD}}}='{applicant_id}'")
        return records[0] if records else None
    
    def get_personal_details(self, applicant_id: str) -> Optional[Dict]:
        """Get personal details for an applicant"""
        records = self.personal_details_table.all(formula=f"{{{Config.APPLICANT_ID_FIELD}}}='{applicant_id}'")
        return records[0] if records else None
    
    def get_work_experience(self, applicant_id: str) -> List[Dict]:
        """Get all work experience records for an applicant"""
        return self.work_experience_table.all(formula=f"{{{Config.APPLICANT_ID_FIELD}}}='{applicant_id}'")
    
    def get_salary_preferences(self, applicant_id: str) -> Optional[Dict]:
        """Get salary preferences for an applicant"""
        records = self.salary_preferences_table.all(formula=f"{{{Config.APPLICANT_ID_FIELD}}}='{applicant_id}'")
        return records[0] if records else None
    
    def update_compressed_json(self, applicant_id: str, compressed_json: str) -> bool:
        """Update the compressed JSON field for an applicant"""
        try:
            applicant_record = self.get_applicant_by_id(applicant_id)
            if applicant_record:
                self.applicants_table.update(applicant_record['id'], {
                    Config.COMPRESSED_JSON_FIELD: compressed_json
                })
                return True
            return False
        except Exception as e:
            print(f"Error updating compressed JSON: {e}")
            return False
    
    def update_llm_evaluation(self, applicant_id: str, summary: str, score: int, follow_ups: str) -> bool:
        """Update LLM evaluation fields for an applicant"""
        try:
            applicant_record = self.get_applicant_by_id(applicant_id)
            if applicant_record:
                self.applicants_table.update(applicant_record['id'], {
                    Config.LLM_SUMMARY_FIELD: summary,
                    Config.LLM_SCORE_FIELD: score,
                    Config.LLM_FOLLOW_UPS_FIELD: follow_ups
                })
                return True
            return False
        except Exception as e:
            print(f"Error updating LLM evaluation: {e}")
            return False
    
    def create_shortlisted_lead(self, applicant_id: str, compressed_json: str, score_reason: str) -> bool:
        """Create a new shortlisted lead record"""
        try:
            self.shortlisted_leads_table.create({
                'Applicant': [applicant_id],
                'Compressed JSON': compressed_json,
                'Score Reason': score_reason,
                'Created At': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"Error creating shortlisted lead: {e}")
            return False
    
    def upsert_personal_details(self, applicant_id: str, personal_data: Dict) -> bool:
        """Upsert personal details record"""
        try:
            existing_record = self.get_personal_details(applicant_id)
            if existing_record:
                self.personal_details_table.update(existing_record['id'], personal_data)
            else:
                personal_data[Config.APPLICANT_ID_FIELD] = applicant_id
                self.personal_details_table.create(personal_data)
            return True
        except Exception as e:
            print(f"Error upserting personal details: {e}")
            return False
    
    def upsert_work_experience(self, applicant_id: str, experience_data: List[Dict]) -> bool:
        """Upsert work experience records"""
        try:
            # Delete existing records
            existing_records = self.get_work_experience(applicant_id)
            for record in existing_records:
                self.work_experience_table.delete(record['id'])
            
            # Create new records
            for exp in experience_data:
                exp[Config.APPLICANT_ID_FIELD] = applicant_id
                self.work_experience_table.create(exp)
            return True
        except Exception as e:
            print(f"Error upserting work experience: {e}")
            return False
    
    def upsert_salary_preferences(self, applicant_id: str, salary_data: Dict) -> bool:
        """Upsert salary preferences record"""
        try:
            existing_record = self.get_salary_preferences(applicant_id)
            if existing_record:
                self.salary_preferences_table.update(existing_record['id'], salary_data)
            else:
                salary_data[Config.APPLICANT_ID_FIELD] = applicant_id
                self.salary_preferences_table.create(salary_data)
            return True
        except Exception as e:
            print(f"Error upserting salary preferences: {e}")
            return False
