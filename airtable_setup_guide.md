# Airtable Setup Guide

This guide will walk you through setting up the Airtable base for the contractor application automation system.

## Step 1: Create New Airtable Base

1. Go to [airtable.com](https://airtable.com)
2. Click "Add a base" → "Start from scratch"
3. Name your base: "Contractor Applications"

## Step 2: Create the Tables

### Table 1: Applicants (Parent Table)

1. **Rename the first table** to "Applicants"
2. **Add these fields:**

| Field Name | Field Type | Options |
|------------|------------|---------|
| Applicant ID | Single line text | Primary key field |
| Compressed JSON | Long text | Stores consolidated data |
| Shortlist Status | Single select | Options: Pending, Shortlisted, Rejected |
| LLM Summary | Long text | AI-generated summary |
| LLM Score | Number | 1-10 scale |
| LLM Follow-Ups | Long text | Suggested questions |

### Table 2: Personal Details

1. **Create new table** named "Personal Details"
2. **Add these fields:**

| Field Name | Field Type | Options |
|------------|------------|---------|
| Full Name | Single line text | |
| Email | Email | |
| Location | Single line text | |
| LinkedIn | URL | |
| Applicant ID | Link to another record | Link to "Applicants" table |

### Table 3: Work Experience

1. **Create new table** named "Work Experience"
2. **Add these fields:**

| Field Name | Field Type | Options |
|------------|------------|---------|
| Company | Single line text | |
| Title | Single line text | |
| Start | Date | |
| End | Date | |
| Technologies | Long text | |
| Applicant ID | Link to another record | Link to "Applicants" table |

### Table 4: Salary Preferences

1. **Create new table** named "Salary Preferences"
2. **Add these fields:**

| Field Name | Field Type | Options |
|------------|------------|---------|
| Preferred Rate | Number | |
| Minimum Rate | Number | |
| Currency | Single select | Options: USD, EUR, GBP, CAD, INR |
| Availability (hrs/wk) | Number | |
| Applicant ID | Link to another record | Link to "Applicants" table |

### Table 5: Shortlisted Leads

1. **Create new table** named "Shortlisted Leads"
2. **Add these fields:**

| Field Name | Field Type | Options |
|------------|------------|---------|
| Applicant | Link to another record | Link to "Applicants" table |
| Compressed JSON | Long text | |
| Score Reason | Long text | |
| Created At | Date | Auto-generated |

## Step 3: Configure Field Settings

### For Applicant ID Fields:
1. In each child table, click on the "Applicant ID" field
2. In the field settings, select "Link to another record"
3. Choose "Applicants" as the linked table
4. Enable "Allow linking to multiple records" if needed

### For Date Fields:
1. Set "Start" and "End" fields to Date type
2. Configure date format as YYYY-MM-DD
3. For "End" field, you can leave it empty for current positions

### For Number Fields:
1. Set "Preferred Rate", "Minimum Rate", and "Availability (hrs/wk)" to Number type
2. Configure decimal places as needed (0 for whole numbers)

## Step 4: Create Forms

### Form 1: Personal Details Form
1. Go to "Personal Details" table
2. Click "Form" in the top right
3. Configure the form to include:
   - Full Name (required)
   - Email (required)
   - Location (required)
   - LinkedIn (optional)
4. Save the form

### Form 2: Work Experience Form
1. Go to "Work Experience" table
2. Click "Form" in the top right
3. Configure the form to include:
   - Company (required)
   - Title (required)
   - Start Date (required)
   - End Date (optional)
   - Technologies (optional)
4. Save the form

### Form 3: Salary Preferences Form
1. Go to "Salary Preferences" table
2. Click "Form" in the top right
3. Configure the form to include:
   - Preferred Rate (required)
   - Minimum Rate (required)
   - Currency (required)
   - Availability (hrs/wk) (required)
4. Save the form

## Step 5: Get API Information

### Get Your Personal Access Token:
1. Go to [airtable.com/account](https://airtable.com/account)
2. Click on "Personal access tokens" in the left sidebar
3. Click "Create new token"
4. Give your token a name (e.g., "Contractor Applications Automation")
5. Select the scopes you need:
   - `data.records:read` (to read records)
   - `data.records:write` (to create/update records)
   - `schema.bases:read` (to read base structure)
6. Click "Create token"
7. **Copy the token immediately** (you won't be able to see it again)

### Get Your Base ID:
1. Go to [airtable.com/api](https://airtable.com/api)
2. Find your base in the list
3. Copy the Base ID (it's in the URL: `https://airtable.com/appXXXXXXXXXXXXXX`)

## Step 6: Test the Setup

### Add Sample Data:
1. Create a test applicant in the "Applicants" table
2. Add sample personal details, work experience, and salary preferences
3. Use the sample data from `sample_data.json` as a reference

### Test the Automation:
1. Set up your `.env` file with the API keys
2. Run the compression script:
   ```bash
   python main.py compress --applicant-id YOUR_TEST_ID
   ```
3. Verify the compressed JSON appears in the Applicants table

## Step 7: Configure Automation (Optional)

### Set up Airtable Automations:
1. Go to the "Automations" tab in your base
2. Create triggers for when records are added/updated
3. Configure actions to run your Python scripts

### Example Automation Flow:
1. **Trigger**: New record in "Personal Details"
2. **Action**: Run compression script
3. **Trigger**: Compressed JSON updated
4. **Action**: Run LLM evaluation
5. **Trigger**: LLM evaluation complete
6. **Action**: Run shortlist evaluation

## Troubleshooting

### Common Issues:

1. **Field Name Mismatches**
   - Ensure field names exactly match those in `config.py`
   - Check for extra spaces or special characters

2. **API Permission Errors**
   - Verify your personal access token has the correct scopes
   - Check that the base ID is correct
   - Ensure the token hasn't expired

3. **Link Field Issues**
   - Ensure all "Applicant ID" fields are properly linked
   - Test the links by creating sample records

4. **Date Format Issues**
   - Use YYYY-MM-DD format for all dates
   - Leave end dates empty for current positions

### Testing Checklist:

- [ ] All 5 tables created with correct names
- [ ] All required fields added with correct types
- [ ] Applicant ID fields properly linked
- [ ] Forms created and accessible
- [ ] Personal access token and base ID obtained
- [ ] Sample data added successfully
- [ ] Compression script runs without errors
- [ ] LLM evaluation works (requires OpenAI API key)
- [ ] Shortlist automation functions correctly

## Next Steps

After completing the setup:

1. **Install the Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your environment**:
   - Create `.env` file with personal access token
   - Test with sample data

3. **Run the full pipeline**:
   ```bash
   python main.py full-pipeline
   ```

4. **Monitor and optimize**:
   - Check automation logs
   - Adjust criteria as needed
   - Scale up for production use

## Support

If you encounter issues during setup:
1. Check the troubleshooting section above
2. Verify all field names match exactly
3. Test with the sample data provided
4. Review the error messages for specific guidance
