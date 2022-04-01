# Data Visualization

## Setup Virtual Environment

 To be able to run that module smootly please follow below steps to setup virtual environment.

1 Create venv
```shell
python3 -m venv ./venv
```
2 Activate venv
```shell
source ./venv/bin/activate
```
3 Install required python packages
```shell
pip install -r requirements.txt
```

---

## Create Dashboard Artifacts

This module is consist of couple of Jupyter Notebooks and Python files. These files can be used for four different apporach.
There is two approach that you follow to could run that module. And after that, all visualization assests will reside in [images](./images/) folder.


### CICD Development (default)

The artifact creation process is automated by creating a GitHub Actions workflow [./github/workflows/visualizayion.yaml](../.github/workflows/visualization.yaml).
Therefore whenever change happens in [visualization](./) folder, the workflow is going to be triggered and run at GitHub. 


### Local Development

**--Interactive Approach with Jupyter Notebook--**

[notebooks] subfolder is created to provide flexibility and readability to the implementation details for each visualization techniques.
If you are interested with more interactive experience on visualizations please check [notebook](./notebooks/visualization.ipynb)


**--Automated Approach in your local setup--**

[`main.py`](./main.py) orchestrates the each visualization logic within [`core.py`](./core.py), [`network_graph.py`](./network_graph.py) and [`word_cloud.py`](./word_cloud.py).

Whole visualization logic can be run simply with single command:
```shell
python main.py local
```
As a result of the command above, eight artifacts (either .png or .html format) will be created and ready to share with people.

---

## Dashboard
The `dashboard.ipynb` is simple Jupyter notebook that visualize artifacts that are build in previous step.
By running the following command, you will be able to create a intreactive HTML file `dashboard.html` that anyone can open from your browser.
```shell
jupyter nbconvert --execute --to html  dashboard.ipynb --no-input
```
