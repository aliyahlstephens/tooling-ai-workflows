#!/usr/bin/env python3
"""
Quick Start Script for Airtable Contractor Application System
This script helps you test the system with sample data and verify setup.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv # Import the load_dotenv function

# --- ADD THIS LINE AT THE TOP TO LOAD THE .env FILE ---
load_dotenv()

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # The .env file check is no longer needed since we're loading it above
    
    # Check required environment variables
    required_vars = ['AIRTABLE_PERSONAL_ACCESS_TOKEN', 'AIRTABLE_BASE_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please make sure they are in your .env file and the file is in this directory.")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def test_airtable_connection():
    """Test Airtable API connection"""
    print("\n🔍 Testing Airtable connection...")
    
    try:
        from airtable_client import AirtableClient
        client = AirtableClient()
        
        # Try to get all applicants
        applicants = client.applicants_table.all()
        print(f"✅ Successfully connected to Airtable! Found {len(applicants)} applicants.")
        return True
        
    except Exception as e:
        print(f"❌ Airtable connection failed: {e}")
        print("Please check your personal access token and base ID.")
        return False

def test_sample_data():
    """Test with sample data"""
    print("\n🔍 Testing with sample data...")
    
    try:
        # Load sample data
        with open('sample_data.json', 'r') as f:
            sample_data = json.load(f)
        
        print("✅ Sample data loaded successfully!")
        print(f"Sample applicant: {sample_data['personal']['name']}")
        print(f"Experience: {len(sample_data['experience'])} positions")
        print(f"Rate: ${sample_data['salary']['rate']}/hr {sample_data['salary']['currency']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic functionality tests...")
    
    try:
        # Test JSON compression
        from json_compression import JSONCompressor
        compressor = JSONCompressor()
        print("✅ JSON compression module loaded")
        
        # Test shortlist automation
        from shortlist_automation import ShortlistAutomation
        automation = ShortlistAutomation()
        print("✅ Shortlist automation module loaded")
        
        # Test LLM evaluation (if OpenAI key is available)
        if os.getenv('OPENAI_API_KEY'):
            from llm_evaluation import LLMEvaluator
            evaluator = LLMEvaluator()
            print("✅ LLM evaluation module loaded")
        else:
            print("⚠️  OpenAI API key not found - LLM evaluation will be skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading modules: {e}")
        return False

def create_sample_applicant():
    """Create a sample applicant in Airtable for testing"""
    print("\n📝 Creating sample applicant for testing...")
    
    try:
        from airtable_client import AirtableClient
        client = AirtableClient()
        
        # Create sample applicant ID
        sample_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create applicant record
        applicant_record = client.applicants_table.create({
            'Applicant ID': sample_id,
            'Shortlist Status': 'Pending'
        })
        
        print(f"✅ Created sample applicant: {sample_id}")
        print("You can now test the automation with this ID.")
        return sample_id
        
    except Exception as e:
        print(f"❌ Error creating sample applicant: {e}")
        return None

def main():
    """Main quick start function"""
    print("=" * 60)
    print("🚀 Airtable Contractor Application System - Quick Start")
    print("=" * 60)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment setup incomplete. Please fix the issues above.")
        return
    
    # Step 2: Test Airtable connection
    if not test_airtable_connection():
        print("\n❌ Airtable connection failed. Please check your API keys.")
        return
    
    # Step 3: Test sample data
    if not test_sample_data():
        print("\n❌ Sample data test failed.")
        return
    
    # Step 4: Run basic tests
    if not run_basic_tests():
        print("\n❌ Basic functionality tests failed.")
        return
    
    # Step 5: Create sample applicant
    sample_id = create_sample_applicant()
    
    print("\n" + "=" * 60)
    print("✅ Quick start completed successfully!")
    print("=" * 60)
    
    if sample_id:
        print(f"\n🎯 Next steps:")
        print(f"1. Test compression: python main.py compress --applicant-id {sample_id}")
        print(f"2. Test decompression: python main.py decompress --applicant-id {sample_id}")
        print(f"3. Test shortlisting: python main.py shortlist --applicant-id {sample_id}")
        if os.getenv('OPENAI_API_KEY'):
            print(f"4. Test LLM evaluation: python main.py evaluate --applicant-id {sample_id}")
        print(f"5. Run full pipeline: python main.py full-pipeline")
    
    print(f"\n📚 For detailed setup instructions, see: airtable_setup_guide.md")
    print(f"📖 For full documentation, see: README.md")

if __name__ == "__main__":
    main()
