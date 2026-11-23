"""Regression test for the safe, authentic BBC classifier sidecar."""
from pathlib import Path
import numpy as np
from src.analysis.bbc_classifier import BBCWeightedClassifier


def test_bbc_weighted_classifier_schema_and_probabilities():
    path = Path(__file__).resolve().parents[1] / 'data' / 'released_models' / 'bbc_classifier_weights.json.gz'
    if not path.exists():
        raise AssertionError('Released BBC weights must be shipped with application')
    classifier = BBCWeightedClassifier(path)
    assert classifier.provenance['articles_used'] == 1440
    assert classifier.provenance['no_raw_articles_embedded'] is True
    example = ('Members of parliament debated changes to the national budget and government policy. '
               'The prime minister appeared before legislators to explain the proposal.')
    response = classifier.predict(example)
    assert response['category'] in {'business','entertainment','politics','sport','technology'}
    assert 0.0 <= response['model_probability'] <= 1.0
    assert np.isclose(sum(response['probabilities'].values()),1,atol=0.001)
