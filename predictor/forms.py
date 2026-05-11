from django import forms

class MicrobiologyForm(forms.Form):
    citrate = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Citrate Utilization")
    mr = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Methyl Red (MR)")
    vp = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Voges‑Proskauer (VP)")
    sucrose = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Sucrose Fermentation")
    lactose = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Lactose Fermentation")
    glucose = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Glucose Fermentation")
    h2s_production = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="H₂S Production")
    gas_production = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Gas Production")
    motility = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Motility")
    indole = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Indole Production")
    grams_reaction = forms.ChoiceField(
        choices=[('positive', 'Gram Positive'), ('negative', 'Gram Negative')],
        label="Gram Reaction")
    coagulase = forms.ChoiceField(
        choices=[('+', '+'), ('-', '-')], label="Coagulase Test")
    production_system = forms.ChoiceField(
        choices=[('Cage', 'Cage'), ('Barn', 'Barn'), ('Free-Range', 'Free‑Range')],
        label="Production System")
    eggshell_integrity = forms.ChoiceField(
        choices=[('Intact', 'Intact'), ('Cracked', 'Cracked')],
        label="Eggshell Integrity")


class EggProductionForm(forms.Form):
    num_layers = forms.IntegerField(min_value=1, label="Number of Layers")
    feed_per_layer_g = forms.FloatField(min_value=0, label="Feed per Layer (g)")
    water_litres = forms.FloatField(min_value=0, label="Water (Litres)")
    maize_percentage = forms.FloatField(min_value=0, max_value=100, label="Maize Percentage")
    season = forms.ChoiceField(
        choices=[('rainy', 'Rainy'), ('dry', 'Dry')], label="Season")
    veterinary_visits_per_month = forms.IntegerField(min_value=0, label="Vet Visits per Month")
    farmers_experience_years = forms.IntegerField(min_value=0, label="Farmer Experience (Years)")
    chicken_breed = forms.ChoiceField(
        choices=[
            ('noiler', 'Noiler'), ('fulani', 'Fulani'),
            ('shika_brown', 'Shika Brown'), ('sasso', 'Sasso'), ('other', 'Other')
        ], label="Chicken Breed")
    age_weeks = forms.IntegerField(min_value=18, label="Age (Weeks)")


class BiomassForm(forms.Form):
    F_time = forms.FloatField(label='Time (F_time)', min_value=0)
    Nano_P_conc = forms.FloatField(label='Nanoparticle Concentration', min_value=0)
    Carbon_Nitrogen = forms.FloatField(label='Carbon/Nitrogen Ratio', min_value=0)