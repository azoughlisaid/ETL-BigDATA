from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
collection = db["user_activity_processed"]

# =====================
# 📊 1. Activités utilisateur (pie chart)
# =====================
activity_data = list(collection.aggregate([
    {"$group": {"_id": "$activity_type", "count": {"$sum": 1}}}
]))
df_activity = pd.DataFrame(activity_data)
df_activity.columns = ['activity_type', 'count']

plt.figure(figsize=(6,6))
plt.pie(df_activity['count'], labels=df_activity['activity_type'], autopct='%1.1f%%')
plt.title("Répartition des activités")
plt.savefig("1_pie_activities.png")
plt.close()

# =====================
# 📉 2. Valeur moyenne des achats par pays
# =====================
avg_price = list(collection.aggregate([
    {"$match": {"activity_type": "purchase"}},
    {"$group": {"_id": "$location", "avg_price": {"$avg": "$price"}}}
]))
df_avg = pd.DataFrame(avg_price)
df_avg.columns = ['location', 'avg_price']

plt.figure(figsize=(8,5))
sns.barplot(data=df_avg, x="location", y="avg_price")
plt.title("Prix moyen des achats par pays")
plt.savefig("2_avg_price_by_location.png")
plt.close()

# =====================
# 📊 3. Appareils utilisés par catégorie
# =====================
device_stats = list(collection.aggregate([
    {"$group": {
        "_id": {"category": "$category", "device": "$device"},
        "count": {"$sum": 1}
    }}
]))
df_device = pd.DataFrame([{
    "category": doc["_id"]["category"],
    "device": doc["_id"]["device"],
    "count": doc["count"]
} for doc in device_stats])

plt.figure(figsize=(10,6))
sns.barplot(data=df_device, x="category", y="count", hue="device")
plt.title("Utilisation des appareils par catégorie")
plt.savefig("3_device_by_category.png")
plt.close()

print("✅ Graphiques générés avec succès 🎉")
