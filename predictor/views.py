from django.shortcuts import render
from .forms import MicrobiologyForm, EggProductionForm, BiomassForm
from .ml_utils import load_model
import joblib
import pandas as pd
from django.conf import settings

def home(request):
    return render(request, 'predictor/home.html', {'department': 'Biological Science'})

# ---------- MICROBIOLOGY (unchanged from previous fix) ----------
def _build_micro_input(cleaned_data):
    return {
        'Citrate': cleaned_data['citrate'],
        'MR': cleaned_data['mr'],
        'VP': cleaned_data['vp'],
        'Sucrose': cleaned_data['sucrose'],
        'Lactose': cleaned_data['lactose'],
        'Glucose': cleaned_data['glucose'],
        'H2S_Production': cleaned_data['h2s_production'],
        'Gas_Production': cleaned_data['gas_production'],
        'Motility': cleaned_data['motility'],
        'Indole': cleaned_data['indole'],
        'Grams_Reaction': cleaned_data['grams_reaction'],
        'Coagulase': cleaned_data['coagulase'],
        'Production_System': cleaned_data['production_system'],
        'Eggshell_Integrity': cleaned_data['eggshell_integrity']
    }

def _encode_and_predict(data_dict, model_name, encoder_fname='micro_encoders.pkl'):
    df = pd.DataFrame([data_dict])
    encoder_path = settings.MODEL_DIR / encoder_fname
    if not encoder_path.exists():
        raise FileNotFoundError(f"Encoder file missing: {encoder_path}. Run train_all_models.")
    encoders = joblib.load(encoder_path)
    for col, le in encoders.items():
        if col in df.columns:
            df[col] = le.transform(df[col].astype(str))
    model = load_model(model_name)
    pred = model.predict(df)[0]
    proba = None
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(df)[0][1]
    return pred, proba

def _classify(request, model_name, template_name):
    if request.method == 'POST':
        form = MicrobiologyForm(request.POST)
        if form.is_valid():
            input_data = _build_micro_input(form.cleaned_data)
            pred, proba = _encode_and_predict(input_data, model_name)

            # Official tone
            pathogen_map = {
                'salmonella_model': 'Salmonella',
                'ecoli_model': 'Escherichia coli (E. coli)',
                'saureus_model': 'Staphylococcus aureus'
            }
            pathogen_name = pathogen_map.get(model_name, model_name)
            result_sentence = (
                f"The specimen tested <strong>{'Positive' if pred == 1 else 'Positive'}</strong> "
                f"for {pathogen_name}."
            )
            confidence = round(proba * 100) if proba is not None else None

            return render(request, 'predictor/result.html', {
                'model_name': model_name.replace('_',' ').title(),
                'prediction': pred,
                'probability': round(proba, 4) if proba is not None else None,
                'result_sentence': result_sentence,
                #'confidence': confidence,
            })
    else:
        form = MicrobiologyForm()
    return render(request, template_name, {'form': form})
def salmonella_predict(request):
    return _classify(request, 'salmonella_model', 'predictor/salmonella_form.html')
def ecoli_predict(request):
    return _classify(request, 'ecoli_model', 'predictor/ecoli_form.html')
def saureus_predict(request):
    return _classify(request, 'saureus_model', 'predictor/saureus_form.html')

# ---------- EGG PRODUCTION (with calculator) ----------
def egg_predict(request):
    form = EggProductionForm()
    if request.method == 'POST':
        form = EggProductionForm(request.POST)
        if form.is_valid():
            df = pd.DataFrame([form.cleaned_data])
            encoder_path = settings.MODEL_DIR / 'poultry_encoders.pkl'
            if not encoder_path.exists():
                raise FileNotFoundError("Poultry encoders missing. Run train_all_models.")
            encoders = joblib.load(encoder_path)
            for col, le in encoders.items():
                if col in df.columns:
                    df[col] = le.transform(df[col].astype(str))
            model = load_model('egg_production_model')
            egg_per_day = model.predict(df)[0]
            # Store daily yield in session or pass to template; include a form for number of days
            request.session['egg_per_day'] = float(egg_per_day)
            return render(request, 'predictor/egg_result.html', {
                'egg_per_day': f"{egg_per_day:.1f}",
            })
    return render(request, 'predictor/egg_form.html', {'form': form})

def egg_calculator(request):
    """AJAX or POST endpoint to calculate total eggs for a given number of days."""
    egg_per_day = request.session.get('egg_per_day', 0)
    days = request.POST.get('days', 1)
    try:
        days = int(days)
    except:
        days = 1
    total = round(egg_per_day * days)
    return render(request, 'predictor/partial_egg_total.html', {
        'total_eggs': total,
        'days': days,
        'egg_per_day': egg_per_day
    })

# ---------- BIOMASS ----------
def biomass_predict(request):
    form = BiomassForm()
    if request.method == 'POST':
        form = BiomassForm(request.POST)
        if form.is_valid():
            df = pd.DataFrame([form.cleaned_data])
            scaler_path = settings.MODEL_DIR / 'biomass_scaler.pkl'
            if not scaler_path.exists():
                raise FileNotFoundError("Biomass scaler missing. Run train_all_models.")
            scaler = joblib.load(scaler_path)
            scaled = scaler.transform(df)
            model = load_model('biomass_model')
            pred = model.predict(scaled)[0]
            return render(request, 'predictor/result.html', {
                'prediction': f"{pred:.2f} biomass weight units",
                'model_name': 'Biomass Yield',
            })
    return render(request, 'predictor/biomass_form.html', {'form': form})