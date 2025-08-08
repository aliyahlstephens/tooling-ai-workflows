import json
from typing import Dict, Any
from airtable_client import AirtableClient
from models import CompressedApplication
from config import Config

class JSONDecompressor:
    def __init__(self):
        self.client = AirtableClient()
    
    def decompress_applicant_data(self, applicant_id: str) -> bool:
        """
        Read compressed JSON and upsert data back to the original tables
        """
        try:
            # Get the applicant record with compressed JSON
            applicant_record = self.client.get_applicant_by_id(applicant_id)
            if not applicant_record:
                raise ValueError(f"Applicant {applicant_id} not found")
            
            compressed_json = applicant_record.get('fields', {}).get(Config.COMPRESSED_JSON_FIELD)
            if not compressed_json:
                raise ValueError(f"No compressed JSON found for applicant {applicant_id}")
            
            # Parse the compressed JSON
            if isinstance(compressed_json, str):
                data = json.loads(compressed_json)
            else:
                data = compressed_json
            
            # Validate the data structure
            compressed_app = CompressedApplication(**data)
            
            # Upsert personal details
            personal_data = {
                'Full Name': compressed_app.personal.full_name,
                'Email': compressed_app.personal.email,
                'Location': compressed_app.personal.location,
                'LinkedIn': compressed_app.personal.linkedin or ''
            }
            self.client.upsert_personal_details(applicant_id, personal_data)
            
            # Upsert work experience
            experience_data = []
            for exp in compressed_app.experience:
                experience_data.append({
                    'Company': exp.company,
                    'Title': exp.title,
                    'Start': exp.start_date,
                    'End': exp.end_date or '',
                    'Technologies': exp.technologies or ''
                })
            self.client.upsert_work_experience(applicant_id, experience_data)
            
            # Upsert salary preferences
            salary_data = {
                'Preferred Rate': compressed_app.salary.preferred_rate,
                'Minimum Rate': compressed_app.salary.minimum_rate,
                'Currency': compressed_app.salary.currency,
                'Availability (hrs/wk)': compressed_app.salary.availability_hours
            }
            self.client.upsert_salary_preferences(applicant_id, salary_data)
            
            print(f"Successfully decompressed data for applicant {applicant_id}")
            return True
            
        except Exception as e:
            print(f"Error decompressing data for applicant {applicant_id}: {e}")
            return False
    
    def decompress_from_json_file(self, json_file_path: str, applicant_id: str) -> bool:
        """
        Decompress data from a JSON file and upsert to Airtable
        """
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Validate the data structure
            compressed_app = CompressedApplication(**data)
            
            # Upsert all data
            personal_data = {
                'Full Name': compressed_app.personal.full_name,
                'Email': compressed_app.personal.email,
                'Location': compressed_app.personal.location,
                'LinkedIn': compressed_app.personal.linkedin or ''
            }
            self.client.upsert_personal_details(applicant_id, personal_data)
            
            experience_data = []
            for exp in compressed_app.experience:
                experience_data.append({
                    'Company': exp.company,
                    'Title': exp.title,
                    'Start': exp.start_date,
                    'End': exp.end_date or '',
                    'Technologies': exp.technologies or ''
                })
            self.client.upsert_work_experience(applicant_id, experience_data)
            
            salary_data = {
                'Preferred Rate': compressed_app.salary.preferred_rate,
                'Minimum Rate': compressed_app.salary.minimum_rate,
                'Currency': compressed_app.salary.currency,
                'Availability (hrs/wk)': compressed_app.salary.availability_hours
            }
            self.client.upsert_salary_preferences(applicant_id, salary_data)
            
            # Update the compressed JSON field
            json_string = json.dumps(compressed_app.dict(), indent=2)
            self.client.update_compressed_json(applicant_id, json_string)
            
            print(f"Successfully decompressed data from file for applicant {applicant_id}")
            return True
            
        except Exception as e:
            print(f"Error decompressing from file for applicant {applicant_id}: {e}")
            return False
    
    def decompress_all_applicants(self) -> Dict[str, bool]:
        """
        Decompress data for all applicants in the system
        """
        results = {}
        
        # Get all applicant records
        all_applicants = self.client.applicants_table.all()
        
        for applicant in all_applicants:
            applicant_id = applicant.get('fields', {}).get(Config.APPLICANT_ID_FIELD)
            if applicant_id:
                success = self.decompress_applicant_data(applicant_id)
                results[applicant_id] = success
        
        return results

if __name__ == "__main__":
    decompressor = JSONDecompressor()
    
    import sys
    
    if len(sys.argv) > 2:
        # Decompress from file
        json_file_path = sys.argv[1]
        applicant_id = sys.argv[2]
        success = decompressor.decompress_from_json_file(json_file_path, applicant_id)
        if success:
            print(f"✓ Successfully decompressed {applicant_id}")
        else:
            print(f"✗ Failed to decompress {applicant_id}")
    elif len(sys.argv) > 1:
        # Decompress specific applicant
        applicant_id = sys.argv[1]
        success = decompressor.decompress_applicant_data(applicant_id)
        if success:
            print(f"✓ Successfully decompressed {applicant_id}")
        else:
            print(f"✗ Failed to decompress {applicant_id}")
    else:
        # Decompress all applicants
        print("Decompressing data for all applicants...")
        results = decompressor.decompress_all_applicants()
        
        for applicant_id, success in results.items():
            if success:
                print(f"✓ Decompressed {applicant_id}")
            else:
                print(f"✗ Failed to decompress {applicant_id}")
