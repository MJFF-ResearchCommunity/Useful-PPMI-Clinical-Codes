"""
PPMI enrollment strata v3: adds HARMONIZED_COHORT
==================================================
HARMONIZED_COHORT merges (PROTOCOL_ERA x STUDY_ARM) cells whose enrollment
inclusion/exclusion criteria are SUBSTANTIVELY equivalent, based on side-by-side
reading of the governing protocol texts. Only enrollment-time information is
used; SAA and other post-enrollment biology never move anyone between groups.

Merge rules and their justification (protocol sections cited in the
supplementary table document):

  MERGED - substantively identical criteria:
  (a) AM2 (002 v1.2, 01Feb2021) and AM3.2 (002 v2.2, 30Jan2023) are merged for
      every cohort: the section-7 texts differ only in a low-dose RLS
      medication exception, an investigator-discretion catch-all exclusion,
      and optional screening blood/skin sampling - none alters the enrolled
      population's defining characteristics. -> "DATera" groups.
  (b) De novo sporadic PD is merged ACROSS PPMI-1 Original, Early Imaging
      (AV-133), and AM2/AM3: all require age >=30, PD diagnosis <=2 y,
      untreated (no current dopaminergic therapy; <=90 d lifetime levodopa/
      agonist; none within 60 d of baseline), core motor criteria, H&Y I-II,
      and a DAT-deficit screening gate. Early Imaging adds AV-133 PET but the
      same entry criteria (flagged via AV133STDY for sensitivity analyses).
  (c) HC merged across PPMI-1 Original and AM2/AM3: age >=30, no first-degree
      relative with PD, no significant neurological disorder, normal screening
      DaTscan. (PPMI-1 additionally required MoCA >26 - retained as a note,
      not a split, since it excludes few and the defining gates coincide.)
  (d) All AM4 prodromal arms are merged into one group: AM4 section 7.8 states
      a single criteria set (central UPSIT eligibility + asyn SAA status +
      age >=40, or >=30 for SNCA/rare) regardless of the ENRL arm recorded.

  KEPT SEPARATE - substantively different criteria:
  - PPMI-1 genetic PD (no disease-duration or treatment restriction, no DAT
    gate) vs AM2/AM3 genetic PD (LRRK2/GBA: <=2 y + H&Y I-II + DAT gate;
    SNCA/rare: no duration limit, H&Y I-III, DAT gate) vs AM4 genetic PD
    (SAA gate, UPSIT pathway).
  - Within AM2/AM3 genetic PD: LRRK2/GBA vs SNCA/rare (duration + staging
    criteria differ by protocol section).
  - AM4 sporadic PD (SAA-gated, hyposmia-enriched UPSIT pathway) vs the
    DAT-gated de novo group.
  - PD Normosmic / Normosmic LRRK2 (AM4 sections 7.6-7.7: diagnosis <=7 y,
    H&Y I-III, normosmic, no SAA gate) - a deliberately different population.
  - PPMI-1 prodromal pilot (fixed UPSIT <=10th percentile by age/sex or
    PSG-confirmed RBD; age >=60; designed ~80/20 DAT-deficit enrichment) vs
    AM2/AM3 prodromal (centrally optimized adaptive predictive criteria via
    the Online->Remote funnel; ~75/25 DAT selection). Structure is similar;
    ascertainment instruments and thresholds are not - kept separate by
    default. (A coarser mapping merging these is noted below as an option.)
  - PPMI-1 genetic non-manifest carriers (no DAT requirement) vs AM2/AM3
    genetic prodromal (funnel + DAT-based continuation) vs AM4 (SAA).
  - HC AM4 (UPSIT + SAA gate, no SPECT gate) vs the DAT-normal HC group.
  - SWEDD: unique by definition.

Output columns added: HARMONIZED_COHORT (and everything from v2).
"""

import pandas as pd
import numpy as np

PS_FILE  = 'data/Participant_Status_11Aug2026.csv'
SAA_FILE = 'data/SAA_Biospecimen_Analysis_Results_11Aug2026.csv'

