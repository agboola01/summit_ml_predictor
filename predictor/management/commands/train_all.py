import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, r2_score, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class Command(BaseCommand):
    help = 'Train all ML models and save to ml_models/'

    def _encode_df(self, df, encoders=None, fit=False):
        if encoders is None:
            encoders = {}
        for col in df.select_dtypes(include='object').columns:
            if fit:
                le = LabelEncoder()
                le.fit(df[col].astype(str))
                encoders[col] = le
            else:
                le = encoders[col]
            df[col] = le.transform(df[col].astype(str))
        return encoders

    def handle(self, *args, **options):
        self.stdout.write("Starting training...\n")

        # --- Microbiology models ---
        micro_path = settings.DATA_DIR / 'salmonella_unified.csv'
        df_micro = pd.read_csv(micro_path)

        feature_cols = [
            'Citrate', 'MR', 'VP', 'Sucrose', 'Lactose', 'Glucose',
            'H2S_Production', 'Gas_Production', 'Motility', 'Indole',
            'Grams_Reaction', 'Coagulase', 'Production_System', 'Eggshell_Integrity'
        ]
        X = df_micro[feature_cols].copy()
        y_sal = df_micro['Salmonella']
        y_ecoli = df_micro['E.coli']
        y_saur = df_micro['S.aureus']

        micro_encoders = self._encode_df(X, fit=True)

        # Split using stratification on Salmonella
        X_train, X_test, y_sal_train, y_sal_test = train_test_split(
            X, y_sal, test_size=0.2, stratify=y_sal, random_state=42
        )
        y_ecoli_train, y_ecoli_test = train_test_split(
            y_ecoli, test_size=0.2, stratify=y_ecoli, random_state=42
        )
        y_saur_train, y_saur_test = train_test_split(
            y_saur, test_size=0.2, stratify=y_saur, random_state=42
        )

        for name, y_tr, y_te in [
            ('Salmonella', y_sal_train, y_sal_test),
            ('E. coli', y_ecoli_train, y_ecoli_test),
            ('S. aureus', y_saur_train, y_saur_test)
        ]:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_tr)
            pred = model.predict(X_test)
            acc = accuracy_score(y_te, pred)
            f1 = f1_score(y_te, pred, zero_division=0)
            self.stdout.write(f"{name} Model: Accuracy={acc:.3f}, F1={f1:.3f}")
            joblib.dump(model, settings.MODEL_DIR / f'{name.replace(" ","_").lower()}_model.pkl')

        joblib.dump(micro_encoders, settings.MODEL_DIR / 'micro_encoders.pkl')

        # --- Egg Production Model (single output) ---
        poultry_path = settings.DATA_DIR / 'poultry.csv'
        df_poultry = pd.read_csv(poultry_path)
        feature_cols_p = [
            'num_layers', 'feed_per_layer_g', 'water_litres', 'maize_percentage',
            'season', 'veterinary_visits_per_month', 'farmers_experience_years',
            'chicken_breed', 'age_weeks'
        ]
        Xp = df_poultry[feature_cols_p].copy()
        yp = df_poultry['eggs_per_day']   # single target

        poultry_encoders = self._encode_df(Xp, fit=True)

        Xp_train, Xp_test, yp_train, yp_test = train_test_split(
            Xp, yp, test_size=0.2, random_state=42
        )

        model_egg = RandomForestRegressor(n_estimators=100, random_state=42)
        model_egg.fit(Xp_train, yp_train)
        egg_pred = model_egg.predict(Xp_test)
        r2 = r2_score(yp_test, egg_pred)
        mae = mean_absolute_error(yp_test, egg_pred)
        self.stdout.write(f"Egg Production Model: R²={r2:.3f}, MAE={mae:.1f} eggs/day")

        joblib.dump(model_egg, settings.MODEL_DIR / 'egg_production_model.pkl')
        joblib.dump(poultry_encoders, settings.MODEL_DIR / 'poultry_encoders.pkl')

        # --- Biomass Model ---
        biomass_path = settings.DATA_DIR / 'biomass.xlsx'
        df_bio = pd.read_excel(biomass_path)
        Xb = df_bio[['F_time', 'Nano_P_conc', 'Carbon_Nitrogen']].copy()
        yb = df_bio['Biomass_wght']

        scaler = StandardScaler()
        Xb_scaled = scaler.fit_transform(Xb)

        Xb_train, Xb_test, yb_train, yb_test = train_test_split(
            Xb_scaled, yb, test_size=0.2, random_state=42
        )

        model_bio = RandomForestRegressor(n_estimators=100, random_state=42)
        model_bio.fit(Xb_train, yb_train)
        bio_pred = model_bio.predict(Xb_test)
        bio_r2 = r2_score(yb_test, bio_pred)
        bio_mae = mean_absolute_error(yb_test, bio_pred)
        self.stdout.write(f"Biomass Model: R²={bio_r2:.3f}, MAE={bio_mae:.2f}")

        joblib.dump(model_bio, settings.MODEL_DIR / 'biomass_model.pkl')
        joblib.dump(scaler, settings.MODEL_DIR / 'biomass_scaler.pkl')

        # Summaries
        self.stdout.write("\n--- Data Summaries ---")
        self.stdout.write(f"Microbiology: {len(df_micro)} rows, {len(feature_cols)} features, "
                          f"Sal+ {y_sal.sum()}, Ecoli+ {y_ecoli.sum()}, Saur+ {y_saur.sum()}")
        self.stdout.write(f"Poultry: {len(df_poultry)} rows, {len(feature_cols_p)} features")
        self.stdout.write(f"Biomass: {len(df_bio)} rows, 3 features")

        self.stdout.write(self.style.SUCCESS("\nAll models trained and saved!"))