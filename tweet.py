# -*- coding: utf-8 -*-
"""TWEET.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ROGJk9qIWvZRv3JgTRw0j_TGOPwftZUb
"""

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import os
import keras
import plotly.express as px
import re
import string
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from tensorflow.keras.layers import SimpleRNN
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import load_model

nltk.download('wordnet')
nltk.download('stopwords')

# Load data
train = pd.read_csv('train.csv')
train.head()

train.shape

train['text'].isna().sum()

test = pd.read_csv('test.csv')
test.head()

test.shape

test['text'].isna().sum()

train['target'].hist()

#plot target distribution

target_counts = train['target'].value_counts().reset_index()


target_counts.columns = ['Target', 'Count']

fig = px.bar(target_counts, x='Target', y='Count', title='Frequency Distribution of Target',
             labels={'Count':'Number of Occurrences', 'Target':'Target'}, color='Target')

fig.show()

target_counts = train['target'].value_counts().reset_index()


target_counts.columns = ['Target', 'Count']

fig = px.pie(target_counts, values='Count', names='Target', title='Frequency Distribution of Target')

fig.show()

train['lenght_tweet'] = train['text'].apply(len)

train.head()

#plot tweets length



fig = px.histogram(train, x='lenght_tweet', nbins=50, title=' length tweet distribution')

fig.show()

test.head()

train['text'] = train['text'].astype(str)

# First, we split the tweets into individual words
words = ' '.join(train['text']).split()

# Count the frequency of each word
word_counts = Counter(words)

# Convert the dictionary to a DataFrame
word_counts_df = pd.DataFrame.from_dict(word_counts, orient='index').reset_index()
word_counts_df.columns = ['Word', 'Count']

# Plot the word frequencies using a histogram
fig = px.histogram(word_counts_df, x='Word', y='Count', nbins=50, title='Word Frequency Distribution')

fig.show()

test['text'] = test['text'].astype(str)

# First, we split the tweets into individual words
words = ' '.join(test['text']).split()

# Count the frequency of each word
word_counts = Counter(words)

# Convert the dictionary to a DataFrame
word_counts_df = pd.DataFrame.from_dict(word_counts, orient='index').reset_index()
word_counts_df.columns = ['Word', 'Count']

# Plot the word frequencies using a histogram
fig = px.histogram(word_counts_df, x='Word', y='Count', nbins=50, title='Word Frequency Distribution')

fig.show()

test['text'] = test['text'].astype(str)

# Create a single string with all tweets
text = ' '.join(test['text'])

# Create the wordcloud object
wordcloud = WordCloud(width=480, height=480, margin=0).generate(text)

# Display the generated image
plt.figure(figsize=(10, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()

#LSTM
# Text preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    # Remove URLs
    text = re.sub(r"http\S|www\S|https\S", '', text, flags=re.MULTILINE)
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Lemmatization and remove stopwords
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words)
    return text

train['text'] = train['text'].apply(preprocess_text)
test['text'] = test['text'].apply(preprocess_text)

X_train = train['text']
y_train = train['target']
X_test = test['text']

# Tokenization
tokenizer = Tokenizer()
tokenizer.fit_on_texts(X_train)
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)

# Padding
max_length = max([len(s.split()) for s in X_train])
X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')

# Split train data into train and validation set
X_train_pad, X_val_pad, y_train, y_val = train_test_split(X_train_pad, y_train, test_size=0.2, random_state=42)

if os.path.isfile('my_model.h5'):
    # Load the pre-trained model
    tweet_model_lstm = keras.models.load_model('my_model.h5')
    print('model loaded')
else:
    print('No model found, the model will train')

    # Define LSTM model
    model = Sequential()
    model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=50, input_length=max_length))
    model.add(LSTM(64, dropout=0.1))
    model.add(Dense(1, activation='sigmoid'))

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Early stopping
    #early_stop = EarlyStopping(monitor='val_loss', patience=20)

    # Fit the model
    model.fit(X_train_pad, y_train, validation_data=(X_val_pad, y_val), epochs=100)
    model.save('my_model.h5')
# Validate the model
#_val_pred = model.predict_classes(X_val_pad)
y_val_pred = (model.predict(X_val_pad) > 0.5).astype("int32")
y_test_pred = (model.predict(X_test_pad) > 0.5).astype("int32")

print(classification_report(y_val, y_val_pred))



# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to sequence
    sentence_seq = tokenizer.texts_to_sequences([sentence])
    # Padding
    sentence_pad = pad_sequences(sentence_seq, maxlen=max_length, padding='post')
    # Predict and return the target class
    return model.predict(sentence_pad)[0][0]

#use the model for prediction
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")



model.save('my_model.h5')

def predict_target(sentence):
    # Load the saved model
    tweet_model_lstm = load_model('my_model')

    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to sequence
    sentence_seq = tokenizer.texts_to_sequences([sentence])
    # Padding
    sentence_pad = pad_sequences(sentence_seq, maxlen=max_length, padding='post')
    # Predict and return the target class
    return tweet_model_lstm.predict(sentence_pad)[0][0]
# prediction
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")

#logistic regression


# Text preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r"http\S|www\S|https\S", '', text, flags=re.MULTILINE)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words)
    return text

train['text'] = train['text'].apply(preprocess_text)
test['text'] = test['text'].apply(preprocess_text)

X_train = train['text']
y_train = train['target']
X_test = test['text']