# ============================================================================
# PART A - era + arm (identical logic to v2)
# ============================================================================
df = pd.read_csv(PS_FILE)
df['ENROLL_DATE_parsed'] = pd.to_datetime(df['ENROLL_DATE'], format='%m/%Y', errors='coerce')
df['ENROLL_YEAR'] = df['ENROLL_DATE_parsed'].dt.year

FLAGS = ['ENRLSRDC', 'ENRLNORM', 'ENRLHPSM', 'ENRLRBD',
         'ENRLLRRK2', 'ENRLGBA', 'ENRLSNCA', 'ENRLPINK1', 'ENRLPRKN', 'ENRLOTHGV']
df[FLAGS] = df[FLAGS].fillna(0).astype(int)
GENETIC = ['ENRLLRRK2', 'ENRLGBA', 'ENRLSNCA', 'ENRLPINK1', 'ENRLPRKN', 'ENRLOTHGV']
RARE    = ['ENRLPINK1', 'ENRLPRKN', 'ENRLOTHGV']

def protocol_era(row):
    if row['SCREENEDAM'] == 2: return 'PPMI2_AM2'
    if row['SCREENEDAM'] == 3: return 'PPMI2_AM3'
    if row['SCREENEDAM'] == 4: return 'PPMI2_AM4'
    if 5000 <= row['PATNO'] < 6000: return 'EarlyImaging_AV133'
    if row['PATNO'] < 10000:  return 'PPMI1_Original'
    if row['PATNO'] < 100000: return 'PPMI1_GeneticProdromal'
    return 'PPMI2_AM_unknown'

df['PROTOCOL_ERA'] = df.apply(protocol_era, axis=1)
df['ENROLLMENT_COHORT'] = df['PROTOCOL_ERA'] + '|' + df['COHORT_DEFINITION']

def study_arm(row):
    cd = row['COHORT_DEFINITION']
    n_gen = sum(row[g] for g in GENETIC)
    if cd == 'Healthy Control': return 'HC'
    if cd == 'SWEDD':           return 'SWEDD'
    if cd == "Parkinson's Disease":
        if row['ENRLNORM'] == 1:
            return 'PD_Normosmic_LRRK2' if row['ENRLLRRK2'] == 1 else 'PD_Normosmic'
        if n_gen > 1: return 'PD_MultiGenetic'
        if row['ENRLLRRK2'] == 1: return 'PD_LRRK2'
        if row['ENRLGBA']  == 1: return 'PD_GBA'
        if row['ENRLSNCA'] == 1: return 'PD_SNCA'
        if any(row[g] == 1 for g in RARE): return 'PD_RareGenetic'
        if row['ENRLSRDC'] == 1: return 'PD_Sporadic'
        if row['PROTOCOL_ERA'] in ('PPMI1_Original', 'EarlyImaging_AV133'):
            return 'PD_Sporadic'
        return 'PD_ArmUnrecorded'
    if cd == 'Prodromal':
        has_hpsm, has_rbd = row['ENRLHPSM'] == 1, row['ENRLRBD'] == 1
        if n_gen >= 1 and (has_hpsm or has_rbd): return 'Prodromal_GeneticPlusPhenotype'
        if n_gen > 1: return 'Prodromal_MultiGenetic'
        if row['ENRLLRRK2'] == 1: return 'Prodromal_LRRK2'
        if row['ENRLGBA']  == 1: return 'Prodromal_GBA'
        if row['ENRLSNCA'] == 1: return 'Prodromal_SNCA'
        if any(row[g] == 1 for g in RARE): return 'Prodromal_RareGenetic'
        if has_hpsm and has_rbd: return 'Prodromal_Hyposmia_RBD'
        if has_hpsm: return 'Prodromal_Hyposmia'
        if has_rbd:  return 'Prodromal_RBD'
        return 'Prodromal_ArmUnrecorded'
    return 'Undetermined'

df['STUDY_ARM'] = df.apply(study_arm, axis=1)
df['COHORT_STRATUM'] = df['PROTOCOL_ERA'] + '|' + df['STUDY_ARM']

EVER_ENROLLED = {'Enrolled', 'Withdrew', 'Complete', 'Withdraw Deceased',
                 'Baseline', 'Baseline Withdraw'}
