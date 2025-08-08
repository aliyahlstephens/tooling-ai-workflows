import json
import time
import openai
from typing import Dict, Optional
from airtable_client import AirtableClient
from models import LLMEvaluation
from config import Config

class LLMEvaluator:
    def __init__(self):
        self.client = AirtableClient()
        openai.api_key = Config.OPENAI_API_KEY
    
    def create_evaluation_prompt(self, applicant_json: str) -> str:
        """
        Create the prompt for LLM evaluation
        """
        return f"""You are a recruiting analyst. Given this JSON applicant profile, do four things:
1. Provide a concise 75-word summary.
2. Rate overall candidate quality from 1-10 (higher is better).
3. List any data gaps or inconsistencies you notice.
4. Suggest up to three follow-up questions to clarify gaps.

Applicant JSON:
{applicant_json}

Return exactly:
Summary: <text>
Score: <integer>
Issues: <comma-separated list or 'None'>
Follow-Ups: <bullet list>"""
    
    def parse_llm_response(self, response: str) -> LLMEvaluation:
        """
        Parse the LLM response into structured data
        """
        try:
            lines = response.strip().split('\n')
            summary = ""
            score = 5  # Default score
            issues = []
            follow_ups = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Summary:'):
                    summary = line.replace('Summary:', '').strip()
                elif line.startswith('Score:'):
                    try:
                        score = int(line.replace('Score:', '').strip())
                    except ValueError:
                        score = 5
                elif line.startswith('Issues:'):
                    issues_text = line.replace('Issues:', '').strip()
                    if issues_text.lower() != 'none':
                        issues = [issue.strip() for issue in issues_text.split(',')]
                elif line.startswith('Follow-Ups:'):
                    # Parse bullet points
                    follow_ups_text = line.replace('Follow-Ups:', '').strip()
                    if follow_ups_text:
                        follow_ups = [f.strip().lstrip('•').strip() for f in follow_ups_text.split('\n') if f.strip()]
            
            return LLMEvaluation(
                summary=summary or "No summary provided",
                score=score,
                issues=issues,
                follow_ups=follow_ups
            )
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return LLMEvaluation(
                summary="Error parsing LLM response",
                score=5,
                issues=["LLM response parsing failed"],
                follow_ups=["Please manually review this applicant"]
            )
    
    def evaluate_applicant_with_retry(self, applicant_id: str, max_retries: int = 3) -> Optional[LLMEvaluation]:
        """
        Evaluate an applicant using LLM with retry logic
        """
        try:
            # Get compressed JSON
            applicant_record = self.client.get_applicant_by_id(applicant_id)
            if not applicant_record:
                print(f"Applicant {applicant_id} not found")
                return None
            
            compressed_json = applicant_record.get('fields', {}).get(Config.COMPRESSED_JSON_FIELD)
            if not compressed_json:
                print(f"No compressed JSON found for applicant {applicant_id}")
                return None
            
            # Convert to string if needed
            if not isinstance(compressed_json, str):
                compressed_json = json.dumps(compressed_json, indent=2)
            
            # Create prompt
            prompt = self.create_evaluation_prompt(compressed_json)
            
            # Try with exponential backoff
            for attempt in range(max_retries):
                try:
                    response = openai.ChatCompletion.create(
                        model=Config.LLM_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a professional recruiting analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=Config.MAX_TOKENS,
                        temperature=Config.TEMPERATURE
                    )
                    
                    llm_response = response.choices[0].message.content.strip()
                    evaluation = self.parse_llm_response(llm_response)
                    
                    print(f"✓ Successfully evaluated applicant {applicant_id} (attempt {attempt + 1})")
                    return evaluation
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for applicant {applicant_id}: {e}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"All attempts failed for applicant {applicant_id}")
                        return None
            
        except Exception as e:
            print(f"Error evaluating applicant {applicant_id}: {e}")
            return None
    
    def update_applicant_evaluation(self, applicant_id: str) -> bool:
        """
        Evaluate an applicant and update the LLM fields in Airtable
        """
        try:
            evaluation = self.evaluate_applicant_with_retry(applicant_id)
            
            if evaluation:
                # Update Airtable
                success = self.client.update_llm_evaluation(
                    applicant_id,
                    evaluation.summary,
                    evaluation.score,
                    '\n'.join(evaluation.follow_ups)
                )
                
                if success:
                    print(f"✓ Updated LLM evaluation for applicant {applicant_id}")
                    print(f"  Summary: {evaluation.summary[:50]}...")
                    print(f"  Score: {evaluation.score}/10")
                    print(f"  Issues: {len(evaluation.issues)} found")
                    print(f"  Follow-ups: {len(evaluation.follow_ups)} suggested")
                    return True
                else:
                    print(f"✗ Failed to update LLM evaluation for applicant {applicant_id}")
                    return False
            else:
                print(f"✗ No evaluation generated for applicant {applicant_id}")
                return False
                
        except Exception as e:
            print(f"Error updating evaluation for applicant {applicant_id}: {e}")
            return False
    
    def evaluate_all_applicants(self) -> Dict[str, bool]:
        """
        Evaluate all applicants in the system
        """
        results = {}
        
        # Get all applicant records
        all_applicants = self.client.applicants_table.all()
        
        for applicant in all_applicants:
            applicant_id = applicant.get('fields', {}).get(Config.APPLICANT_ID_FIELD)
            if applicant_id:
                success = self.update_applicant_evaluation(applicant_id)
                results[applicant_id] = success
        
        return results
    
    def get_evaluation_summary(self) -> Dict:
        """
        Get a summary of LLM evaluations
        """
        try:
            all_applicants = self.client.applicants_table.all()
            
            summary = {
                'total_applicants': len(all_applicants),
                'evaluated': 0,
                'average_score': 0.0,
                'score_distribution': {}
            }
            
            total_score = 0
            for applicant in all_applicants:
                llm_score = applicant.get('fields', {}).get(Config.LLM_SCORE_FIELD)
                if llm_score:
                    summary['evaluated'] += 1
                    total_score += llm_score
                    
                    # Count score distribution
                    score = int(llm_score)
                    summary['score_distribution'][score] = summary['score_distribution'].get(score, 0) + 1
            
            if summary['evaluated'] > 0:
                summary['average_score'] = total_score / summary['evaluated']
            
            return summary
            
        except Exception as e:
            print(f"Error getting evaluation summary: {e}")
            return {'total_applicants': 0, 'evaluated': 0, 'average_score': 0.0, 'score_distribution': {}}

if __name__ == "__main__":
    evaluator = LLMEvaluator()
    
    import sys
    
    if len(sys.argv) > 1:
        # Evaluate specific applicant
        applicant_id = sys.argv[1]
        success = evaluator.update_applicant_evaluation(applicant_id)
        if success:
            print(f"✓ Successfully evaluated {applicant_id}")
        else:
            print(f"✗ Failed to evaluate {applicant_id}")
    else:
        # Evaluate all applicants
        print("Evaluating all applicants with LLM...")
        results = evaluator.evaluate_all_applicants()
        
        evaluated_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\nEvaluation Summary:")
        print(f"Total applicants: {total_count}")
        print(f"Successfully evaluated: {evaluated_count}")
        print(f"Success rate: {(evaluated_count/total_count*100):.1f}%" if total_count > 0 else "No applicants found")
        
        # Get detailed summary
        summary = evaluator.get_evaluation_summary()
        print(f"\nDetailed Summary:")
        print(f"Total applicants: {summary['total_applicants']}")
        print(f"Evaluated: {summary['evaluated']}")
        print(f"Average score: {summary['average_score']:.1f}/10")
        print(f"Score distribution: {summary['score_distribution']}")
