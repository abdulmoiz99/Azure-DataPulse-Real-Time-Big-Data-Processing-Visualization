from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import pandas as pd
import requests
from azure.storage.blob import BlobServiceClient
from io import StringIO

# Create Spark session with proper configuration for Azure Blob Storage (abfs)
spark = SparkSession.builder.master("local[*]") \
    .appName("BatchProcessingTriviaData") \
    .config("spark.hadoop.fs.azure.account.key.fordatalakestorage.blob.core.windows.net", "<YOUR_SECRET_KEY>") \
    .config("spark.hadoop.fs.azure.account.auth.type.fordatalakestorage.blob.core.windows.net", "SharedKey") \
    .config("spark.hadoop.fs.azure", "org.apache.hadoop.fs.azurebfs.AzureBlobFileSystem") \
    .getOrCreate()

def fetch_trivia_data():
    url = "https://opentdb.com/api.php?amount=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        return []

def process_batch(df, batch_id):
    # Fetch data and convert to CSV
    data = fetch_trivia_data()
    if data:
        pandas_df = pd.DataFrame(data)
        csv_buffer = StringIO()
        pandas_df.to_csv(csv_buffer, index=False)

        # Configuration for Azure Blob Storage
        account_name = "ACCOUNT_NAME"
        account_key = "SECRET_KEY"
        container_name = "CONTAINER_NAME"
        blob_name = f"output/trivia_data_batch_{batch_id}.csv"

        # Create BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)

        # Create BlobClient
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Upload CSV string to Azure Blob Storage
        blob_client.upload_blob(csv_buffer.getvalue(), overwrite=True)

        print(f"Batch {batch_id} written to {blob_name} in Azure Blob Storage")

    # Add additional processing if needed

# Read stream from a source that generates data
trivia_df = spark.readStream.format("rate").option("rowsPerSecond", 2).load()

# Use foreachBatch to process each batch of data
query = trivia_df.writeStream.foreachBatch(process_batch).start()
query.awaitTermination()

# Stop the Spark session
spark.stop()