SCREEN_ONLY   = {'Screen failed', 'Excluded', 'Screened', 'Declined'}
df['PARTICIPATION'] = df['ENROLL_STATUS'].apply(
    lambda s: 'ever_enrolled' if s in EVER_ENROLLED
    else ('screened_not_enrolled' if s in SCREEN_ONLY else 'pre_screening'))

# ============================================================================
# PART B - HARMONIZED_COHORT
# ============================================================================
DAT_ERAS   = {'PPMI2_AM2', 'PPMI2_AM3'}                       # rule (a)
DENOVO_ERAS = {'PPMI1_Original', 'EarlyImaging_AV133'} | DAT_ERAS   # rule (b)
GEN_PD_ARMS = {'PD_LRRK2', 'PD_GBA', 'PD_SNCA', 'PD_RareGenetic', 'PD_MultiGenetic'}
GEN_PRO_ARMS = {'Prodromal_LRRK2', 'Prodromal_GBA', 'Prodromal_SNCA',
                'Prodromal_RareGenetic', 'Prodromal_MultiGenetic',
                'Prodromal_GeneticPlusPhenotype'}

def harmonized_cohort(row):
    era, arm = row['PROTOCOL_ERA'], row['STUDY_ARM']

    if era == 'PPMI2_AM_unknown':
        return 'Unresolved_PPMI2_pending'

    # ---- Healthy Controls ----
    if arm == 'HC':
        return 'HC_DATnormal' if era in ({'PPMI1_Original'} | DAT_ERAS) else 'HC_UPSIT_SAAgated_AM4'

    if arm == 'SWEDD':
        return 'SWEDD_PPMI1'

    # ---- Parkinson's disease ----
    if arm == 'PD_Sporadic':
        return 'PD_DeNovoSporadic_DATgated' if era in DENOVO_ERAS else 'PD_DeNovoSporadic_SAAgated_AM4'
    if arm in ('PD_Normosmic', 'PD_Normosmic_LRRK2'):
        return 'PD_Normosmic_AM4'
    if arm in GEN_PD_ARMS:
        if era == 'PPMI1_GeneticProdromal':
            return 'PD_Genetic_PPMI1_unrestricted'
        if era in DAT_ERAS:
            # protocol 002 sections 7.3 vs 7.4 impose different duration/staging
            if arm in ('PD_LRRK2', 'PD_GBA', 'PD_MultiGenetic'):
                return 'PD_LRRK2GBA_Recent_DATgated'
            return 'PD_SNCARare_DATgated'
        if era == 'PPMI2_AM4':
            return 'PD_Genetic_SAAgated_AM4'
    if arm == 'PD_ArmUnrecorded':
        return 'Unclassified_' + era

    # ---- Prodromal ----
    if arm.startswith('Prodromal'):
        if era == 'PPMI2_AM4':
            return 'Prodromal_UPSIT_SAAgated_AM4'          # rule (d): single AM4 criteria set
        if era == 'PPMI1_GeneticProdromal':
            if arm in GEN_PRO_ARMS:
                return 'Prodromal_GeneticCarrier_PPMI1'
            if arm in ('Prodromal_Hyposmia', 'Prodromal_RBD', 'Prodromal_Hyposmia_RBD'):
                return 'Prodromal_Pilot_HPSM_RBD_PPMI1'
            return 'Unclassified_' + era
        if era in DAT_ERAS:
            if arm == 'Prodromal_Hyposmia':      return 'Prodromal_Hyposmia_DATera'
            if arm == 'Prodromal_RBD':           return 'Prodromal_RBD_DATera'
            if arm == 'Prodromal_Hyposmia_RBD':  return 'Prodromal_HyposmiaRBD_DATera'
            if arm in GEN_PRO_ARMS:              return 'Prodromal_Genetic_DATera'
            return 'Unclassified_' + era
    return 'Unclassified_' + era

df['HARMONIZED_COHORT'] = df.apply(harmonized_cohort, axis=1)

# ============================================================================
# PART C - SAA descriptive overlay (unchanged from v2)
# ============================================================================
saa = pd.read_csv(SAA_FILE)
saa['RUNDATE'] = pd.to_datetime(saa['RUNDATE'], errors='coerce')

