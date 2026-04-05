## Yucatan -- Carbon Pricing Overlap Analysis

State & Trends of Carbon Pricing publication.
Three-instrument Venn: S (state tax) x F (federal IEPS) x E (Pilot ETS).

### Quick start
```bash
cd states/yucatan
python 01_clean.py    # Extract inventory, validate, create scope mapping
python 02_estimate.py # Eight-segment Venn decomposition
python 03_outputs.py  # Publication figures and tables
```

### Data
- `data/raw/`: Source PDF (IEEGYCEI 2010-2023, SDS Yucatan 2024)
- `data/processed/`: Cleaned CSVs from 01_clean.py and 02_estimate.py

### Outputs
- `outputs/tables/`: Publication-ready CSV tables
- `outputs/figures/`: PNG figures (Venn segments, coverage summary, HFC breakdown)

### Key findings
- Yucatan is the first state with HFCs both in tax scope AND quantified
  in the inventory (334 GgCO2e, 3.2% of state total)
- Electricity is 93.5% natural gas -- minimal S n F overlap in power sector
- Cement process CO2 (318 GgCO2e) in S n E but not F
- State is a net carbon sink (-2,686 GgCO2e net)
- Best-quality inventory: AR5 GWPs natively, 2023 data, no conversion needed

### Documentation
- `docs/data_sources.md` -- Source document details and validation
- `docs/assumptions_02.md` -- All estimation assumptions
- `docs/methodology.md` -- Methodology note
