# nlp/src/tests/test_setup.py
import spacy
from transformers import pipeline
import tensorflow as tf
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_spacy():
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("This is a test sentence for SpaCy.")
    print("SpaCy test:", [token.text for token in doc])


def test_transformers():
    try:
        classifier = pipeline("sentiment-analysis")
        result = classifier("I love Python programming!")[0]
        print("Transformers test:", result)
    except Exception as e:
        print(f"Transformers test failed: {str(e)}")


def test_tensorflow():
    print("TensorFlow version:", tf.__version__)
    a = tf.constant([1, 2, 3])
    b = tf.constant([4, 5, 6])
    print("TensorFlow test:", tf.reduce_sum(a * b))


def test_fastapi():
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"Hello": "World"}

    client = TestClient(app)
    response = client.get("/")
    print("FastAPI test:", response.json())


if __name__ == "__main__":
    print("Running setup tests...")
    test_spacy()
    test_transformers()
    test_tensorflow()
    test_fastapi()
    print("All tests completed.")
