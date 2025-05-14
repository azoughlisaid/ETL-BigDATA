import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# 1. Créer le topic Kafka
def create_kafka_topic(topic_name="user_activity"):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")
        topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
        admin_client.create_topics([topic])
        print(f"✅ Topic '{topic_name}' créé avec succès.")
    except Exception as e:
        print(f"⚠️ Erreur création topic : {e}")
    finally:
        admin_client.close()

# 2. Générer un événement simulé
def generate_user_event():
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": str(random.randint(1000, 9999)),
        "timestamp": datetime.now().isoformat(),
        "activity_type": random.choice(['view', 'add_to_cart', 'purchase', 'search']),
        "product_id": str(random.randint(10000, 99999)),
        "price": round(random.uniform(10, 1000), 2),
        "category": random.choice(['electronics', 'clothing', 'books', 'home', 'beauty']),
        "device": random.choice(['mobile', 'desktop', 'tablet']),
        "location": random.choice(['US', 'FR', 'DE', 'JP', 'CA']),
        "session_id": f"sess_{random.randint(1000,9999)}"
    }

# 3. Envoyer les messages dans Kafka
def produce_messages(topic_name="user_activity", num_messages=1000):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    for i in range(num_messages):
        event = generate_user_event()
        producer.send(topic_name, event)

        if (i + 1) % 100 == 0:
            print(f"💬 {i + 1} messages envoyés...")
        time.sleep(0.01)

    producer.flush()
    producer.close()
    print(f"✅ {num_messages} messages envoyés à Kafka.")

# Exécution
if __name__ == "__main__":
    create_kafka_topic()
    produce_messages()
