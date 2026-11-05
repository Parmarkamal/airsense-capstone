WHO_GUIDELINES = """
WHO Air Quality Guidelines — Global Update 2021

# Overview
The World Health Organization (WHO) updated its Air Quality Guidelines (AQGs) in 2021, 
providing evidence-based recommendations to protect human health from the adverse effects 
of air pollution. These are the most comprehensive and authoritative guidelines globally.

---

# Key Pollutant Limits (WHO 2021 AQGs)

## PM2.5 (Fine Particulate Matter — diameter < 2.5 µm)
- Annual mean: 5 µg/m³
- 24-hour mean: 15 µg/m³ (99th percentile, 3–4 days/year)

Sources: Vehicle exhaust, biomass burning, industrial emissions, secondary aerosol formation.
Health Effects: Penetrates deep into the lungs and bloodstream. Causes cardiovascular disease, 
stroke, lung cancer, COPD, and premature death. Children and elderly are most vulnerable.

## PM10 (Coarse Particulate Matter — diameter 2.5–10 µm)
- Annual mean: 15 µg/m³
- 24-hour mean: 45 µg/m³ (99th percentile)

Sources: Road dust, construction sites, industrial processes, sea salt.
Health Effects: Causes respiratory inflammation, aggravates asthma, and reduces lung function.

## NO2 (Nitrogen Dioxide)
- Annual mean: 10 µg/m³
- 24-hour mean: 25 µg/m³

Sources: Vehicle emissions, power plants, industrial combustion.
Health Effects: Inflames airways, worsens asthma attacks, increases susceptibility to respiratory infections.

## O3 (Ozone)
- Peak season 8-hour mean: 60 µg/m³

Sources: Secondary pollutant formed by sunlight reacting with NOx and VOCs.
Health Effects: Chest tightness, coughing, worsening of asthma and COPD. Peaks during hot, sunny afternoons.

## CO (Carbon Monoxide)
- 24-hour mean: 4 mg/m³

Sources: Incomplete combustion (vehicles, cooking stoves, fires).
Health Effects: Reduces oxygen-carrying capacity of blood. Dangerous for heart patients and fetuses.

## SO2 (Sulfur Dioxide)
- 24-hour mean: 40 µg/m³

Sources: Fossil fuel combustion, industrial smelting.
Health Effects: Causes bronchoconstriction, worsens asthma. Linked to acid rain.

---

# Health Impact Summary by Population Group

## General Population
- Short-term: Increased hospital admissions for respiratory and cardiovascular conditions.
- Long-term: Reduced life expectancy.

## Sensitive Groups (Priority Protection Required)
1. Children (under 14 years): Developing lungs are disproportionately affected. Avoid outdoor exercise when AQI > 100.
2. Elderly (over 65 years): Weaker immune system, higher risk of stroke and heart failure. Stay indoors when AQI > 50.
3. Pregnant women: Air pollution linked to low birth weight, preterm birth, and infant mortality. Minimize outdoor exposure above AQI 50.
4. Patients with asthma or COPD: Even short-term spikes cause acute attacks. Must always carry inhalers.
5. Patients with heart disease: PM2.5 triggers cardiac events. No outdoor exercise when AQI > 50.
6. Outdoor workers: Daily prolonged exposure increases occupational risk. Use N95 masks above AQI 150.

---

# Protective Measures by Pollution Level

## AQI 0–50 (Good) — No action required
- Enjoy outdoor activities freely.
- Normal indoor ventilation is fine.

## AQI 51–100 (Moderate / Satisfactory) — Cautious
- Sensitive individuals should consider reducing prolonged outdoor exertion.
- Close windows if near traffic or industrial areas.

## AQI 101–200 (Moderate/Poor) — Caution Advised
- Reduce prolonged or heavy outdoor activities.
- Wear N95 masks outdoors if possible.
- Use air purifiers indoors (HEPA filter).
- Avoid exercising near busy roads.

## AQI 201–300 (Poor/Very Poor) — Health Alert
- Avoid outdoor physical activity.
- Keep windows and doors shut.
- Use air conditioning with recirculation mode.
- Medical check-up for sensitive groups if persistent.

## AQI > 300 (Severe/Hazardous) — Emergency Conditions
- All outdoor activities must cease.
- Seek medical attention if experiencing breathing difficulty.
- Consider temporary relocation for highly sensitive individuals.

---

# Air Pollution and COVID-19 / Respiratory Illness
Research shows that chronic exposure to air pollution worsens COVID-19 outcomes. 
Regions with higher PM2.5 levels had significantly higher COVID-19 mortality rates 
(Harvard T.H. Chan School of Public Health, 2020).

# Economic Impact
The World Bank estimates that air pollution costs the global economy $5 trillion annually 
in welfare losses, primarily from premature deaths and productivity losses.

# India-Specific Context
India bears 17.8% of the global disease burden from air pollution (State of Global Air 2020).
The Indo-Gangetic Plain (Delhi, Agra, Kanpur) is one of the world's most polluted airsheds.
Stubble burning in Punjab and Haryana peaks in October–November, causing severe Delhi smog events.
"""

