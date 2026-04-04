import pickle

MODEL_PATH = r"E:\Projects\Fraud-detection-system\ml-service\artifacts\model.pkl"

print("📦 Loading model bundle...")
bundle = pickle.load(open(MODEL_PATH, 'rb'))

lgbm           = bundle['lgbm']
iso_forest     = bundle['iso_forest']
explainer      = bundle['explainer']
FEATURES       = bundle['features']
FEATURES_AUG   = bundle['features_aug']
BEST_THRESHOLD = bundle['best_threshold']

print(f"✅ Model loaded | Threshold: {BEST_THRESHOLD}")