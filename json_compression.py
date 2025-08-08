import json
from datetime import datetime
from typing import Dict, Any
from airtable_client import AirtableClient
from models import CompressedApplication, PersonalDetails, WorkExperience, SalaryPreferences
from config import Config

class JSONCompressor:
    def __init__(self):
        self.client = AirtableClient()
    
    def compress_applicant_data(self, applicant_id: str) -> str:
        """
        Gather data from all linked tables and compress into a single JSON object
        """
        try:
            # Get data from all tables
            personal_details = self.client.get_personal_details(applicant_id)
            work_experience = self.client.get_work_experience(applicant_id)
            salary_preferences = self.client.get_salary_preferences(applicant_id)
            
            if not personal_details or not salary_preferences:
                raise ValueError(f"Missing required data for applicant {applicant_id}")
            
            # Build compressed application object
            compressed_data = {
                "personal": {
                    "full_name": personal_details.get('fields', {}).get('Full Name', ''),
                    "email": personal_details.get('fields', {}).get('Email', ''),
                    "location": personal_details.get('fields', {}).get('Location', ''),
                    "linkedin": personal_details.get('fields', {}).get('LinkedIn', '')
                },
                "experience": [
                    {
                        "company": exp.get('fields', {}).get('Company', ''),
                        "title": exp.get('fields', {}).get('Title', ''),
                        "start_date": exp.get('fields', {}).get('Start', ''),
                        "end_date": exp.get('fields', {}).get('End', ''),
                        "technologies": exp.get('fields', {}).get('Technologies', '')
                    }
                    for exp in work_experience
                ],
                "salary": {
                    "preferred_rate": salary_preferences.get('fields', {}).get('Preferred Rate', 0),
                    "minimum_rate": salary_preferences.get('fields', {}).get('Minimum Rate', 0),
                    "currency": salary_preferences.get('fields', {}).get('Currency', 'USD'),
                    "availability_hours": salary_preferences.get('fields', {}).get('Availability (hrs/wk)', 0)
                }
            }
            
            # Validate the compressed data
            compressed_app = CompressedApplication(**compressed_data)
            
            # Convert to JSON string
            json_string = json.dumps(compressed_app.dict(), indent=2)
            
            # Update the compressed JSON field in Airtable
            success = self.client.update_compressed_json(applicant_id, json_string)
            
            if success:
                print(f"Successfully compressed data for applicant {applicant_id}")
                return json_string
            else:
                raise Exception(f"Failed to update compressed JSON for applicant {applicant_id}")
                
        except Exception as e:
            print(f"Error compressing data for applicant {applicant_id}: {e}")
            raise
    
    def compress_all_applicants(self) -> Dict[str, str]:
        """
        Compress data for all applicants in the system
        """
        results = {}
        
        # Get all applicant records
        all_applicants = self.client.applicants_table.all()
        
        for applicant in all_applicants:
            applicant_id = applicant.get('fields', {}).get(Config.APPLICANT_ID_FIELD)
            if applicant_id:
                try:
                    compressed_json = self.compress_applicant_data(applicant_id)
                    results[applicant_id] = compressed_json
                except Exception as e:
                    print(f"Failed to compress applicant {applicant_id}: {e}")
                    results[applicant_id] = None
        
        return results

if __name__ == "__main__":
    compressor = JSONCompressor()
    
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Compress specific applicant
        applicant_id = sys.argv[1]
        try:
            compressed_json = compressor.compress_applicant_data(applicant_id)
            print(f"Compressed JSON for {applicant_id}:")
            print(compressed_json)
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Compress all applicants
        print("Compressing data for all applicants...")
        results = compressor.compress_all_applicants()
        
        for applicant_id, result in results.items():
            if result:
                print(f"✓ Compressed {applicant_id}")
            else:
                print(f"✗ Failed to compress {applicant_id}")
