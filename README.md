# Airtable Contractor Application Automation System

A comprehensive automation system for managing contractor applications using Airtable with Python automation scripts for data compression, LLM evaluation, and shortlisting.

## Overview

This system provides:
- **Multi-table data collection** through Airtable forms
- **JSON compression/decompression** for efficient data storage
- **Automated shortlisting** based on configurable criteria
- **LLM-powered evaluation** using OpenAI for candidate analysis
- **Complete automation pipeline** for end-to-end processing

## System Architecture

### Airtable Schema

The system uses 5 interconnected tables:

1. **Applicants** (Parent Table)
   - `Applicant ID` (Primary Key)
   - `Compressed JSON` (Stores consolidated data)
   - `Shortlist Status`
   - `LLM Summary`
   - `LLM Score`
   - `LLM Follow-Ups`

2. **Personal Details** (Child Table)
   - `Full Name`
   - `Email`
   - `Location`
   - `LinkedIn`
   - `Applicant ID` (Link to parent)

3. **Work Experience** (Child Table)
   - `Company`
   - `Title`
   - `Start Date`
   - `End Date`
   - `Technologies`
   - `Applicant ID` (Link to parent)

4. **Salary Preferences** (Child Table)
   - `Preferred Rate`
   - `Minimum Rate`
   - `Currency`
   - `Availability (hrs/wk)`
   - `Applicant ID` (Link to parent)

5. **Shortlisted Leads** (Auto-populated)
   - `Applicant` (Link to Applicants)
   - `Compressed JSON`
   - `Score Reason`
   - `Created At`

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your API keys:

```env
# Airtable Configuration
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_personal_access_token_here
AIRTABLE_BASE_ID=your_base_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
LLM_MODEL=gpt-4
MAX_TOKENS=500
TEMPERATURE=0.3
```

### 3. Airtable Setup

1. Create a new Airtable base
2. Create the 5 tables with the specified fields
3. Set up the linking relationships between tables
4. Create forms for data collection (Personal Details, Work Experience, Salary Preferences)

## Usage

### Command Line Interface

The main automation script provides several operations:

```bash
# Compress data for all applicants
python main.py compress

# Compress data for specific applicant
python main.py compress --applicant-id APP001

# Decompress data for all applicants
python main.py decompress

# Decompress from JSON file
python main.py decompress --json-file data.json --applicant-id APP001

# Evaluate shortlist criteria for all applicants
python main.py shortlist

# Evaluate specific applicant for shortlisting
python main.py shortlist --applicant-id APP001

# Run LLM evaluation for all applicants
python main.py evaluate

# Evaluate specific applicant with LLM
python main.py evaluate --applicant-id APP001

# Run full automation pipeline
python main.py full-pipeline
```

### Individual Scripts

You can also run individual automation scripts:

```bash
# JSON Compression
python json_compression.py [applicant_id]

# JSON Decompression
python json_decompression.py [applicant_id]
python json_decompression.py [json_file] [applicant_id]

# Shortlist Automation
python shortlist_automation.py [applicant_id]

# LLM Evaluation
python llm_evaluation.py [applicant_id]
```

## Automation Features

### 1. JSON Compression

- Gathers data from all linked tables
- Validates data structure using Pydantic models
- Creates a single JSON object for efficient storage
- Updates the `Compressed JSON` field in Airtable

**Example Output:**
```json
{
  "personal": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "location": "NYC",
    "linkedin": "https://linkedin.com/in/janedoe"
  },
  "experience": [
    {
      "company": "Google",
      "title": "Software Engineer",
      "start": "2020-01-15",
      "end": "2023-06-30",
      "technologies": "Python, JavaScript, React"
    }
  ],
  "salary": {
    "rate": 100,
    "currency": "USD",
    "availability": 25
  }
}
```

### 2. JSON Decompression

- Reads compressed JSON from Airtable
- Validates data structure
- Upserts data back to original tables
- Maintains data integrity and relationships

