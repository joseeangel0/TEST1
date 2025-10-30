
import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, udf, expr
from pyspark.sql.types import FloatType, StringType, IntegerType

# --- Job Initialization ---
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# --- Configuration ---
S3_BUCKET_NAME = "instructions-67f86d4f"
S3_RAW_PREFIX = "raw/"
S3_PROCESSED_PREFIX = "processed/"

# --- Helper function to find the latest file ---
def get_latest_s3_object(bucket, prefix):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if 'Contents' not in response:
            print(f"No files found in s3://{bucket}/{prefix}")
            return None
        
        all_files = response['Contents']
        latest_file = max(all_files, key=lambda x: x['LastModified'])
        print(f"Latest file found: {latest_file['Key']}")
        return latest_file['Key']
    except Exception as e:
        print(f"Error finding latest file: {e}")
        return None

# --- Transformation Logic ---

# 1. Find and read the latest raw file
latest_raw_key = get_latest_s3_object(S3_BUCKET_NAME, S3_RAW_PREFIX)

if latest_raw_key:
    input_path = f"s3://{S3_BUCKET_NAME}/{latest_raw_key}"
    
    # Read the JSON data into a DynamicFrame
    dynamic_frame = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [input_path]},
        format="json"
    )
    
    df = dynamic_frame.toDF()
    print(f"Initial row count: {df.count()}")

    # 2. Select required columns and handle missing values
    required_columns = ['name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender']
    df = df.select(required_columns)
    df = df.replace('unknown', None).replace('n/a', None)

    # 3. Create 'normalized_birth_year'
    # Using expr for robust conversion
    df = df.withColumn("normalized_birth_year", expr("2000 - CAST(regexp_replace(birth_year, 'BBY', '') AS FLOAT)"))

    # 4. Create 'mass_lb'
    # Ensure mass is numeric before conversion
    df = df.withColumn("mass_numeric", col("mass").cast(FloatType()))
    df = df.withColumn("mass_lb", col("mass_numeric") * 2.20462)

    # 5. Create 'gender_id'
    df = df.withColumn("gender_id", 
        when(col("gender") == "male", "M")
        .when(col("gender") == "female", "F")
        .otherwise("N")
    )

    # 6. Filter out rows where mass > 1000
    df = df.filter(col("mass_numeric") <= 1000)

    # 7. Filter rows with 3 or more empty fields
    # Create a count of nulls for each row across the original required columns
    null_counts = sum(when(col(c).isNull(), 1).otherwise(0) for c in required_columns)
    df = df.withColumn("null_count", null_counts)
    df = df.filter(col("null_count") < 3)

    # 8. Select final columns and prepare for writing
    final_df = df.select(
        'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender',
        'normalized_birth_year', 'mass_lb', 'gender_id'
    )
    
    print(f"Final row count after transformations: {final_df.count()}")

    # 9. Write the data to the processed folder as a single CSV file
    output_path = f"s3://{S3_BUCKET_NAME}/{S3_PROCESSED_PREFIX}"
    
    # Convert back to DynamicFrame before writing
    final_dynamic_frame = final_df.repartition(1).fromDF(final_df, glueContext, "final_df")

    glueContext.write_dynamic_frame.from_options(
        frame=final_dynamic_frame,
        connection_type="s3",
        connection_options={"path": output_path},
        format="csv",
        format_options={"writeHeader": True}
    )
    
    print(f"Successfully transformed data and saved to {output_path}")

else:
    print("Job finished: No new file to process.")

# --- Job Commit ---
job.commit()
