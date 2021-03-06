# Good-2-Knows

## Code Standardization & Code Formatting  with Pre-commit ((optional))
Follow the instructions below to install and setup pre-commit for the project.
In below, the steps to setup in **MacOs** will be given, for any other operating system,
please check [pre-commit](https://pre-commit.com/) documentation

1  Install pre-commit on machine
```shell
brew install pre-commit
pre-commit --version
```

2 (no action needed) Add pre-commit plugins to the project
Create `.pre-commit-config.yaml` configuration file on root to setup plugins.


3 To run pre-commit againts your git repository. There is two
approaches that can be followed.
- (Option 1) Install pre-pommit Git Hook Script which will ensure running pre-commit automatically with every `git commit`.
    ```shell
    cd <project-git-repo>
    pre-commit install
    ```
- (Option 2) Run pre-commit against all files manually, which is more transparent way as you have more control over changes.
    ```shell
    pre-commit run --all-files
    ```

4 (optional) To update hooks to latest version automatically.
```shell
 pre-commit autoupdate
```

---

## External Table vs Native Tables in BigQuery
by Quora [Question](https://www.quora.com/What-is-the-difference-between-native-and-external-tables-in-Google-Big-Query)
~Native tables are tables that you import the full data inside Google BigQuery like you would do in any other common database system. In contrast, external tables are tables where the data is not stored inside Google BigQuery, but instead references the data from an external source, such as a data lake.

The advantages of creating external tables is that they are fast to create (you skip the part of importing data) and no additional monthly billing storage costs are accrued to your account (you only get charged the data that is stored in the data lake, which is comperatively cheaper than storing it in BigQuery). The disadvantages is that the queries against external tables are comparably slow as compared to native tables, especially if the files are very big. Otherwise, if the data is split into small files and is infrequently used by users, keeping them in a bucket in Google Cloud Storage can be a good use case to save storage costs.

There are other competitors like Amazon that provides the ability to create external tables as well. For instance, Amazon Redshift Spectrum allows you to create external tables in Redshift which references files in their S3 cloud storage~

For futher information please check limitations of [external](https://cloud.google.com/bigquery/docs/external-tables#external_table_limitations) and naive tables[].


---

## Debug your Files in Data Lake
If you are having a problem with the data-ingestion and following data reading step.
You may want to check your schema in the file level and try to debug the error/issue.
To fasten the feedback loop, you can use the `gcsfs` package to understnad mismatch between files.

1. Install the required package
```shell
%system pip install gcsfs -q
```
2. Run the code as given below
```python
import pyarrow.parquet as pq
import gcsfs
import pandas as pd

fs = gcsfs.GCSFileSystem(project=PROJECT_NAME)
f = fs.open("gs://<filepath>")
schema = pq.ParquetFile(f).schema
parquet_file = pq.ParquetFile(f)
```
3. Check if schema and file has any anomaly.