# CountVectorizer to convert the text data into a matrix of token counts
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Split train data into train and validation set
X_train_vectorized, X_val_vectorized, y_train, y_val = train_test_split(X_train_vectorized, y_train, test_size=0.2, random_state=42)

# Define Logistic Regression model
model = LogisticRegression()

# Fit the model
model.fit(X_train_vectorized, y_train)

# Validate the model
y_val_pred = model.predict(X_val_vectorized)
y_test_pred = model.predict(X_test_vectorized)

print(classification_report(y_val, y_val_pred))

# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to vector
    sentence_vectorized = vectorizer.transform([sentence])
    # Predict and return the target class
    return model.predict(sentence_vectorized)[0]

# PREDICTION
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")

#Random forest

# Text preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r"http\S|www\S|https\S", '', text, flags=re.MULTILINE)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words)
    return text

train['text'] = train['text'].apply(preprocess_text)
test['text'] = test['text'].apply(preprocess_text)

X_train = train['text']
y_train = train['target']
X_test = test['text']

# CountVectorizer to convert the text data into a matrix of token counts
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Split train data into train and validation set
X_train_vectorized, X_val_vectorized, y_train, y_val = train_test_split(X_train_vectorized, y_train, test_size=0.2, random_state=42)

# Define Random Forest model
model = RandomForestClassifier()

# Fit the model
model.fit(X_train_vectorized, y_train)

# Validate the model
y_val_pred = model.predict(X_val_vectorized)
y_test_pred = model.predict(X_test_vectorized)

print(classification_report(y_val, y_val_pred))

# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to vector
    sentence_vectorized = vectorizer.transform([sentence])
    # Predict and return the target class
    return model.predict(sentence_vectorized)[0]

# prediction
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")

# Text preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r"http\S|www\S|https\S", '', text, flags=re.MULTILINE)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words)
    return text

train['text'] = train['text'].apply(preprocess_text)
test['text'] = test['text'].apply(preprocess_text)

X_train = train['text']
y_train = train['target']
X_test = test['text']

# CountVectorizer to convert the text data into a matrix of token counts
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Split train data into train and validation set
X_train_vectorized, X_val_vectorized, y_train, y_val = train_test_split(X_train_vectorized, y_train, test_size=0.2, random_state=42)

# Define SVM model
model = SVC(probability=True)  # 'probability = True' is needed for predict_proba

# Fit the model
model.fit(X_train_vectorized, y_train)

# Validate the model
y_val_pred = model.predict(X_val_vectorized)
y_test_pred = model.predict(X_test_vectorized)

print(classification_report(y_val, y_val_pred))

# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to vector
    sentence_vectorized = vectorizer.transform([sentence])
    # Predict and return the target class
    return model.predict(sentence_vectorized)[0]

# Example usage
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")

# DecisionTreeClassifier
# Text preprocessing
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = re.sub(r"http\S|www\S|https\S", '', text, flags=re.MULTILINE)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words)
    return text

train['text'] = train['text'].apply(preprocess_text)
test['text'] = test['text'].apply(preprocess_text)

X_train = train['text']
y_train = train['target']
X_test = test['text']

# CountVectorizer to convert the text data into a matrix of token counts
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Split train data into train and validation set
X_train_vectorized, X_val_vectorized, y_train, y_val = train_test_split(X_train_vectorized, y_train, test_size=0.2, random_state=42)

# Define Decision Tree model
model = DecisionTreeClassifier()

# Fit the model
model.fit(X_train_vectorized, y_train)

# Validate the model
y_val_pred = model.predict(X_val_vectorized)
y_test_pred = model.predict(X_test_vectorized)

print(classification_report(y_val, y_val_pred))

# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to vector
    sentence_vectorized = vectorizer.transform([sentence])
    # Predict and return the target class
    return model.predict(sentence_vectorized)[0]

# Example usage
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")



#RNN
# Define RNN model
model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=50, input_length=max_length))
model.add(SimpleRNN(64, dropout=0.1))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Fit the model
model.fit(X_train_pad, y_train, validation_data=(X_val_pad, y_val), epochs=100)

# Validate the model
y_val_pred = (model.predict(X_val_pad) > 0.5).astype("int32")
y_test_pred = (model.predict(X_test_pad) > 0.5).astype("int32")

print(classification_report(y_val, y_val_pred))

# Function to predict target class for a given sentence
def predict_target(sentence):
    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to sequence
    sentence_seq = tokenizer.texts_to_sequences([sentence])
    # Padding
    sentence_pad = pad_sequences(sentence_seq, maxlen=max_length, padding='post')
    # Predict and return the target class
    return (model.predict(sentence_pad) > 0.5).astype("int32")

# Example usage
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result[0][0] == 1 else "No disaster")

model.save('RNN_model.h5')

def predict_target(sentence):
    # Load the saved model
    tweet_model_RNN = load_model('my_model')

    # Preprocess the sentence
    sentence = preprocess_text(sentence)
    # Convert the sentence to sequence
    sentence_seq = tokenizer.texts_to_sequences([sentence])
    # Padding
    sentence_pad = pad_sequences(sentence_seq, maxlen=max_length, padding='post')
    # Predict and return the target class
    return tweet_model_RNN.predict(sentence_pad)[0][0]
# prediction
sentence = input("Please enter your sentence: ")
result = predict_target(sentence)
print("Disaster tweet" if result == 1 else "No disaster")