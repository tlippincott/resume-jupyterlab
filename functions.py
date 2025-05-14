# functions for resume optimization
import os
from dotenv import load_dotenv
from openai import OpenAI
from markdown import markdown
from weasyprint import HTML

def create_prompt(resume_string: str, jd_string: str, comp_name_string: str, comp_info_string: str) -> str:
    """
    Creates a detailed prompt for AI-powered resume optimization based on a job description.

    This function generates a structured prompt that guides the AI to:
    - Tailor the resume bullet points and summary to match job requirements
    - Optimize for ATS systems
    - Provide actionable improvement suggestions
    - Format the output in clean Markdown

    Args:
        resume_string (str): The input resume bullet points
        jd_string (str): The target job description text
        comp_name_string (str): The company name where applying
        comp_info_string (str): The "About Us" section of the application; information about the company

    Returns:
        str: A formatted prompt string containing instructions for resume optimization
    """
    return f"""
You are a professional resume optimization expert specializing in tailoring resumes to specific job descriptions. Your goal is to optimize my resume and provide actionable suggestions for improvement to align with the target role.

Enhance given bullet points to reflect a specific job description and company, optimizing for ATS and demonstrating alignment with the company's needs.

Given resume bullet points as a string in markdown format, along with a job description, company name, and company information, your goal is to:

1. Update the resume's bullet points to align with the job description by incorporating keywords and phrases naturally, using strong action verbs, and optimizing for Applicant Tracking Systems (ATS).
2. Write a summary of 6-8 sentences that includes the company name and explains how the applicant’s skills fit the company's needs.
3. Provide actionable suggestions in three areas: additional skills, certifications or courses, and project ideas or experiences.

# Steps

1. **Analyze the Job Description**:
   - Extract key skills, action verbs, and industry-specific jargon.
   - Identify elements that are prioritized in the job description.

2. **Update Resume Bullet Points**:
   - Rewrite bullet points to naturally include keywords and phrases from the job description.
   - Use strong action verbs to describe accomplishments and responsibilities.

3. **Craft the Summary**:
   - Write a 6-8 sentence summary tailored to the company name and needs.
   - Highlight how existing skills map to the job requirements and the company’s mission or values.

4. **Suggest Improvements**:
   - List additional technical or soft skills that would strengthen the profile.
   - Recommend relevant certifications or courses to help bridge any gaps.
   - Propose project ideas or experiences that align with the desired role.

5. **Output the Enhanced Resume**:
   - Format the updated resume in clean Markdown format.
   - Include a section titled "Additional Suggestions" with detailed, actionable items for improvement.

**Input:**
- Resume in Markdown: {resume_string}
- Job Description: {jd_string}
- Company Name: {comp_name_string}
- Company Info: {comp_info_string}

# Output Format

- **Bullet Point Format**: The enhanced bullet points should be formatted in clean, readable Markdown.
- **Summary**: Write a concise, 6-8 sentence summary.
- **Additional Suggestions**: Provide detailed recommendations in a separate section.
- **Overall Structure**: Maintain original resume sections but enhance content as described.

# Examples

**Example Input:**
- Bullet Points in Markdown: "[Bullet Points String Here]"
- Job Description: "[Job Description Here]"
- Company Name: "[Company Name Here]"
- Company Info: "[Company Info Here]"

**Example Output:**

- **Enhanced Bullet Points and Summary**:
  ```markdown
  <!-- summary -->
  [Tailored summary using the company name and detailing alignment with job requirements.]

  <!-- spins -->
    - Enhanced bullet points incorporating keywords and strong action verbs.

  <!-- programmer -->
  - Enhanced skills list with relevant additions.

  <!-- analyst -->
  - Enhanced skills list with relevant additions.

  ## Additional Suggestions
  - **Skills**: Suggest additional skills here.
  - **Certifications/Courses**: Recommend relevant certifications or courses.
  - **Projects/Experiences**: Propose project ideas or experiences.

  ```
*Note: This structure is an example. Ensure to fully adapt the content relevant to the specific job and company.*

# Notes

- Leverage the company's mission and values to better align the summary with their needs.
- Prioritize clarity and simplicity in language, ensuring adherence to recruitment trends and standards.
- Customize suggestions to be highly relevant and practical for the candidate's career goals and current position.
"""

def get_resume_response(prompt: str, my_api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """
    Sends a resume optimization prompt to OpenAI's API and returns the optimized resume response.

    This function:
    - Initializes the OpenAI client
    - Makes an API call with the provided prompt
    - Returns the generated response

    Args:
        prompt (str): The formatted prompt containing resume and job description
        api_key (str): OpenAI API key for authentication
        model (str, optional): The OpenAI model to use. Defaults to "gpt-4-turbo-preview"
        temperature (float, optional): Controls randomness in the response. Defaults to 0.7

    Returns:
        str: The AI-generated optimized resume and suggestions

    Raises:
        OpenAIError: If there's an issue with the API call
    """
    # Setup API client
    client = OpenAI(api_key=my_api_key)

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Expert resume writer"},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )

    # Extract and return response
    return response.choices[0].message.content

def process_resume(resume, jd_string, comp_name_string, comp_info_string):
    """
    Process resume sections against a job description, a company name, and company information, to create optimized bullet points and a summary.

    Args:
        resume (file): A file object containing the bullet points in markdown format
        jd_string (str): The job description text to optimize the resume against
        comp_name_string (str): The company name where applying to use in the resume summary section
        comp_info_string (str): The "About Us" section of the application, also to be utilized in creating the resume summary section

    Returns:
        tuple: A tuple containing three elements:
            - str: The optimized resume sections in markdown format (for display)
            - str: The same optimized resume sections (for editing)
            - str: Suggestions for improving the resume
    """
    # read resume
    with open(resume, "r", encoding="utf-8") as file:
        resume_string = file.read()

    # create prompt
    prompt = create_prompt(resume_string, jd_string, comp_name_string, comp_info_string)

    # get the .env values
    load_dotenv()

    # assign the ChatGPT api key
    my_api_key = os.getenv("API_KEY")

    # generate response
    response_string = get_resume_response(prompt, my_api_key)
    response_list = response_string.split("## Additional Suggestions")
    
    # extract new resume and suggestions for improvement
    new_resume = response_list[0]
    suggestions = "## Additional Suggestions \n\n" +response_list[1]

    return new_resume, new_resume, suggestions

def export_resume(new_resume):
    """
    Convert a markdown resume to PDF format and save it.

    Args:
        new_resume (str): The resume content in markdown format

    Returns:
        str: A message indicating success or failure of the PDF export
    """
    try:
        # save as PDF
        output_pdf_file = "resumes/resume_new.pdf"
        
        # Convert Markdown to HTML
        html_content = markdown(new_resume)
        
        # Convert HTML to PDF and save
        HTML(string=html_content).write_pdf(output_pdf_file, stylesheets=['resumes/style.css'])

        return f"Successfully exported resume to {output_pdf_file} 🎉"
    except Exception as e:
        return f"Failed to export resume: {str(e)} 💔"