CPCB_GUIDELINES = """
Central Pollution Control Board (CPCB) — Indian Air Quality Standards & NAAQS

# National Ambient Air Quality Standards (NAAQS) — India, Revised 2009

The CPCB, under the Ministry of Environment, Forest and Climate Change (MoEFCC), 
sets legally binding standards for ambient air quality in India under the Air 
(Prevention and Control of Pollution) Act, 1981.

---

# AQI Categories (CPCB India — 6-Tier Scale)

## Category 1: Good (AQI 0–50)
- Color Code: Green
- Health Message: Minimal impact. Air quality is considered satisfactory.
- Advisory: Ideal for all outdoor activities including running, cycling, and sports.

## Category 2: Satisfactory (AQI 51–100)
- Color Code: Light Green
- Health Message: Minor breathing discomfort to sensitive people.
- Advisory: Unusually sensitive individuals should consider reducing prolonged outdoor exertion.

## Category 3: Moderate (AQI 101–200)
- Color Code: Yellow
- Health Message: Breathing discomfort to people with lung disease, asthma, and heart disease.
- Advisory: People with lung, heart disease, elderly and children should reduce prolonged outdoor exertion.

## Category 4: Poor (AQI 201–300)
- Color Code: Orange
- Health Message: Breathing discomfort to most people on prolonged exposure.
- Advisory: Avoid prolonged outdoor activities. People with respiratory/heart disease should stay indoors.
- Required Actions: Issue health advisory through local authorities, hospitals.

## Category 5: Very Poor (AQI 301–400)
- Color Code: Red
- Health Message: Respiratory illness on prolonged exposure. Affects healthy people and seriously impacts those with existing disease.
- Advisory: Avoid outdoor activities. People with existing diseases should remain indoors.
- Required Actions: Schools may consider closing. Industries must reduce emissions.

## Category 6: Severe (AQI 401–500+)
- Color Code: Dark Red / Maroon
- Health Message: Affects healthy people and seriously impacts those with existing disease. Even light outdoor activity is harmful.
- Advisory: Full outdoor restrictions. Emergency health response. Graded Response Action Plan (GRAP) activated.
- Required Actions: Construction halted, diesel generators banned, trucks restricted, Odd-Even vehicle rationing.

---

# NAAQS Pollutant Standards (Annual / 24-Hour Averages)

| Pollutant | Time Period | Standard |
|-----------|------------|----------|
| PM2.5 | Annual | 40 µg/m³ |
| PM2.5 | 24-hour | 60 µg/m³ |
| PM10 | Annual | 60 µg/m³ |
| PM10 | 24-hour | 100 µg/m³ |
| NO2 | Annual | 40 µg/m³ |
| NO2 | 24-hour | 80 µg/m³ |
| SO2 | Annual | 50 µg/m³ |
| SO2 | 24-hour | 80 µg/m³ |
| O3 | 8-hour | 100 µg/m³ |
| CO | 8-hour | 2 mg/m³ |

Note: Indian standards are currently less stringent than WHO 2021 AQGs.
India is working towards progressive tightening under the National Clean Air Programme (NCAP).

---

# Graded Response Action Plan (GRAP) — Delhi NCR

GRAP is a set of emergency measures activated based on AQI levels in Delhi NCR:

## Stage 1 (AQI 201–300 — Poor)
- Enhanced mechanical road sweeping
- Ban on burning of garbage/biomass/construction waste
- Increased water sprinkling on roads

## Stage 2 (AQI 301–400 — Very Poor)
- Ban on diesel gensets (except essential services)
- Restrictions on construction and demolition activities
- Enhanced parking fees in city centers

## Stage 3 (AQI 401–450 — Severe)
- BS III petrol and BS IV diesel 4-wheelers banned
- Mining activities suspended
- State transport buses from neighboring states restricted

## Stage 4 (AQI > 450 — Severe+)
- Odd-Even vehicle rationing scheme
- Schools switch to online mode
- All non-essential construction halted
- Emergency meeting of Commission for Air Quality Management (CAQM)

---

# Indian Cities Monitored — Typical AQI Patterns

## Delhi
- Worst months: October–January (post-monsoon, stubble burning, winter inversions)
- Best months: July–August (monsoon washes atmosphere)
- Primary sources: Vehicles (40%), industry (29%), road dust (16%), biomass burning (15%)

## Mumbai
- Generally better than Delhi due to sea breeze ventilation
- Peak pollution: November–January
- Primary sources: Vehicles, construction, waste burning

## Ahmedabad
- Industrial city with petrochemical complexes
- Moderate to Poor AQI year-round
- Primary sources: Industrial emissions, vehicles

## Bengaluru
- Relatively clean due to elevation and vegetation
- Worsening due to rapid urbanization
- Primary sources: Vehicles, construction

## Pune
- Mixed pattern — cleaner than Delhi but urbanizing rapidly
- Primary sources: Vehicles, industrial area (Pimpri-Chinchwad)

## Gandhinagar
- Capital city with lower industrial load
- Generally cleaner than Ahmedabad

---

# Health Advisories for Indian Cities (CPCB)

## Children (Schools & Parents)
- Avoid outdoor PE activities when AQI > 100
- Schools should close outdoor sports above AQI 200
- Emergency school closure recommended above AQI 400

## Senior Citizens
- Should minimize outdoor activity when AQI > 50
- Must stay indoors when AQI > 150
- Consult physician if experiencing breathlessness

## Athletes & Fitness Enthusiasts
- Outdoor jogging/running not recommended above AQI 100
- Gyms and indoor exercise preferred above AQI 150
- Race events should be cancelled above AQI 200

## Commuters
- Use N95/FFP2 masks when AQI > 150
- Avoid peak traffic hours (8–10 AM, 5–8 PM)
- Choose metro/bus over personal vehicles when possible
"""

