# Introduction

This repository provides a structured template for starting a new analytical project. It is designed with the following priorities in mind:

1. **Reproducibility**: Ensure that analyses are easily reproducible with a clear folder structure and environmental setup guidelines.
2. **Security**: Prevent sensitive information, such as data, API keys, and passwords, from being uploaded to GitHub.

The following sections require git to be installed on your machine. If you have not set up the git, please follow the instructions [here](https://docs.github.com/en/get-started/quickstart/set-up-git)

## Install and Set Up the GitHub Connection

To create a new repository based on this template, follow the steps below.

#### Notes:
1. Replace `YOUR_PROJECT_NAME` with the desired name of your project.
2. Replace `YOUR_GITHUB_REPO_URL` with the URL of your newly created GitHub repository.


### Step 1: Clone the Template Repository

The following commands will clone the template repository, rename it to your project name, and remove the existing Git history.

#### For macOS/Linux (Bash):
```bash
# Clone the template repository
git clone https://github.com/hirotaka-i/new_analysis.git 

# Rename the folder. Substitute YOUR_PROJECT_NAME with your desired project name
mv new_analysis YOUR_PROJECT_NAME 

# Change directory to the new project folder
cd YOUR_PROJECT_NAME

# Remove the existing Git history
rm -rf .git
```

#### For Windows PowerShell:
```powershell
# Clone the template repository
git clone https://github.com/hirotaka-i/new_analysis.git 

# Rename the folder. Substitute YOUR_PROJECT_NAME with your desired project name
Rename-Item -Path "new_analysis" -NewName "YOUR_PROJECT_NAME" 

# Change directory to the new project folder
Set-Location "YOUR_PROJECT_NAME"

# Remove the existing Git history
Remove-Item -Recurse -Force ".git"
```

---

### Step 2: Initialize and Set Up the New Repository

Once the template is set up, create a new repository on [GitHub](https://github.com) and copy the repository URL. Use the commands below to initialize the repository, link it to your new remote repository, and push the initial commit.

```bash
# Initialize a new Git repository
git init 

# Connect to your new remote repository (replace YOUR_GITHUB_REPO_URL with your repository URL)
git remote add origin YOUR_GITHUB_REPO_URL 

# Stage all files for the initial commit
git add .

# Commit the changes
git commit -m "Initial commit"

# Rename the default branch to 'main'
git branch -M main

# Push the changes to the remote repository
git push -u origin main
```

---
### Note
If this is the first time to push git to the remote repository, you will be asked to provide the username and password. 
```
git config --global user.name "Your Name"
git config --global user.email "Your Email"
```
---




## Environment Setup

For Python projects, the recommended way to manage the environment is by using Python’s built-in `venv` module. Follow the steps below to set up your environment, manage dependencies, and ensure consistency across development environments.

### Step 1: Create a Virtual Environment

Run the following commands inside your project folder:

#### macOS/Linux:
```bash
# Create a virtual environment in the .venv directory
python3 -m venv .venv # or "python -m venv .venv"

# Activate the virtual environment
source .venv/bin/activate 
```

#### Windows (PowerShell):
```powershell
# Create a virtual environment in the .venv directory
python -m venv .venv 

# Activate the virtual environment
.venv\Scripts\Activate 
```

#### Package Installation:
```
# Upgrade pip
python -m pip install --upgrade pip 

# Install dependencies listed in requirements.txt
python -m pip install -r requirements.txt 
```

> **Note**: `requirements.txt` is to to document dependencies for the project. This allows others to replicate your environment easily. Ensure `requirements.txt` includes all necessary packages for your project. Modify it as needed. (see the following section to update it)
---



#### Additional notes:

##### Install New Packages and Update Dependencies

To add new packages to your environment and update the `requirements.txt` file:

```bash
pip install <package_name>   # Install a new package
pip freeze > requirements.txt # Update dependencies in requirements.txt
```

##### Deactivate the Virtual Environment:
When you're done working, deactivate the virtual environment with:

```bash
deactivate
```

##### Specify Python Version with `pyenv` (Optional)

If you use `pyenv` to manage Python versions, you can specify a different Python version when creating the virtual environment. For example:

```bash
python3.9 -m venv .venv 
```

This ensures the environment is created using Python 3.9 (or another desired version).

##### GitHub CLI (Optional)
[GitHub CLI](https://cli.github.com/manual/gh_repo_create) can create a new GitHub repository directly from the terminal: 
e.g. `gh repo create my-new-repo --public --source=. --remote=origin`

---

## Folder Structure

The recommended folder structure is as follows:

```
new_analysis
├── README.md
├── code                 # Code snippets and scripts
│   ├── test.py
│   ├── test.r
│   ├── main.sh          # Shell script to run the main analysis
├── data                 # Input data (gitignored)
│   ├── testdata.csv
├── priv                 # Private information (gitignored)
│   ├── exports.sh       # Script to export environment variables
│   ├── private.txt      # Sensitive information, e.g., API keys
├── report               # Analysis outputs (figures, summaries)
│   └── report.txt
├── temp                 # Temporary files (gitignored)
│   ├── temp1.txt
├── requirements.txt
└── .gitignore
```

Once the `venv` is created, a `.venv` folder will also be generated and should remain gitignored.

## Security

To safeguard sensitive information, the `data`, `priv`, and `temp` folders are gitignored by default:

- The **`data`** folder is for input data.
- The **`priv`** folder stores private information such as API keys and passwords.
- The **`temp`** folder holds temporary files generated during analysis.

**Note**: Ensure that sensitive information is never stored in the `report` folder or any other tracked location.


# Larger project template with cookiecutter
There is a very well organized tempplate for this: [cookiecutter data science](https://drivendata.github.io/cookiecutter-data-science/). They are well-thought of, and have many handy tricks inside and the documentation is helpful. From my perspective, the major differences are 

1. **Extented environment setup**: Combined with the more comprehensive environmental management tools such as virtualenv, conda etc, the cookiecutter provides a more robust environment setup. They even provide the Makefile to manage the environment.
2. **Ease of reusing the codes**: The module folder is structured so that the funtions could be installed as a package. You can use these functions in the `notebook` as you go. Also you can pip install these functions in a different project. (e.g. `pip install git+<github repo>`)
3. **More organized**: The folder structure is more suitable for the larger development and collaborations. Documentations and detailed data subfolders are provided.



## Install cookiecutter
```
pip install cookiecutter-data-science
```
## Create a new project
In the parent folder, run the following command
```
ccdss
```
Then you will be asked to provide the project name, author, etc. and this will generate the project folder with the necessary files and folders.

The default folder structure is well thought and organized. I highly recommend reading the [documentation](https://drivendata.github.io/cookiecutter-data-science/). Especially the landing part (Home) and the Opinions part of the documentation. These are very useful to understand the ideas for the robust data analysis.


## Set up the python environment
Having the same envirioment is important for the reproducibility of the analysis. The following is the command to set up the python environment according to the parameters you provided - the python version and the environment management tool
```
cd <project folder>
make create_environment
```

## Install requirement packages

```
make requirements
```
The above will make sure the requirements will be installed in the environment you created. If you install a new package, make sure to update the requirements.txt file by running the following command. Your module will be installed in the environment as editable mode. 
```
pip install <package name> # install the package
pip freeze > requirements.txt # update the file
```

