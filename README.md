
# Azure-DataPulse: Real-Time Big Data Streaming with Spark and Azure

This project demonstrates an end-to-end big data pipeline using Spark Streaming, Azure Data Lake Storage, Azure Data Factory, and Power BI for visualization. The pipeline ingests data via a Spark Docker container, processes it in real-time, and stores it in Azure Data Lake for downstream analytics and reporting. 

## Prerequisites 
	- Docker installed on your local machine 
	- Azure subscription with: 
		- Azure Data Lake Storage (ADLS) 
		- Azure Data Factory 
		- Azure Synapse Analytics 
		- Power BI for visualization

## Step 1: Configuring Azure Environment with ARM Template

To automate the deployment of Azure resources (Data Lake Storage, Data Factory, and Synapse Analytics), you can use the provided ARM template.

### 1.1. Clone the Repository

First, clone the project repository that contains the ARM template:

```bash
git clone https://github.com/abdulmoiz99/Azure-DataPulse-Real-Time-Big-Data-Processing-Visualization.git
cd <repository_directory>
```
### 1.2. Deploy the ARM Template
To deploy the Azure environment using the ARM template, follow these steps:

Log in to your Azure account using the Azure CLI:
```bash
az login
```
Use the following command to create a new resource group (if you don't already have one):
```bash 
az group create --name MyResourceGroup --location eastus
```
Deploy the ARM template:
```bash 
az deployment group create --resource-group MyResourceGroup --template-file azure-deployment-template.json --parameters azure-deployment-parameters.json
```
### 1.3. Template Details
The ARM template will provision the following resources in your Azure environment:

**Azure Data Lake Storage Gen2**: For storing the batch-processed data from Spark Streaming.
 **Azure Data Factory**: For automating data pipeline and transformation workflows.
**Azure Synapse Analytics**: For executing Spark SQL queries on the data.
**Other Resources**: Any additional resources specified in the ARM template.
The parameters file (azure-deployment-parameters.json) allows you to customize resource names, locations, and other settings.


## Step 2: Setting up the Spark Docker Environment
 We are using the `bitnami/spark` Docker image to run Spark Streaming.
  ### 2.1. Download the Docker Image
   Pull the Spark Docker image from Docker Hub by running the following command: 
```bash
docker pull bitnami/spark
```
Alternatively, visit [bitnami/spark on Docker Hub](https://hub.docker.com/r/bitnami/spark) to get the image details.

### 2.2. Build the Docker Image

Navigate to the directory where the provided `Dockerfile` is located. Then, build your Docker image by running:
```bash
docker build -t my-spark-app .
```
### 2.3. Running the Docker Container

Once the image is built, run the container with the following command:

```bash
docker run -it --rm -v "local repo path:/app" bitnami/spark /bin/bash
```
This mounts the project directory from your local system to the Docker container and opens an interactive Bash shell inside the container.

## Step 3: Installing Dependencies

Inside the Docker container, you need to install the following Python libraries to work with Azure Data Lake and handle requests:

```bash
pip install requests
pip install azure-storage-file-datalake 
pip install pandas
```

## Step 4: Submitting the Spark Streaming Job

To run the Spark Streaming application, use the following command to submit the Spark job:
```bash
spark-submit /app/github_streaming_app.py
```
This script processes the data and writes the output to Azure Data Lake Storage.



## Step 5: Data Output in Azure Data Lake Storage

Once the Spark Streaming job is submitted, it processes data and dumps the output files into Azure Data Lake Storage. These output files are initially created as small batch files.

The merged file will be stored in the following path within your Azure Data Lake Storage container:
	 ``` bigdatatesting1/mergedOutput```
In the specified path, you will find the merged CSV file containing the processed data from your Spark job.

##  Running the Docker Image and Populating Azure Data Lake

Below is a demonstration of how to run the Docker image and how Azure Data Lake is populated with batch files:

![Demonstration of Docker and Azure Data Lake](https://github.com/abdulmoiz99/Azure-DataPulse-Real-Time-Big-Data-Processing-Visualization/blob/main/public/gifs/DockerExecution.gif)

After executing the Spark job, the data will be dumped into Azure Data Lake Storage, and Azure Data Factory will trigger to merge the batch files into a single blob.


## Step 6: Azure Data Factory Pipeline

An Azure Data Factory (ADF) pipeline is automatically triggered after the Spark job completes. The pipeline is responsible for merging the small batch files into a single consolidated file.

### 6.1. Pipeline Actions

- **Merging Batch Files**: The pipeline collects the small batch files created by the Spark Streaming job and merges them into one file.
- **Batch File Cleanup**: After the merge operation is completed, the pipeline deletes the smaller batch files, leaving only the merged CSV file in the storage location.

You can view and manage this pipeline from the Azure Data Factory portal.

To check the status of your pipeline execution:

1. Go to the [Azure Data Factory portal](https://adf.azure.com/).
2. Navigate to the **Monitor** tab to view pipeline runs.
3. Here, you can monitor the pipeline execution, see the merged file creation, and check for any error
### Demonstration of Azure Data Factory Pipeline

![Demonstration of Docker and Azure Data Lake](https://github.com/abdulmoiz99/Azure-DataPulse-Real-Time-Big-Data-Processing-Visualization/blob/main/public/gifs/DataPipeLineExecution.gif)

This pipeline automatically consolidates all blob files into a single blob upon execution. A trigger has been set up, eliminating the need for manual execution.

## Step 7: Running Spark SQL Queries in Azure Synapse Analytics

Once the data is merged and stored in Azure Data Lake, you can use Azure Synapse Analytics to run Spark SQL queries for data analysis.

### 7.1. Accessing Azure Synapse Studio

1. Navigate to the [Azure Synapse Analytics portal](https://web.azuresynapse.net/).
2. Open **Synapse Studio** from your Synapse workspace.

### 7.2. Creating a Notebook in Synapse Studio

1. In Synapse Studio, select the **Develop** tab from the left-hand menu.
2. Click on **+** and choose **Notebook** to create a new notebook for running your queries.

### 7.3. Configuring the Notebook

1. Attach the notebook to your **Spark pool** by selecting your Spark pool from the **Attach to** dropdown in the notebook interface.
2. Choose **PySpark** as the language for your notebook.

### 7.4. Loading Data into Spark
You can load the merged CSV file from Azure Data Lake Storage into a Spark DataFrame and register it as a temporary table for querying. Replace `<your-blob-url>` in the following code with your actual Azure Data Lake Storage Blob URL: 
```python
# Read the merged CSV file from Azure Data Lake Storage
df = spark.read.csv("<your-blob-url>", header=True, inferSchema=True)
# Create a temporary view for the dataset 
df.createOrReplaceTempView("trivialDataset")
```
For example, your Blob URL will be something like:
```
abfs://<your-container-name>@<your-storage-account-name>.dfs.core.windows.net/<your-path-to-merged-output>
```
### 7.5. Executing Spark SQL Queries

Now that the data is loaded into a temporary view, you can run SQL queries on the dataset using Spark SQL.

Here's a sample query to retrieve all the data:
```python
# Execute a SQL query on the dataset
result = spark.sql("SELECT * FROM trivialDataset")

# Show the results of the query
result.show()
```
You can modify the SQL query to perform different analyses on the dataset.

## Preview of Spark SQL Execution.
![Demonstration of Spark SQL in Azure Synapse](https://github.com/abdulmoiz99/Azure-DataPulse-Real-Time-Big-Data-Processing-Visualization/blob/main/public/images/SparkSQLExecution.png)


## Step 8: Configuring Power BI Report

Once you have attached the Power BI report to the repository, follow these steps to configure and visualize your data:

### 8.1. Download the Power BI Report

1. Clone the repository or download the Power BI report file (e.g., `datasetReport.pbix`) from the repository.
2. Open Power BI Desktop on your machine.

### 8.2. Open the Report in Power BI Desktop

1. In Power BI Desktop, click on **File** and select **Open**.
2. Navigate to the downloaded Power BI report file and open it.

### 8.3. Connecting to Azure Data Lake Storage

1. In Power BI Desktop, go to the **Home** tab and click on **Get Data**.
2. Select **Azure** from the list and choose **Azure Data Lake Storage Gen2**.
3. Enter the URL of your Azure Data Lake Storage account in the format:  https://<your-storage-account-name>.dfs.core.windows.net/
4. Authenticate with your Azure credentials if prompted.

### 8.4. Loading Data

1. After connecting, navigate to the folder where your merged CSV file is stored (e.g., `merged_output`).
2. Select the merged CSV file to load the data into Power BI.
3. Click on **Load** to import the data.

### 8.5. Refreshing the Data

1. To refresh the data, go to the **Home** tab and click on **Refresh**.
2. You can also set up scheduled refreshes in the Power BI service after publishing your report online.

### 8.6. Publishing the Report

1. Once your report is ready, click on the **Publish** button in the Home tab.
2. Choose the destination workspace in your Power BI service to publish the report.

### 8.7. Visualizing the Data

You can now create various visualizations and dashboards using the data from Azure Data Lake Storage. Explore the features of Power BI to gain insights from your dataset.

![Data Pipeline Animation](https://github.com/abdulmoiz99/Azure-DataPulse-Real-Time-Big-Data-Processing-Visualization/blob/main/public/gifs/PowerBIReport.gif)

  
