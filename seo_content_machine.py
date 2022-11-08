import requests

SEO_CONTENT_URL = 'http://localhost:8008'
BASE_CAMPAIGN_SETTINGS_WITH_SOFT_SPIN_ID = '61d70d3a609698184e26431b'

def healthz():
    try:
        test = requests.get(SEO_CONTENT_URL)
    except:
        return False
    return test.status_code == 200


def spin(data):
    """
      Post a JSON with the following parameters to spin content using the soft spinner.
      data = {"text": "hello world","csvprotectedwords": ""}
    """
    try:
        response = requests.post(f"{SEO_CONTENT_URL}/spin", data)
    except Exception as e:
        print(e)
    return response.json()

def create_about_me(data):
    """
    Generate an aboutme. Post a JSON with the following parameters.
    data = {"keyword": "dog training"}
    """
    try:
        response = requests.post(f"{SEO_CONTENT_URL}/aboutme", data)
    except Exception as e:
        print(e)
    return response.json


def get_projects():
    """
    Retrieve a list of only article creator projects together with the keywords that have content available for retrieval.
    """
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/projects")
    except Exception as e:
        print(e)
    return response.json()


def get_all_projects(query=None):
    """
    Returns a list of ALL projects inside SCM. You can use this to manage all tasks.
    You can filter the results by adding the following parameters to the end of the url.
    group
    name
    type
    status
    eg: http://localhost:8008/all-projects?type=article%20downloader
    will return a list of all article downloader tasks.
    """
    try:
        if not query:
          response = requests.get(f"{SEO_CONTENT_URL}/all-projects")
        else:
          response = requests.get(f"{SEO_CONTENT_URL}/all-projects?{query}")
    except Exception as e:
        print(e)
        return
    return response.json()

def get_project_status(project_id=BASE_CAMPAIGN_SETTINGS_WITH_SOFT_SPIN_ID):
    """
    Returns the status of a project.
    project_id = '61d70d3a609698184e26431b'
    """
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/project/status/{project_id}")
        response.json()
    except Exception as e:
        print(e)
        return
    return response.json()

def get_project_data(project_id=BASE_CAMPAIGN_SETTINGS_WITH_SOFT_SPIN_ID):
    """
    Returns the data of a project.
    project_id = '61d70d3a609698184e26431b'
    """
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/project/data/{project_id}")
    except Exception as e:
        print(e)
    return response.json()

def get_project_content_modules(project_id=BASE_CAMPAIGN_SETTINGS_WITH_SOFT_SPIN_ID):
    """
    Returns the data of a project.
    project_id = '61d70d3a609698184e26431b'
    """
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/project/{project_id}")
    except Exception as e:
        print(e)
    return response.json()


def clone_project(project_id=BASE_CAMPAIGN_SETTINGS_WITH_SOFT_SPIN_ID):
    """
    Clone a project.JSON fail result
    """
    print(f"Cloning project {project_id}")
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/project/duplicate/{project_id}")
    except Exception as e:
        print(e)
    return response.json()

def run_project(project_id):
    """
    Run a task
    """
    try:
        response = requests.get(f"{SEO_CONTENT_URL}/project/run/{project_id}")
        response.json()
    except Exception as e:
        print(e)
    return response.json()

def update_project(project_id, data):
    """
    Update a project with new data.
    project_id = '61e055fda7378153035c3e67'
    data = {"articleKeywordsFile":["dog training tips",]}
    """
    try:
        response = requests.post(f"{SEO_CONTENT_URL}/project/data/{project_id}", json=data)
    except Exception as e:
        print(e)
    
    return response.json()

# 1. Duplicate The Base Project
# 2. Get New Project ID
# 4. Modify
# 5. Post New Project JSON
# 6. Run Project
# 7. Schedule Task To Check For Completion
# 8. Once Completed, Get Project JSON
# 9. Create New Campaign using project data

# Questions
# 1. How do I Assign Domains to the campaign
# 2. How do I Assign Subdomains to the campaign