def resolve_status(g):
    g237 = g[g['PROJECTID'] == 237]
    pick = (g237 if len(g237) else g).sort_values('RUNDATE').iloc[-1]
    return pd.Series({'status': pick['SAA_Status'], 'type': pick['SAA_Type'],
                      'event': pick['CLINICAL_EVENT'], 'rundate': pick['RUNDATE']})

entry = (saa[saa['CLINICAL_EVENT'].isin(['SC', 'BL'])]
         .groupby('PATNO').apply(resolve_status)
         .rename(columns={'status': 'SAA_AT_ENTRY', 'type': 'SAA_AT_ENTRY_TYPE'}))
latest = (saa.groupby('PATNO').apply(resolve_status)
          .rename(columns={'status': 'SAA_LATEST', 'type': 'SAA_LATEST_TYPE',
                           'event': 'SAA_LATEST_EVENT'}))
df = (df.merge(entry[['SAA_AT_ENTRY', 'SAA_AT_ENTRY_TYPE']],
               left_on='PATNO', right_index=True, how='left')
        .merge(latest[['SAA_LATEST', 'SAA_LATEST_TYPE', 'SAA_LATEST_EVENT']],
               left_on='PATNO', right_index=True, how='left'))
df['SAA_TESTED'] = df['SAA_LATEST'].notna()

# ============================================================================
# PART D - Reports
# ============================================================================
pd.set_option('display.width', 240)
enr = df[df['PARTICIPATION'] == 'ever_enrolled']

print("=" * 110)
print("COHORT_DEFINITION x PROTOCOL_ERA (ever-enrolled)")
print("=" * 110)
print(pd.crosstab(enr['COHORT_DEFINITION'], enr['PROTOCOL_ERA']).to_string())

print("\n" + "=" * 110)
print("STUDY_ARM x PROTOCOL_ERA (ever-enrolled)")
print("=" * 110)
print(pd.crosstab(enr['STUDY_ARM'], enr['PROTOCOL_ERA']).to_string())

print("\n" + "=" * 110)
print("Two-level counts: HARMONIZED_COHORT x COHORT_STRATUM (ever-enrolled)")
print("=" * 110)
level_counts = (enr.groupby(['HARMONIZED_COHORT', 'COHORT_STRATUM'])
                .size()
                .reset_index(name='n')
                .sort_values(['HARMONIZED_COHORT', 'n'], ascending=[True, False]))
print(level_counts.to_string(index=False))

print("\n" + "=" * 110)
print("Mapping audit: HARMONIZED_COHORT x PROTOCOL_ERA (ever-enrolled) - verify merges are as intended")
print("=" * 110)
print(pd.crosstab(enr['HARMONIZED_COHORT'], enr['PROTOCOL_ERA']).to_string())

print("\n" + "=" * 110)
print("Within-group heterogeneity check: SAA_AT_ENTRY positivity by HARMONIZED_COHORT x era (merged groups only)")
print("=" * 110)
merged_groups = ['PD_DeNovoSporadic_DATgated', 'HC_DATnormal',
                 'Prodromal_Hyposmia_DATera', 'Prodromal_RBD_DATera']
sub = enr[enr['HARMONIZED_COHORT'].isin(merged_groups) & enr['SAA_AT_ENTRY'].notna()]
chk = (sub.assign(pos=(sub['SAA_AT_ENTRY'] == 'Positive'))
          .groupby(['HARMONIZED_COHORT', 'PROTOCOL_ERA'])['pos']
          .agg(n='size', pos_pct=lambda s: round(100 * s.mean(), 1)))
print(chk.to_string())

out = 'output/Participant_Status_HarmonizedCohorts_11Aug2026.csv'
keep_first = ['PATNO', 'HARMONIZED_COHORT', 'ENROLLMENT_COHORT', 'PROTOCOL_ERA',
              'STUDY_ARM', 'COHORT_STRATUM', 'PARTICIPATION',
              'SAA_AT_ENTRY', 'SAA_AT_ENTRY_TYPE', 'SAA_LATEST', 'SAA_LATEST_TYPE',
              'SAA_LATEST_EVENT', 'SAA_TESTED']
cols = keep_first + [c for c in df.columns if c not in keep_first]
df[cols].to_csv(out, index=False)
print(f"\nSaved: {out}")