AQI_HEALTH_ADVISORY = """
AirSense Health Advisory Knowledge Base — Common Questions & Evidence-Based Answers

# Morning Outdoor Exercise

## Q: Is it safe to jog in the morning when AQI is 150?
A: No. AQI 150 falls in the CPCB 'Moderate' category. During exercise, breathing rate increases 
5–10 times, meaning you inhale far more pollutants per minute than at rest. The WHO and CPCB both 
recommend avoiding heavy outdoor exercise when AQI exceeds 100. If you must exercise, do so indoors, 
or choose very light activities such as walking in less-congested green areas.

## Q: What is the best time of day to exercise outdoors?
A: Generally, AQI is lowest between 4–7 AM (before traffic peaks and before photochemical reactions 
form ozone). Avoid exercising from 8–11 AM (rush hour traffic) and 12–3 PM (peak ozone formation 
from sunlight). Evening (after 7 PM) is also relatively cleaner than peak afternoon hours.

# Children's Safety

## Q: Should my child go to school when AQI is 300?
A: AQI 300 is 'Poor' under CPCB guidelines. The CPCB specifically recommends that children 
avoid all outdoor activities at this level. Schools should cancel outdoor PE and recess. 
If possible, children should travel to school with N95 masks. Parents of children with asthma 
or respiratory conditions should strongly consider keeping them home.

## Q: My 3-year-old plays outdoors. At what AQI should I stop?
A: Children under 5 are extremely vulnerable because their lungs are still developing. 
The WHO recommends restricting outdoor play above AQI 100. Above AQI 150, all outdoor 
play should be moved indoors. Air purifiers in the child's bedroom are highly recommended 
in cities where AQI frequently exceeds 100.

# Elderly and Heart Patients

## Q: My 70-year-old mother has heart disease. What AQI is safe for her outdoors?
A: For elderly individuals with cardiovascular disease, outdoor activity should be 
very limited even at moderate AQI (51–100). PM2.5 particles at concentrations above 
25 µg/m³ can trigger cardiac events in vulnerable individuals. Recommend staying 
indoors with HEPA air purification when AQI exceeds 50. Absolutely no outdoor activity 
above AQI 100.

## Q: Can air pollution cause a heart attack?
A: Yes. Multiple peer-reviewed studies confirm that acute exposure to high PM2.5 concentrations 
triggers inflammation, increases blood clotting tendency, and can cause cardiac arrhythmias. 
The Harvard Six Cities Study and multiple European cohort studies have established that 
long-term exposure to PM2.5 above 10 µg/m³ (annual average) significantly increases 
risk of cardiovascular mortality.

# Asthma & Respiratory Conditions

## Q: I have asthma. The AQI is 200 today. Can I go outside?
A: AQI 200 is at the 'Poor' category boundary. For asthma patients, this is a high-risk day. 
If going outside is unavoidable: wear a properly fitted N95 mask, carry your rescue inhaler, 
avoid areas near traffic or construction, and limit time outdoors to less than 20 minutes. 
Better to work/exercise from home on such days.

## Q: Which pollutant triggers asthma attacks most?
A: Ozone (O3) and PM2.5 are the primary triggers. Ozone causes direct airway inflammation 
and bronchospasm. NO2 makes airways hyper-responsive, amplifying reactions to allergens. 
SO2 causes rapid bronchoconstriction even at low concentrations. PM2.5 deposits deep in 
bronchioles and triggers immune responses.

# Protective Measures

## Q: Do N95 masks actually help against air pollution?
A: Yes, properly worn N95/FFP2 respirators filter ≥95% of airborne particles ≥0.3 µm, 
covering PM2.5 effectively. Key points:
1. Must have a proper seal — no facial hair at the seal line.
2. Surgical/cloth masks provide minimal protection against PM2.5 (only ~5–20% filtration).
3. Effectiveness degrades after 8–12 hours of use.
4. N99/FFP3 provides 99% filtration — preferred for very poor/severe AQI days.

## Q: Do air purifiers help indoors?
A: Yes, HEPA (High-Efficiency Particulate Air) purifiers rated for your room size 
can reduce indoor PM2.5 by 70–90%. Look for CADR (Clean Air Delivery Rate) ≥250 m³/hr 
for a standard bedroom. Run continuously during high-AQI days. Change filters every 6–12 months.
Activated carbon filters additionally remove NO2, SO2, and VOCs.

## Q: What plants help clean indoor air?
A: While NASA research (1989 Clean Air Study) showed certain houseplants remove VOCs, 
the effect is too small to meaningfully reduce PM2.5 at real-world concentrations. 
A HEPA air purifier is 1000x more effective than indoor plants for PM2.5 reduction. 
Plants are beneficial for psychological wellbeing but should not replace mechanical 
filtration in high-pollution environments.

# Pregnancy

## Q: I am pregnant. How dangerous is air pollution?
A: Air pollution during pregnancy is serious. Multiple studies show associations between 
PM2.5 exposure and:
- Low birth weight (17% increased risk above 10 µg/m³)
- Preterm birth
- Infant mortality
- Childhood asthma and developmental delays
Recommendations: Minimize outdoor time when AQI > 50. Use HEPA purifiers at home. 
Avoid commuting during peak traffic hours. Inform your obstetrician if you live near 
industrial areas or heavy traffic corridors.

# Delhi-Specific Context

## Q: Why is Delhi's air so bad in November?
A: Multiple factors converge in October–November in Delhi:
1. Stubble burning: Farmers in Punjab and Haryana burn rice crop residue (3–5 crore tonnes annually).
2. Diwali fireworks: Single-night PM2.5 spike of 300–500% above normal.
3. Weather inversion: Cold, stagnant air traps pollutants near the ground (the 'bowl effect').
4. Reduced wind speed: Monsoon withdrawal leaves no ventilation.
5. Wood burning: For heating as temperatures drop.
This combination can push Delhi AQI above 800–1000 on severe nights.

## Q: When is Mumbai's air quality best?
A: Mumbai's air quality is best during monsoon (June–September) when rain continuously 
washes the atmosphere and sea breezes provide ventilation. AQI typically stays in 
the Good-Satisfactory range (30–70) during these months. Post-monsoon (October–November) 
and winter (December–January) bring moderate pollution due to reduced ventilation and 
increased vehicle congestion.
"""

