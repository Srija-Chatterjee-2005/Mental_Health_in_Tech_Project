"""Midnight Insight dashboard for the 2014 Mental Health in Tech survey."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from analysis_utils import clean_data, cramers_v, load_data, pct, treatment_rate_table

st.set_page_config(page_title="Mind at Work", layout="wide", initial_sidebar_state="expanded")

BG, SURFACE, BORDER = "#071426", "#0D2138", "#24405D"
TEXT, MUTED = "#F4F7FF", "#9DB0C7"
CYAN, MINT, VIOLET, BLUE = "#58D5F5", "#65E6B4", "#9B7BFF", "#5B8CFF"
COLORS = {"Yes": MINT, "No": "#5C7189", "Maybe": VIOLET, "Don't know": "#8DA1B8", "Not sure": "#8DA1B8"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root {{color-scheme:dark}} html,body,[class*="css"]{{font-family:Inter,sans-serif}}
.stApp{{background:radial-gradient(circle at 78% -10%,rgba(91,140,255,.17),transparent 31rem),radial-gradient(circle at 45% 105%,rgba(155,123,255,.1),transparent 34rem),{BG};color:{TEXT}}}
.block-container{{max-width:1480px;padding:1.35rem 2rem 2.5rem}} h1,h2,h3{{font-family:Manrope,sans-serif!important;letter-spacing:-.025em;color:{TEXT}!important}} p,label,.stCaption{{color:{MUTED}}}
#MainMenu,footer,header{{visibility:hidden}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,#091A30,#0B2037);border-right:1px solid {BORDER};min-width:310px}}
[data-testid="stSidebar"] .block-container{{padding:1.45rem 1.15rem 2rem}} [data-testid="stSidebar"] label{{color:#D8E4F3!important;font-weight:600;font-size:.84rem}}
.brand{{padding:.15rem 0 1rem;border-bottom:1px solid {BORDER};margin-bottom:1rem}} .brand-name{{font:800 1.65rem Manrope;color:{TEXT}}}.brand-line{{margin-top:.35rem;color:{MUTED};font-size:.72rem;letter-spacing:.1em;text-transform:uppercase}}
.filter-copy{{font-size:.82rem;color:{MUTED};line-height:1.5;margin-bottom:.45rem}}
div[data-baseweb="select"]>div,[data-testid="stFileUploaderDropzone"]{{background:#0B1D33!important;border:1px solid {BORDER}!important;color:{TEXT}!important;border-radius:10px!important}}
[data-testid="stFileUploaderDropzone"]{{padding:.8rem}} [data-testid="stFileUploaderDropzone"] small{{display:none}}
.stButton>button,.stDownloadButton>button{{width:100%;min-height:2.7rem;border-radius:10px;border:1px solid #41607F;background:#102842;color:{TEXT};font-weight:700;transition:.2s}}
.stButton>button:hover,.stDownloadButton>button:hover{{border-color:{CYAN};background:#163652;transform:translateY(-1px)}} [data-testid="stSidebar"] .stButton>button{{background:linear-gradient(90deg,{MINT},#4CD8CD);color:#062238;border:0}}
.hero{{display:flex;justify-content:space-between;gap:2rem;padding:.55rem 0 1.3rem;border-bottom:1px solid {BORDER};margin-bottom:1.15rem}}.eyebrow{{color:{CYAN};font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;font-weight:700}}.hero h1{{font-size:2.35rem;margin:.28rem 0 .4rem;line-height:1.07}}.hero p{{margin:0;max-width:700px;font-size:.97rem;line-height:1.55}}.hero-tag{{text-align:right;color:{MUTED};font-size:.73rem;letter-spacing:.12em;text-transform:uppercase;line-height:1.65}}
.metric-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.25rem}}.metric-card{{position:relative;overflow:hidden;min-height:128px;padding:1.1rem;background:linear-gradient(145deg,rgba(18,45,73,.96),rgba(11,30,52,.96));border:1px solid {BORDER};border-radius:14px}}.metric-card:after{{content:"";position:absolute;left:0;bottom:0;height:3px;width:100%;background:var(--accent)}}.metric-label{{color:#B6C7DA;font-size:.75rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase}}.metric-value{{font:800 2.05rem Manrope;color:var(--accent);margin:.58rem 0 .25rem}}.metric-note{{color:{MUTED};font-size:.77rem}}
.section-head h2{{font-size:1.28rem;margin:.7rem 0 0}}.section-head p{{margin:.3rem 0 .8rem;font-size:.86rem}}
[data-testid="stTabs"] [data-baseweb="tab-list"]{{gap:.35rem;border-bottom:1px solid {BORDER}}}[data-testid="stTabs"] button{{color:{MUTED};padding:.7rem 1rem;font-weight:650}}[data-testid="stTabs"] button[aria-selected="true"]{{color:{TEXT};background:rgba(88,213,245,.09)}}[data-testid="stTabs"] [data-baseweb="tab-highlight"]{{background:{CYAN}}}
[data-testid="stPlotlyChart"]{{background:rgba(12,32,55,.72);border:1px solid {BORDER};border-radius:14px;padding:.35rem}}[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden}}[data-testid="stAlert"]{{background:#0F2A42;border:1px solid #315879;color:{TEXT};border-radius:11px}}
.insight{{margin:.7rem 0 1.1rem;padding:1rem 1.1rem;border-left:3px solid {MINT};background:rgba(101,230,180,.065);border-radius:0 10px 10px 0;color:#C7D5E5;font-size:.88rem}}.footer-note{{border-top:1px solid {BORDER};margin-top:1.4rem;padding-top:1rem;color:#7890AA;font-size:.76rem}}
@media(max-width:1000px){{.metric-grid{{grid-template-columns:repeat(2,1fr)}}.hero-tag{{display:none}}}}@media(max-width:650px){{.block-container{{padding:1rem}}.metric-grid{{grid-template-columns:1fr}}.hero h1{{font-size:1.9rem}}}}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_default_data():
    return clean_data(load_data(Path(__file__).parent / "data" / "survey.csv"))

def reset_filters():
    for key in ("country_filter", "gender_filter", "company_filter", "age_filter"):
        st.session_state.pop(key, None)

def filter_data(df):
    st.sidebar.markdown("## Explore the data")
    st.sidebar.markdown('<div class="filter-copy">Refine the survey sample. Every metric and chart updates instantly.</div>', unsafe_allow_html=True)
    countries = st.sidebar.multiselect("Country", sorted(df.Country.dropna().unique()), key="country_filter")
    genders = st.sidebar.multiselect("Gender group", sorted(df.Gender_clean.unique()), key="gender_filter")
    order = ["1-5", "6-25", "26-100", "100-500", "500-1000", "More than 1000"]
    companies = st.sidebar.multiselect("Company size", [x for x in order if x in df.no_employees.unique()], key="company_filter")
    lo, hi = int(df.Age.min()), int(df.Age.max())
    ages = st.sidebar.slider("Age range", lo, hi, (lo, hi), key="age_filter")
    st.sidebar.button("Reset filters", on_click=reset_filters)
    out = df[df.Age.between(*ages) | df.Age.isna()]
    if countries: out = out[out.Country.isin(countries)]
    if genders: out = out[out.Gender_clean.isin(genders)]
    if companies: out = out[out.no_employees.isin(companies)]
    return out

def style_chart(fig, height=430):
    fig.update_layout(template="plotly_dark", height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter",color="#C7D5E5",size=12), title_font=dict(family="Manrope",color=TEXT,size=18), margin=dict(l=42,r=25,t=68,b=48), legend=dict(bgcolor="rgba(0,0,0,0)",title=""), hoverlabel=dict(bgcolor="#132B46",bordercolor="#3D5A77",font_color=TEXT))
    fig.update_xaxes(gridcolor="rgba(116,145,176,.14)",zeroline=False,linecolor="#2A4663")
    fig.update_yaxes(gridcolor="rgba(116,145,176,.14)",zeroline=False,linecolor="#2A4663")
    return fig

def response_bar(df, column, title):
    counts=df[column].value_counts(dropna=False).rename_axis("Response").reset_index(name="Count")
    fig=px.bar(counts,x="Response",y="Count",color="Response",title=title,color_discrete_map=COLORS,text_auto=True)
    fig.update_traces(marker_line_width=0,textposition="outside"); fig.update_layout(showlegend=False,xaxis_title=None)
    return style_chart(fig)

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-name">Mind at Work</div><div class="brand-line">People · Work · Better futures</div></div>',unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload a compatible CSV (optional)",type="csv")
    st.markdown('<div class="filter-copy">Your file remains within this active app session.</div>',unsafe_allow_html=True)

try: data=clean_data(load_data(uploaded)) if uploaded else get_default_data()
except Exception as exc: st.error(f"The file could not be loaded: {exc}"); st.stop()
filtered=filter_data(data)
if filtered.empty: st.warning("No responses match these filters. Reset or adjust the selections."); st.stop()

st.markdown('<section class="hero"><div><div class="eyebrow">2014 Mental Health in Tech Survey</div><h1>Workplace mental health, made visible.</h1><p>Explore how treatment seeking, work experiences, and employer support vary across the technology workforce.</p></div><div class="hero-tag">Explore<br>Understand<br>Improve</div></section>',unsafe_allow_html=True)
treat,family=pct(filtered.treatment),pct(filtered.family_history)
interference=100*filtered.work_interfere.isin(["Rarely","Sometimes","Often"]).mean(); support=filtered.support_index.mean()
st.markdown(f'''<section class="metric-grid">
<div class="metric-card" style="--accent:{VIOLET}"><div class="metric-label">Total respondents</div><div class="metric-value">{len(filtered):,}</div><div class="metric-note">Filtered survey sample</div></div>
<div class="metric-card" style="--accent:{CYAN}"><div class="metric-label">Sought treatment</div><div class="metric-value">{treat:.1f}%</div><div class="metric-note">Reported seeking treatment</div></div>
<div class="metric-card" style="--accent:{MINT}"><div class="metric-label">Work interference</div><div class="metric-value">{interference:.1f}%</div><div class="metric-note">Rarely, sometimes, or often</div></div>
<div class="metric-card" style="--accent:{BLUE}"><div class="metric-label">Support index</div><div class="metric-value">{support:.1f}</div><div class="metric-note">Descriptive score out of 100</div></div></section>''',unsafe_allow_html=True)

overview,demographics,workplace,drivers,data_tab=st.tabs(["Overview","Demographics","Workplace support","Treatment drivers","Data explorer"])
with overview:
    st.markdown('<div class="section-head"><h2>Survey overview</h2><p>The clearest signals in the current selection.</p></div>',unsafe_allow_html=True)
    a,b=st.columns([1.2,1])
    with a: st.plotly_chart(response_bar(filtered,"treatment","Treatment-seeking responses"),width="stretch")
    with b: st.plotly_chart(response_bar(filtered,"work_interfere","Mental health interference at work"),width="stretch")
    st.markdown(f'<div class="insight"><strong>{family:.1f}%</strong> of the selected respondents report a family history of mental illness. Explore the Treatment Drivers tab for association strength.</div>',unsafe_allow_html=True)
    country=treatment_rate_table(filtered,"Country",10).head(15)
    fig=px.bar(country.sort_values("treatment_rate"),x="treatment_rate",y="Country",orientation="h",color="treatment_rate",color_continuous_scale=["#273A70",VIOLET,MINT],hover_data=["responses"],title="Treatment-seeking rate by country")
    fig.update_layout(xaxis_title="Treatment-seeking rate (%)",yaxis_title=None,coloraxis_showscale=False); st.plotly_chart(style_chart(fig,520),width="stretch")
with demographics:
    st.markdown('<div class="section-head"><h2>Who responded</h2><p>Age, gender-group, and geographic composition.</p></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        fig=px.histogram(filtered,x="Age",nbins=25,color="treatment",barmode="overlay",color_discrete_map=COLORS,title="Age distribution by treatment seeking"); st.plotly_chart(style_chart(fig),width="stretch")
    with b:
        gender=treatment_rate_table(filtered,"Gender_clean",1); fig=px.bar(gender,x="Gender_clean",y="treatment_rate",color="Gender_clean",color_discrete_sequence=[CYAN,VIOLET,MINT],text_auto=".1f",hover_data=["responses"],title="Treatment-seeking rate by gender group"); fig.update_layout(showlegend=False,yaxis_title="Rate (%)",xaxis_title=None); st.plotly_chart(style_chart(fig),width="stretch")
    fig=px.sunburst(filtered,path=["Country","Gender_clean"],maxdepth=2,color_discrete_sequence=[CYAN,VIOLET,MINT,BLUE],title="Respondent composition by country and gender group"); st.plotly_chart(style_chart(fig,560),width="stretch")
with workplace:
    st.markdown('<div class="section-head"><h2>Workplace support</h2><p>Policies, access, and psychological safety.</p></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        fig=px.histogram(filtered,x="support_index",color="treatment",nbins=20,color_discrete_map=COLORS,barmode="overlay",title="Distribution of workplace support index"); st.plotly_chart(style_chart(fig),width="stretch")
    with b:
        company=filtered.groupby("no_employees",observed=True).support_index.mean().reset_index(); fig=px.bar(company,x="no_employees",y="support_index",color="support_index",color_continuous_scale=["#223B66",CYAN,MINT],title="Average support index by company size"); fig.update_layout(coloraxis_showscale=False,xaxis_title="Employees",yaxis_title="Mean index"); st.plotly_chart(style_chart(fig),width="stretch")
    dims=["benefits","care_options","wellness_program","seek_help","anonymity","mental_vs_physical"]
    long=filtered[dims].melt(var_name="Measure",value_name="Response"); shares=long.groupby(["Measure","Response"]).size().reset_index(name="Count"); shares["Percent"]=shares.groupby("Measure").Count.transform(lambda s:s/s.sum()*100)
    fig=px.bar(shares,x="Percent",y="Measure",color="Response",orientation="h",color_discrete_map=COLORS,title="Employer support responses",barmode="stack"); st.plotly_chart(style_chart(fig,500),width="stretch")
    st.info("The support index combines 11 workplace-policy and psychological-safety questions. It is descriptive, not clinical.")
with drivers:
    st.markdown('<div class="section-head"><h2>Treatment drivers</h2><p>Association strength across categorical survey factors.</p></div>',unsafe_allow_html=True)
    variables=["family_history","work_interfere","benefits","care_options","leave","mental_health_consequence","coworkers","supervisor","remote_work","tech_company","no_employees","Gender_clean","age_group"]
    associations=pd.DataFrame({"Variable":variables,"Cramer's V":[cramers_v(filtered[v],filtered.treatment) for v in variables]}).sort_values("Cramer's V")
    fig=px.bar(associations,x="Cramer's V",y="Variable",orientation="h",color="Cramer's V",color_continuous_scale=["#283B68",VIOLET,MINT],title="Association with treatment seeking (Cramér’s V)"); fig.update_layout(coloraxis_showscale=False); st.plotly_chart(style_chart(fig,540),width="stretch")
    selected=st.selectbox("Compare treatment rate by",variables,index=0); table=treatment_rate_table(filtered,selected,3)
    fig=px.bar(table,x=selected,y="treatment_rate",color="treatment_rate",color_continuous_scale=["#273A70",CYAN,MINT],text_auto=".1f",hover_data=["responses"],title=f"Treatment-seeking rate by {selected.replace('_',' ')}"); fig.update_layout(coloraxis_showscale=False,yaxis_title="Treatment-seeking rate (%)"); st.plotly_chart(style_chart(fig),width="stretch")
    st.caption("Association does not imply causation. Responses are observational and self-reported.")
with data_tab:
    st.markdown('<div class="section-head"><h2>Data explorer</h2><p>Inspect and export the current filtered sample.</p></div>',unsafe_allow_html=True)
    visible=st.multiselect("Columns",filtered.columns.tolist(),default=["Age","Gender_clean","Country","treatment","work_interfere","support_index"])
    st.dataframe(filtered[visible] if visible else filtered,width="stretch",hide_index=True,height=480)
    st.download_button("Download filtered data",filtered.to_csv(index=False).encode(),"mental_health_tech_filtered.csv","text/csv")
st.markdown('<div class="footer-note">OSMI Mental Health in Tech Survey (2014). Results describe this self-reported sample only. The Workplace Support Index is an analytical aid and must not be used for diagnosis.</div>',unsafe_allow_html=True)
