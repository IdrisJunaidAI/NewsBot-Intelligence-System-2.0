"""Central configuration; no secrets in repository."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
@dataclass(frozen=True)
class Settings:
    seed: int = 42
    n_topics: int = 5
    max_features: int = 12000
    max_input_characters: int = 30000
    low_confidence_threshold: float = 0.55
    model_path: Path = ROOT / 'data' / 'models' / 'newsbot2.joblib'
    demo_path: Path = ROOT / 'data' / 'raw' / 'demo_articles.csv'