# ── Phase 6: verified static fallbacks (used when RAG confidence is low) ──────
AQI_CATEGORY_STATIC_FALLBACKS: dict[str, str] = {
    "Good": (
        "### 🌤️ Air Quality: Good (AQI 0–50)\n\n"
        "• **Outdoor Activities:** Safe and unrestricted. Ideal for outdoor workouts, running, cycling, and sports.\n"
        "• **Best Timing:** All times of day are suitable. Natural ventilation is encouraged.\n"
        "• **Sensitive Groups:** No special restrictions required (CPCB NAQI / WHO 2021)."
    ),
    "Satisfactory": (
        "### 🌤️ Air Quality: Satisfactory (AQI 51–100)\n\n"
        "• **Outdoor Activities:** Acceptable for most people. General population can carry on normal outdoor routines.\n"
        "• **Best Timing:** Afternoon hours (12 PM – 4 PM) typically feature better vertical atmospheric dispersion than early mornings.\n"
        "• **Sensitive Groups:** Unusually sensitive individuals (asthma, COPD) should monitor for minor throat irritation and avoid intense prolonged exertion (CPCB NAQI advisory)."
    ),
    "Moderate": (
        "### ⚠️ Air Quality: Moderate (AQI 101–200)\n\n"
        "• **Outdoor Activities:** Reduce prolonged or vigorous outdoor workouts (heavy cardio, marathon training).\n"
        "• **Best Timing:** Midday to early afternoon (1 PM – 4 PM) when atmospheric mixing is highest. Avoid peak morning rush hour (7 AM – 9 AM) and late evening.\n"
        "• **Sensitive Groups:** Children, seniors, and individuals with respiratory or heart conditions should limit outdoor time and keep quick-relief medication handy (CPCB NAQI)."
    ),
    "Poor": (
        "### 🚨 Air Quality: Poor (AQI 201–300)\n\n"
        "• **Outdoor Activities:** Significantly limit outdoor exposure. Avoid strenuous outdoor physical exertion.\n"
        "• **Best Timing:** If stepping outside is necessary, do so briefly during the warmest part of the afternoon. Wear a well-fitted N95/FFP2 respirator.\n"
        "• **Sensitive Groups:** Keep windows closed; run HEPA air purifiers indoors. Vulnerable individuals should remain indoors (CPCB NAQI / GRAP Stage 1)."
    ),
    "Very Poor": (
        "### 🛑 Air Quality: Very Poor (AQI 301–400)\n\n"
        "• **Outdoor Activities:** Strictly avoid all outdoor physical exercise and discretionary outdoor trips.\n"
        "• **Best Timing:** No outdoor time is recommended. High pollution persists throughout the day due to strong surface inversions.\n"
        "• **Sensitive Groups:** Must remain indoors with air filtration. N95 masks mandatory for unavoidable outdoor transit (CPCB NAQI / GRAP Stage 2)."
    ),
    "Severe": (
        "### ⛔ Air Quality: Severe (AQI 401+)\n\n"
        "• **Emergency Health Warning:** Seriously impacts both healthy individuals and those with pre-existing conditions.\n"
        "• **Outdoor Activities:** Absolute restriction on outdoor exposure. Keep indoor air sealed with active purification.\n"
        "• **Sensitive Groups:** Seek medical attention immediately if experiencing acute chest tightness, wheezing, or shortness of breath (CPCB NAQI Emergency Guidance)."
    ),
    "No Data": (
        "### ℹ️ Air Quality: Data Pending\n\n"
        "• **Precautionary Advice:** Verified station readings are temporarily updating. Sensitive groups should exercise caution and avoid heavy prolonged exertion until fresh telemetry is confirmed (WHO 2021 / CPCB NAQI)."
    ),
}


