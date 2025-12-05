import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from joblib import dump

# Path to your Excel file
excel_file = r"C:\Work\ai-demo\data\synthetic_dataset_large.xlsx" 

# Read Excel file (requires openpyxl)
df = pd.read_excel(excel_file, engine='openpyxl')

# Validate columns
if 'text' not in df.columns or 'label' not in df.columns:
    raise ValueError("Excel file must contain 'text' and 'label' columns")

# Extract features and labels
texts = df['text'].astype(str).tolist()
labels = df['label'].tolist()

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Build pipeline: TF-IDF + Naive Bayes
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train model
model.fit(X_train, y_train)

# Evaluate accuracy
accuracy = model.score(X_test, y_test)
print(f"Model trained successfully. Accuracy on test set: {accuracy:.2f}")

# Save trained model
dump(model, 'text_classifier.joblib')
print("Trained model saved as text_classifier.joblib")