### 3. Shortlist Automation

Evaluates applicants based on configurable criteria:

**Experience Criteria:**
- ≥ 4 years total experience OR
- Worked at tier-1 company (Google, Meta, OpenAI, etc.)

**Compensation Criteria:**
- Preferred rate ≤ $100 USD/hour AND
- Availability ≥ 20 hours/week

**Location Criteria:**
- Located in US, Canada, UK, Germany, or India

### 4. LLM Evaluation

Uses OpenAI to automatically:
- Generate 75-word candidate summaries
- Assign quality scores (1-10)
- Identify data gaps and inconsistencies
- Suggest follow-up questions

**Sample LLM Output:**
```
Summary: Full-stack SWE with 5 yrs experience at Google and Meta...
Score: 8
Issues: Missing portfolio link, unclear availability after next month
Follow-Ups: • Can you confirm availability after next month?
           • Have you led any production ML launches?
```

## Configuration

### Shortlist Criteria

Edit `config.py` to customize shortlist criteria:

```python
# Tier-1 companies
TIER_1_COMPANIES = ['Google', 'Meta', 'OpenAI', 'Microsoft', 'Apple', 'Amazon', 'Netflix']

# Eligible locations
ELIGIBLE_LOCATIONS = ['US', 'Canada', 'UK', 'Germany', 'India']

# Rate and availability thresholds
MAX_HOURLY_RATE = 100
MIN_AVAILABILITY_HOURS = 20
MIN_EXPERIENCE_YEARS = 4
```

### LLM Configuration

Customize LLM settings in `config.py`:

```python
LLM_MODEL = 'gpt-4'  # or 'gpt-3.5-turbo'
MAX_TOKENS = 500
TEMPERATURE = 0.3
```

## Error Handling & Reliability

### Retry Logic
- LLM API calls include exponential backoff
- Up to 3 retry attempts for failed operations
- Graceful error handling with detailed logging

### Data Validation
- Pydantic models ensure data integrity
- Comprehensive error messages for debugging
- Safe fallbacks for missing or invalid data

### API Rate Limiting
- Built-in delays between API calls
- Configurable timeouts and limits
- Respects Airtable and OpenAI rate limits

## Security Best Practices

1. **API Key Management**
   - Store keys in environment variables
   - Never hardcode sensitive data
   - Use `.env` files for local development

2. **Data Privacy**
   - All data processing is local
   - No data stored in external services
   - Secure API communication

3. **Access Control**
   - Airtable permissions control data access
   - Script-level validation prevents unauthorized operations

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys in `.env` file
   - Check Airtable base permissions
   - Ensure OpenAI API key is valid

2. **Data Validation Errors**
   - Check field names match Airtable exactly
   - Verify data types (dates, numbers, etc.)
   - Review Pydantic model requirements

3. **LLM Evaluation Failures**
   - Check OpenAI API quota
   - Verify model name in config
   - Review token limits

### Debug Mode

Enable detailed logging by modifying scripts to include:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending the System

### Adding New Criteria

1. Update `ShortlistCriteria` model in `models.py`
2. Modify evaluation logic in `shortlist_automation.py`
3. Update configuration in `config.py`

### Custom LLM Prompts

1. Modify `create_evaluation_prompt()` in `llm_evaluation.py`
2. Update response parsing logic
3. Test with sample data

### Additional Tables

1. Add table configuration to `config.py`
2. Update `AirtableClient` class
3. Modify compression/decompression logic

## Performance Considerations

- **Batch Processing**: Scripts can handle multiple applicants efficiently
- **API Optimization**: Minimizes API calls through smart caching
- **Memory Management**: Processes data in chunks for large datasets
- **Parallel Processing**: Can be extended for concurrent operations

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs for specific details
3. Verify configuration settings
4. Test with sample data first

## License

This project is provided as-is for educational and demonstration purposes.