def get_static_fallback_for_aqi(
    aqi_value: float | None = None,
    city: str = "",
    category_label: str | None = None,
) -> str:
    """
    Return a verified CPCB/WHO-aligned static advisory when RAG confidence is low.
    Does not invent statistics — uses fixed category text from this module.
    """
    label = category_label
    if label is None:
        if aqi_value is None:
            label = "No Data"
        else:
            val = float(aqi_value)
            if val <= 50:
                label = "Good"
            elif val <= 100:
                label = "Satisfactory"
            elif val <= 200:
                label = "Moderate"
            elif val <= 300:
                label = "Poor"
            elif val <= 400:
                label = "Very Poor"
            else:
                label = "Severe"

    body = AQI_CATEGORY_STATIC_FALLBACKS.get(
        label, AQI_CATEGORY_STATIC_FALLBACKS["No Data"]
    )
    city_prefix = f"For **{city}**: " if city else ""
    aqi_prefix = (
        f"Current observed AQI ≈ **{float(aqi_value):.0f}**. "
        if aqi_value is not None
        else ""
    )
    return (
        "ℹ️ *Low retrieval confidence — showing verified CPCB/WHO category guidance "
        "instead of free-form AI extrapolation.*\n\n"
        f"{city_prefix}{aqi_prefix}{body}"
    )
