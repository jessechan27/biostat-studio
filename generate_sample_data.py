import os
import numpy as np
import pandas as pd

os.makedirs('sample_data', exist_ok=True)

# 1. Clinical Trial Data (Drug Treatment Response)
np.random.seed(42)
n_patients = 120
treatment_groups = np.random.choice(['Control (Placebo)', 'Treatment A (Low Dose)', 'Treatment B (High Dose)'], size=n_patients, p=[0.33, 0.33, 0.34])
gender = np.random.choice(['Female', 'Male'], size=n_patients, p=[0.52, 0.48])
age = np.random.normal(loc=58, scale=11, size=n_patients).clip(25, 85).round().astype(int)
bmi = np.random.normal(loc=26.5, scale=4.2, size=n_patients).clip(17, 42).round(1)

# Baseline biomarker
baseline_biomarker = np.random.normal(loc=120, scale=25, size=n_patients).round(1)

# Post-treatment biomarker with treatment effect
treatment_effect = np.where(treatment_groups == 'Control (Placebo)', np.random.normal(2, 8, n_patients),
                   np.where(treatment_groups == 'Treatment A (Low Dose)', np.random.normal(-18, 10, n_patients),
                            np.random.normal(-32, 12, n_patients)))
post_biomarker = (baseline_biomarker + treatment_effect).clip(20, 250).round(1)

# Clinical response (Categorical)
reduction_pct = (baseline_biomarker - post_biomarker) / baseline_biomarker * 100
response_status = np.where(reduction_pct > 20, 'Responder', 'Non-Responder')
adverse_event = np.random.choice(['None', 'Mild Nausea', 'Fatigue', 'Headache'], size=n_patients, p=[0.65, 0.18, 0.12, 0.05])

df_clinical = pd.DataFrame({
    'Patient_ID': [f'PT-{1000+i}' for i in range(n_patients)],
    'Treatment_Group': treatment_groups,
    'Gender': gender,
    'Age': age,
    'BMI': bmi,
    'Baseline_Biomarker': baseline_biomarker,
    'Post_Biomarker': post_biomarker,
    'Biomarker_Change': (post_biomarker - baseline_biomarker).round(1),
    'Reduction_Percent': reduction_pct.round(1),
    'Clinical_Response': response_status,
    'Adverse_Event': adverse_event
})

df_clinical.to_excel('sample_data/clinical_trial_data.xlsx', index=False, sheet_name='Trial_Cohort')
print("Generated sample_data/clinical_trial_data.xlsx")

# 2. Cancer Survival Data (Kaplan-Meier & Cox Proportional Hazards)
np.random.seed(101)
n_cases = 150
stages = np.random.choice(['Stage I', 'Stage II', 'Stage III', 'Stage IV'], size=n_cases, p=[0.25, 0.3, 0.25, 0.2])
mutation_status = np.random.choice(['Wild Type (WT)', 'Mutant (MUT)'], size=n_cases, p=[0.55, 0.45])
chemo = np.random.choice(['Standard Chemo', 'Targeted Therapy'], size=n_cases, p=[0.5, 0.5])

# Survival time simulation based on risk factors
base_risk = 0.015
stage_hazard = {'Stage I': 0.5, 'Stage II': 1.0, 'Stage III': 2.0, 'Stage IV': 3.8}
mutation_hazard = {'Wild Type (WT)': 1.0, 'Mutant (MUT)': 1.7}
chemo_hazard = {'Standard Chemo': 1.0, 'Targeted Therapy': 0.6}

times = []
events = []
for i in range(n_cases):
    h = base_risk * stage_hazard[stages[i]] * mutation_hazard[mutation_status[i]] * chemo_hazard[chemo[i]]
    t = np.random.exponential(1.0 / h)
    # Study ended at month 60
    if t > 60:
        times.append(60.0)
        events.append(0) # Censored
    else:
        times.append(round(float(t), 1))
        events.append(1) # Event (Death/Relapse)

df_survival = pd.DataFrame({
    'Sample_ID': [f'CAS-{2000+i}' for i in range(n_cases)],
    'Stage': stages,
    'Mutation_Status': mutation_status,
    'Therapy': chemo,
    'Survival_Months': times,
    'Event_Status': events, # 1=Dead, 0=Alive
    'Age_at_Diagnosis': np.random.normal(62, 9, n_cases).clip(35, 88).round().astype(int),
    'Tumor_Size_cm': np.random.gamma(2, 1.8, n_cases).round(2)
})

df_survival.to_excel('sample_data/cancer_survival_data.xlsx', index=False, sheet_name='Survival_Cohort')
print("Generated sample_data/cancer_survival_data.xlsx")

# 3. Gene Expression & Volcano Data
np.random.seed(202)
n_genes = 200
gene_names = [f'GENE_{i:04d}' for i in range(1, n_genes + 1)]
# Add some notable biomarker names
gene_names[0:10] = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'VEGFA', 'KRAS', 'PTEN', 'CD274_PDL1', 'ERBB2_HER2', 'IL6']

log2_fc = np.random.normal(loc=0.1, scale=1.4, size=n_genes).round(3)
# Make key genes significantly modulated
log2_fc[0] = -2.8  # TP53 down
log2_fc[1] = 3.2   # EGFR up
log2_fc[2] = -1.9
log2_fc[4] = 2.5
log2_fc[7] = 2.1

raw_p = np.random.beta(0.5, 3.5, size=n_genes)
raw_p[0:10] = [1.2e-7, 4.5e-9, 2.1e-5, 3.8e-2, 8.4e-6, 0.045, 0.001, 5.2e-6, 0.0003, 0.002]
neg_log10_p = (-np.log10(np.clip(raw_p, 1e-12, 1.0))).round(3)

regulation = []
for lfc, p in zip(log2_fc, raw_p):
    if p < 0.05 and lfc >= 1.0:
        regulation.append('Up-regulated')
    elif p < 0.05 and lfc <= -1.0:
        regulation.append('Down-regulated')
    else:
        regulation.append('Not Significant')

df_genes = pd.DataFrame({
    'Gene_Symbol': gene_names,
    'Log2_Fold_Change': log2_fc,
    'P_Value': raw_p.round(8),
    'Neg_Log10_PValue': neg_log10_p,
    'Regulation_Status': regulation,
    'Control_Mean_Expression': np.random.uniform(50, 5000, n_genes).round(1),
    'Treated_Mean_Expression': np.random.uniform(50, 5000, n_genes).round(1)
})

df_genes.to_excel('sample_data/gene_expression_volcano.xlsx', index=False, sheet_name='Differential_Expression')
print("Generated sample_data/gene_expression_volcano.xlsx")
