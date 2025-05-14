from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Création de la session Spark avec connecteurs Kafka + MongoDB
spark = SparkSession.builder \
    .appName("ETL_to_MongoDB") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/ecommerce.user_activity_processed") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Définir le schéma JSON attendu
schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("activity_type", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("category", StringType(), True),
    StructField("device", StringType(), True),
    StructField("location", StringType(), True),
    StructField("session_id", StringType(), True)
])

# Lire depuis Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "user_activity") \
    .option("startingOffsets", "earliest") \
    .load()

# Parser le JSON proprement
df = df_raw.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*")

# Enrichir les données
df_transformed = df \
    .withColumn("event_timestamp", to_timestamp("timestamp")) \
    .withColumn("price_category", when(col("price") < 50, "low")
                .when(col("price") < 200, "medium")
                .otherwise("high")) \
    .withColumn("weekday", date_format(col("event_timestamp"), "EEEE")) \
    .withColumn("processing_time", current_timestamp())

# Nettoyer les lignes incomplètes
df_clean = df_transformed.filter(
    col("user_id").isNotNull() &
    col("product_id").isNotNull() &
    col("price").isNotNull() &
    col("event_timestamp").isNotNull()
)

# Fonction pour écrire dans MongoDB
def write_to_mongo(batch_df, batch_id):
    batch_df.write \
        .format("mongo") \
        .mode("append") \
        .option("database", "ecommerce") \
        .option("collection", "user_activity_processed") \
        .save()
    print(f"✅ Batch {batch_id} écrit dans MongoDB")

# Lancer le streaming
df_clean.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_mongo) \
    .option("checkpointLocation", "/tmp/checkpoint_user_activity/") \
    .start() \
    .awaitTermination()

