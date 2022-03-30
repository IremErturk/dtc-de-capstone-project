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

This module is consist of couple of Jupyter Notebooks and Python files. There is two approach that you follow to could run that module. And after that, all visualization assests will reside in [images](./images/) folder. 

### Local Development

**Option 1. Interactive Approach with Jupyter Notebook**

Jupyter notebooks are created on purpose to give user more flexibility and readability to the implementation details for each visualization techniques. 
If you are interested with more interactive experience on visualizations please check [notebook](./notebooks/visualization.ipynb) 


**Option 2. Automated Approach in your local setup**

[`main.py`](./main.py) orchestrates the each visualization logic within [`core.py`](./core.py), [`network_graph.py`](./network_graph.py) and [`word_cloud.py`](./word_cloud.py)

Whole visualization logic can be run simply with single command:
```shell
python main.py local 
```

### CICD Development (default)

Exactly the same approach using `main.py` the visualization logic is going to run as a workflow in CICD whenever there is change in [visualiztion](.) folder. You can find the details of workflow configuration under the [./github/workflows](../.github/workflows/visualization.yaml)

--- 

## Dashboard 
The `dashboard.ipynb` is simple Jupyter notebook that visualize artifacts that are build in previous step.
By running the following command, you will be able to create a intreactive HTML file `dashboard.html` that anyone can open from your browser.
```shell
jupyter nbconvert --execute --to html  dashboard.ipynb --no-input
```