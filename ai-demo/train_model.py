from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from joblib import dump

# Load dataset
data = fetch_20newsgroups(subset='train', categories=['sci.space', 'rec.sport.baseball'])
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2)

# Build pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())

# Train model
model.fit(X_train, y_train)

# Evaluate
print("Accuracy:", model.score(X_test, y_test))

# Save model
dump(model, 'text_classifier.joblib')