import json
from datetime import datetime, date
from typing import Dict, List, Tuple
from airtable_client import AirtableClient
from models import CompressedApplication, ShortlistCriteria
from config import Config

class ShortlistAutomation:
    def __init__(self):
        self.client = AirtableClient()
    
    def calculate_experience_years(self, experience_data: List[Dict]) -> Tuple[float, bool]:
        """
        Calculate total years of experience and check for tier-1 company experience
        """
        total_years = 0.0
        tier_1_experience = False
        
        for exp in experience_data:
            company = exp.get('company', '').lower()
            start_date = exp.get('start', '')
            end_date = exp.get('end', '')
            
            # Check for tier-1 company
            if any(tier_company.lower() in company for tier_company in Config.TIER_1_COMPANIES):
                tier_1_experience = True
            
            # Calculate duration
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                if end_date and end_date.lower() != 'present':
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                else:
                    end = date.today()
                
                duration = (end - start).days / 365.25
                total_years += duration
            except (ValueError, TypeError):
                # Skip invalid dates
                continue
        
        return total_years, tier_1_experience
    
    def evaluate_applicant(self, applicant_id: str) -> ShortlistCriteria:
        """
        Evaluate an applicant against shortlist criteria
        """
        try:
            # Get compressed JSON
            applicant_record = self.client.get_applicant_by_id(applicant_id)
            if not applicant_record:
                raise ValueError(f"Applicant {applicant_id} not found")
            
            compressed_json = applicant_record.get('fields', {}).get(Config.COMPRESSED_JSON_FIELD)
            if not compressed_json:
                raise ValueError(f"No compressed JSON found for applicant {applicant_id}")
            
            # Parse JSON
            if isinstance(compressed_json, str):
                data = json.loads(compressed_json)
            else:
                data = compressed_json
            
            # Validate data structure
            compressed_app = CompressedApplication(**data)
            
            # Evaluate experience criteria
            total_years, tier_1_experience = self.calculate_experience_years(compressed_app.experience)
            experience_qualified = (total_years >= Config.MIN_EXPERIENCE_YEARS) or tier_1_experience
            
            # Evaluate compensation criteria
            preferred_rate = compressed_app.salary.preferred_rate
            availability = compressed_app.salary.availability_hours
            currency = compressed_app.salary.currency.upper()
            
            # Convert to USD if needed (simplified conversion)
            usd_rate = preferred_rate
            if currency != 'USD':
                # Simple conversion rates (in production, use real-time rates)
                conversion_rates = {'EUR': 1.1, 'GBP': 1.3, 'CAD': 0.75, 'INR': 0.012}
                usd_rate = preferred_rate * conversion_rates.get(currency, 1.0)
            
            compensation_qualified = (usd_rate <= Config.MAX_HOURLY_RATE) and (availability >= Config.MIN_AVAILABILITY_HOURS)
            
            # Evaluate location criteria
            location = compressed_app.personal.location.upper()
            location_qualified = any(eligible_loc.upper() in location for eligible_loc in Config.ELIGIBLE_LOCATIONS)
            
            # Build score reason
            reasons = []
            if experience_qualified:
                if tier_1_experience:
                    reasons.append("Has tier-1 company experience")
                else:
                    reasons.append(f"Has {total_years:.1f} years of experience")
            else:
                reasons.append(f"Insufficient experience ({total_years:.1f} years)")
            
            if compensation_qualified:
                reasons.append(f"Rate ${usd_rate:.0f}/hr USD, {availability} hrs/week available")
            else:
                reasons.append(f"Rate too high (${usd_rate:.0f}/hr) or insufficient availability ({availability} hrs/week)")
            
            if location_qualified:
                reasons.append(f"Located in {location}")
            else:
                reasons.append(f"Location {location} not eligible")
            
            score_reason = " | ".join(reasons)
            
            return ShortlistCriteria(
                experience_qualified=experience_qualified,
                compensation_qualified=compensation_qualified,
                location_qualified=location_qualified,
                total_years_experience=total_years,
                tier_1_experience=tier_1_experience,
                score_reason=score_reason
            )
            
        except Exception as e:
            print(f"Error evaluating applicant {applicant_id}: {e}")
            return ShortlistCriteria(
                experience_qualified=False,
                compensation_qualified=False,
                location_qualified=False,
                total_years_experience=0.0,
                tier_1_experience=False,
                score_reason=f"Error during evaluation: {str(e)}"
            )
    
    def shortlist_applicant(self, applicant_id: str) -> bool:
        """
        Evaluate and shortlist an applicant if they meet all criteria
        """
        try:
            criteria = self.evaluate_applicant(applicant_id)
            
            # Check if all criteria are met
            if criteria.experience_qualified and criteria.compensation_qualified and criteria.location_qualified:
                # Get compressed JSON
                applicant_record = self.client.get_applicant_by_id(applicant_id)
                compressed_json = applicant_record.get('fields', {}).get(Config.COMPRESSED_JSON_FIELD)
                
                # Create shortlisted lead
                success = self.client.create_shortlisted_lead(applicant_id, compressed_json, criteria.score_reason)
                
                if success:
                    print(f"✓ Shortlisted applicant {applicant_id}: {criteria.score_reason}")
                    return True
                else:
                    print(f"✗ Failed to create shortlisted lead for {applicant_id}")
                    return False
            else:
                print(f"✗ Applicant {applicant_id} does not meet shortlist criteria: {criteria.score_reason}")
                return False
                
        except Exception as e:
            print(f"Error shortlisting applicant {applicant_id}: {e}")
            return False
    
    def shortlist_all_applicants(self) -> Dict[str, bool]:
        """
        Evaluate and shortlist all applicants in the system
        """
        results = {}
        
        # Get all applicant records
        all_applicants = self.client.applicants_table.all()
        
        for applicant in all_applicants:
            applicant_id = applicant.get('fields', {}).get(Config.APPLICANT_ID_FIELD)
            if applicant_id:
                success = self.shortlist_applicant(applicant_id)
                results[applicant_id] = success
        
        return results
    
    def get_shortlist_summary(self) -> Dict:
        """
        Get a summary of shortlisted applicants
        """
        try:
            shortlisted_leads = self.client.shortlisted_leads_table.all()
            
            summary = {
                'total_shortlisted': len(shortlisted_leads),
                'applicants': []
            }
            
            for lead in shortlisted_leads:
                applicant_id = lead.get('fields', {}).get('Applicant', [''])[0]
                score_reason = lead.get('fields', {}).get('Score Reason', '')
                created_at = lead.get('fields', {}).get('Created At', '')
                
                summary['applicants'].append({
                    'applicant_id': applicant_id,
                    'score_reason': score_reason,
                    'created_at': created_at
                })
            
            return summary
            
        except Exception as e:
            print(f"Error getting shortlist summary: {e}")
            return {'total_shortlisted': 0, 'applicants': []}

if __name__ == "__main__":
    automation = ShortlistAutomation()
    
    import sys
    
    if len(sys.argv) > 1:
        # Shortlist specific applicant
        applicant_id = sys.argv[1]
        success = automation.shortlist_applicant(applicant_id)
        if success:
            print(f"✓ Successfully shortlisted {applicant_id}")
        else:
            print(f"✗ Failed to shortlist {applicant_id}")
    else:
        # Shortlist all applicants
        print("Evaluating and shortlisting all applicants...")
        results = automation.shortlist_all_applicants()
        
        shortlisted_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\nShortlist Summary:")
        print(f"Total applicants: {total_count}")
        print(f"Shortlisted: {shortlisted_count}")
        print(f"Success rate: {(shortlisted_count/total_count*100):.1f}%" if total_count > 0 else "No applicants found")
        
        # Get detailed summary
        summary = automation.get_shortlist_summary()
        print(f"\nDetailed Summary:")
        print(f"Total shortlisted leads: {summary['total_shortlisted']}")
        
        for applicant in summary['applicants']:
            print(f"- {applicant['applicant_id']}: {applicant['score_reason']}")
