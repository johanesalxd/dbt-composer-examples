# dbt-composer-examples

## Notes
* Additional updates might be needed.

## Folder structures

```
my_dbt_project/
├── dbt_project.yml
├── profiles.yml  # Primarily for local development; Composer will use environment/connection settings
├── models/
│   ├── staging/
│   │   └── stg_raw_orders.sql
│   └── marts/
│       └── fct_daily_summary.sql
└── seeds/ # Optional: if you have CSV data to seed
    └── raw_orders_seed.csv
```

## DAG explanation

* `DBT_PROJECT_DIR`: Points to where your dbt project will live within the GCS bucket synced to Composer's /home/airflow/gcs/dags/ directory.
* `DBT_PROFILE_DIR`: Usually the same as the project directory if profiles.yml is in the root.
* `DBT_ENV_VARS`: This is a clean way to ensure dbt-bigquery knows which project and dataset to use, especially if you want to avoid checking in profiles.yml or want environment-specific overrides.
* `BashOperator`: We use it to execute dbt CLI commands.
    * `cwd=DBT_PROJECT_DIR`: Sets the current working directory for the bash_command to your dbt project's root. This is crucial so dbt can find dbt_project.yml.
    * `env=DBT_ENV_VARS`: Passes the defined environment variables to the shell where dbt commands are executed.
* Tasks:
    * `dbt_deps`: Installs any dbt packages listed in packages.yml (if you have one).
    * `dbt_seed`: Loads data from CSVs in your seeds folder into BigQuery. The --full-refresh flag will cause dbt to drop and recreate the seed tables.
    * `dbt_compile`: Compiles your dbt project (Jinja templating, graph construction) without running models. Good for validation.
    * `dbt_run`: Executes your dbt models, creating or updating tables/views in BigQuery.
    * `dbt_test`: Runs data and schema tests.

## How to run on Cloud Composer
### Permissions
* Permissions: The service account used by your Cloud Composer environment needs:
    * `roles/bigquery.dataEditor` (to create/modify datasets and tables)
    * `roles/bigquery.jobUser` (to run BigQuery jobs)
    * `roles/storage.objectViewer` (to read DAGs and dbt project files from GCS)

### Install `dbt` in your Cloud Composer Environment:
You need to add dbt-bigquery (and any other dbt adapters you might use) to your Composer environment's PyPI packages.
1. Go to your Cloud Composer environment in the GCP Console.
2. Navigate to the "PyPI Packages" tab.
Click "Edit" and add the following packages:
3. `dbt-bigquery>=1.9.1` (specify a version you're compatible with; check the latest stable version).


### Upload your `dbt` Project and DAG to GCS:
Cloud Composer monitors a GCS bucket for DAGs and related files.
1. Find your Composer environment's GCS bucket (usually something like `us-central1-your-env-name-randomhash-bucket`).
2. Inside this bucket, navigate to the `dags/` folder.
3. Upload your entire dbt project directory (e.g., `my_dbt_project/`) into the `dags/` folder.
    * The structure in GCS should look like: `gs://<your-composer-bucket>/dags/my_dbt_project/dbt_project.yml`, etc.
4. Upload your DAG file (e.g., `my_dbt_dag.py`) directly into the `dags/` folder.
    * GCS path: `gs://<your-composer-bucket>/dags/my_dbt_dag.py`

### Trigger and Monitor the DAG:
1. Once Airflow parses the new DAG (may take a few minutes), it will appear in the Airflow UI of your Composer environment.
2. You can trigger it manually.
3. Monitor the task logs in the Airflow UI. You should see the output of `dbt compile` and `dbt run`.
4. Check BigQuery to see if your tables/views (`stg_raw_orders` in the `dbt_transformed_data_staging` dataset and `fct_daily_summary` in the `dbt_transformed_data_marts` dataset, assuming your default dataset is `dbt_transformed_data`) have been created/updated.
