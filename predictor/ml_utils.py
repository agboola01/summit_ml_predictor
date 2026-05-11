import joblib
from django.conf import settings

_MODEL_CACHE = {}

def load_model(model_name):
    """Load a pre-trained model from disk (cached)."""
    if model_name not in _MODEL_CACHE:
        path = settings.MODEL_DIR / f"{model_name}.pkl"
        if not path.exists():
            raise FileNotFoundError(
                f"Model '{model_name}' not found. Run 'python manage.py train_all_models' first."
            )
        _MODEL_CACHE[model_name] = joblib.load(path)
    return _MODEL_CACHE[model_name]