import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import sqlalchemy

# Database connection setup
DATABASE_URL = "mysql+pymysql://root:mysql@localhost/room_booking_system"  # Update credentials if needed
engine = sqlalchemy.create_engine(DATABASE_URL)

# Load data
query = """
SELECT ul.log_id, ul.booking_id, ul.check_in_time, ul.check_out_time, b.room_id, b.group_size
FROM usage_logs ul
JOIN bookings_booking b ON ul.booking_id = b.id
"""
data = pd.read_sql(query, con=engine)

# Feature engineering
data['hour'] = pd.to_datetime(data['check_in_time']).dt.hour
features = data[['hour', 'group_size']]  # Include 'group_size' as a feature
target = data['room_id']

# Train model
model = RandomForestClassifier()
model.fit(features, target)

# Save model
joblib.dump(model, 'room_recommendation_model.pkl')
print("Model training completed and saved as 'room_recommendation_model.pkl'.")
