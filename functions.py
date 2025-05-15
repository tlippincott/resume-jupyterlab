# functions for resume optimization
import os
import re
import pathlib as Path
from openai import OpenAI

from markdown import markdown
from weasyprint import HTML, CSS

def create_prompt(resume_string: str, jd_string: str, comp_name_string: str, comp_info_string: str, job_change_bool: bool) -> str:
    """
    Creates a detailed prompt for AI-powered resume section optimization based on a job description, company name, and company information.

    This function generates a structured prompt that guides the AI to:
    - Tailor the resume bullet points and summary to match job requirements
    - Optimize for ATS systems
    - Provide actionable improvement suggestions
    - Format the output in clean Markdown to be utilized in a HTML template

    Args:
        resume_string (str): The input resume bullet points
        jd_string (str): The target job description text
        comp_name_string (str): The company name where applying
        comp_info_string (str): The "About Us" section of the application; information about the company
        job_change_bool (bool): Value to indicate if the summary section should contain a statement about looking for a more customer-focused role (e.g. Helpdesk)

    Returns:
        str: A formatted prompt string containing instructions for resume optimization
    """
    return f"""
You are a professional resume optimization expert specializing in tailoring resume bullet points and summaries to specific job descriptions. Your goal is to optimize my bullet points and provide actionable suggestions for improvement to align with the target role.

Enhance the provided resume bullet points to align with the given job description and create a tailored resume summary. The summary should leverage the enhanced bullet points, the company name, and company information while underscoring how your skills, including 15 years of experience in the technology sector, can benefit the company. If the "change" section of the markdown file is "true," also state that you are looking for a role that is more customer-focused. The uploaded files will be `resume_string` (a string), `jd_string` (a string), `comp_name_string` (a string), and `comp_info_string` (a string).

- Incorporate details from the job description (`jd_string`) to refine the bullet points, ensuring they highlight relevant skills and experiences.
- Craft a resume summary that emphasizes your alignment with the company’s needs and objectives, using the company name (`comp_name_string`) and company information (`comp_info_string`) effectively.

# Steps

1. **Analyze Job Description:** Identify key skills, experiences, and attributes the company is looking for from the `jd_string`.
2. **Modify Bullet Points:** Align each bullet point with these key areas, emphasizing relevant experience and achievements from `resume_string`.
3. **Write Resume Summary:**
   - Begin with a brief introduction summarizing your experience in the technology world.
   - Highlight how specific skills and achievements align with the company's goals.
   - If the job change value ('job_change') is "True," include a statement about seeking a more customer-focused role.
   - Conclude with the value you can bring to the company.

# Additional Suggestions

- **Additional Skills:** Identify and suggest any additional skills that could enhance your candidacy for roles in the target industry or position.
- **Certifications or Courses:** Recommend certifications or courses that can further establish your expertise and relevance to the target job market.
- **Project Ideas or Experiences:** Propose potential project ideas or experiences that can be pursued to gain or demonstrate relevant expertise.

**Input:**
- Resume in Markdown: {resume_string}
- Job Description: {jd_string}
- Company Name: {comp_name_string}
- Company Info: {comp_info_string}
- Customer Facing Role: {job_change_bool}

# Output Format

- Enhanced bullet points that directly relate to the job description (`jd_string`).
- Each bullet point begins with "<li>" and ends with "</li>" and only contains text in the middle.
- A resume summary consisting of 6-8 sentences, incorporating your experience, skills, alignment with the company’s objectives, and any additional notes about seeking a customer-focused role, using information from `comp_name_string` and `comp_info_string`.
- Additional Suggestions section detailing actionable points on additional skills, certifications/courses, and project ideas/experiences.
- Return the same updated markdown file as "enhanced-information.md" with the same number of sections and enhanced bullet points, summary, and additional suggestions placed under the correct headings. Ensure enhancements are made to the "spins", "programmer", and "analyst" sections with bullet points placed accordingly.

# Examples

## Input
- **Resume Bullet Points:** 
  - Developed applications using Agile methodologies.
  - Managed a software development team.
- **Job Description:** Seeks project managers with experience in leading technology projects and optimizing team performance.
- **Company Name:** TechVision
- **Company Information:** TechVision is a leading innovator in cloud solutions and AI technologies.
- **Job Change:** True

## Output
- **Enhanced Bullet Points:**
  <li>Successfully led cross-functional teams in developing key applications, utilizing Agile methodologies to enhance productivity and product quality.</li>
  <li>Managed a high-performing software development team, achieving a 20% increase in project delivery efficiency</li>

- **Resume Summary:**
  With over 15 years in the technology industry, I have honed my ability to lead dynamic teams and drive innovation in fast-paced environments. My experience in managing technology projects aligns seamlessly with TechVision's aim to pioneer cloud solutions and AI advancements. By optimizing team performance and fostering collaboration, I have consistently delivered top-tier results. Additionally, I am seeking a role that is more customer-focused to leverage my strategic insights in enhancing client engagement. At TechVision, I plan to leverage these skills to spearhead projects that fuel growth and differentiation in the market. My strategic perspective and commitment to quality will support your mission of innovation. I am excited about the opportunity to contribute to TechVision's success and drive future achievements.

- **Additional Suggestions:**
  - **Additional Skills:** Leadership in collaborative project environments.
  - **Certifications or Courses:** Agile Project Management Certification.
  - **Project Ideas or Experiences:** Develop an AI-focused project that aligns with cloud services.

# Notes

- Ensure that the enhanced bullet points and summary narrative maintain a formal and professional tone.
- Customize the summary to reflect a strong understanding of the company’s mission and values.
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
        str: The AI-generated optimized resume sections and suggestions

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

def process_resume(resume, jd_string, comp_name_string, comp_info_string, job_change):
    """
    Process resume sections against a job description, a company name, and company information, to create optimized bullet points and a summary.

    Args:
        resume (file): A file object containing the bullet points in markdown format
        jd_string (str): The job description text to optimize the resume against
        comp_name_string (str): The company name where applying to use in the resume summary section
        comp_info_string (str): The "About Us" section of the application, also to be utilized in creating the resume summary section
        job_change_bool (bool): Should the summary section include the statement you are looking for a job change which is more customer-focused (e.g. Helpdesk Position)

    Returns:
        tuple: A tuple containing three elements:
            - str: The optimized resume sections in markdown format (for display)
            - str: The same optimized resume sections (for editing)
            - str: Suggestions for improving the resume
    """
    # read resume
    with open(resume, "r", encoding="utf-8") as file:
        resume_string = file.read()

    # set job change boolean value based on radio button selection
    if job_change == 'Yes':
        job_change_bool:bool = True
    else:
        job_change_bool:bool = False

    # create prompt
    prompt = create_prompt(resume_string, jd_string, comp_name_string, comp_info_string, job_change_bool)

    # load the dotenv IPython extension and load the .env file
    %load_ext dotenv
    %dotenv

    # assign the ChatGPT api key
    my_api_key = os.getenv("API_KEY")

    # generate response
    response_string = get_resume_response(prompt, my_api_key)
    response_list = response_string.split("## Additional Suggestions")
    
    # extract new resume and suggestions for improvement
    new_resume_sections = response_list[0]
    suggestions = "## Additional Suggestions \n\n" + response_list[1]

    return new_resume_sections, suggestions

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
