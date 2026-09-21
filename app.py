Here is the complete fix! The issue was caused by light-gray text colors blending into the bright white background. 

I have updated the colors to **high-contrast dark slate (`#0F172A` and `#1E293B`)** with bold, crisp text, so every metric, chart, label, and alert is crystal clear and easy to read.

---

### 🛠️ How to apply the fix (1 Minute):

1. Go to your GitHub repository: `github.com/YOUR_USERNAME/aerotwin-dashboard`
2. Click on **`app.py`**
3. Click the **Pencil icon** (✏️) in the top-right to edit.
4. **Select all (`Ctrl + A` or `Cmd + A`) and delete everything.**
5. **Copy and paste the entire updated code below.**
6. Click **"Commit changes..."** ➔ **"Commit changes"**.
7. Streamlit Cloud will auto-refresh in ~10 seconds with dark, crisp, readable fonts! 🚀

---

### 👇 Copy ALL of this updated code for `app.py`:

```python
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List
from enum import Enum
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AeroTwin – Digital Twin Dashboard",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# HIGH CONTRAST EYE-SOOTHING CLEAN THEME CSS
# ============================================================
st.markdown("""
<style>
    /* Main Background */
    .stApp { 
        background-color: #F8FAFC !important; 
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Text & Headings */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #0F172A !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #E2E8F0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: #FFFFFF !important; 
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important; 
        padding: 14px 18px !important;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.05) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #475569 !important; 
        font-size: 0.85rem !important;
        font-weight: 700 !important; 
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] div { 
        color: #0F172A !important; 
        font-weight: 800 !important; 
        font-size: 1.7rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; 
        background: #FFFFFF; 
        border-radius: 12px;
        padding: 6px; 
        border: 1.5px solid #CBD5E1;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; 
        padding: 8px 20px; 
        color: #334155 !important; 
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #4338CA !important; 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #FFFFFF !important;
    }

    /* Cards */
    .health-card {
        background: #FFFFFF !important; 
        border-radius: 16px !important; 
        padding: 22px !important;
        border: 1.5px solid #CBD5E1 !important; 
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06) !important;
        text-align: center !important; 
        margin-bottom: 16px !important;
    }
    .health-card h2 { 
        margin: 0 !important; 
        font-size: 2.8rem !important; 
        font-weight: 900 !important; 
    }
    .health-card p { 
        color: #475569 !important; 
        font-weight: 700 !important;
        margin: 4px 0 0 0 !important; 
        font-size: 0.95rem !important; 
    }

    .info-box {
        background: #FFFFFF !important; 
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 14px !important; 
        padding: 20px !important; 
        margin-bottom: 16px !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
    }
    .info-box p, .info-box li, .info-box strong {
        color: #1E293B !important;
    }

    .section-header {
        color: #0F172A !important; 
        font-size: 1.15rem !important; 
        font-weight: 800 !important;
        margin-bottom: 14px !important; 
        padding-bottom: 8px !important; 
        border-bottom: 2px solid #E2E8F0 !important;
    }

    /* Alerts with High Contrast Text */
    .alert-card {
        border-radius: 10px !important; 
        padding: 14px 18px !important; 
        margin-bottom: 12px !important; 
        border-left: 6px solid !important;
        font-weight: 500 !important;
    }
    .alert-green { 
        background: #ECFDF5 !important; 
        border-color: #059669 !important; 
        color: #064E3B !important; 
    }
    .alert-green * { color: #064E3B !important; }

    .alert-yellow { 
        background: #FEFCE8 !important; 
        border-color: #D97706 !important; 
        color: #78350F !important; 
    }
    .alert-yellow * { color: #78350F !important; }

    .alert-orange { 
        background: #FFF7ED !important; 
        border-color: #EA580C !important; 
        color: #7C2D12 !important; 
    }
    .alert-orange * { color: #7C2D12 !important; }

    .alert-red { 
        background: #FEF2F2 !important; 
        border-color: #DC2626 !important; 
        color: #7F1D1D !important; 
    }
    .alert-red * { color: #7F1D1D !important; }

    .alert-blue { 
        background: #EFF6FF !important; 
        border-color: #2563EB !important; 
        color: #1E3A8A !important; 
    }
    .alert-blue * { color: #1E3A8A !important; }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DOMAIN MODELS & ENUMS
# ============================================================
class FaultType(Enum):
    HEALTHY = "Healthy (Nominal Operation)"
    INJECTOR_DEGRADATION = "Injector Degradation"
    MISFIRE = "Cylinder Misfire"
    OVERHEATING = "Thermal Overheating"
    LUBRICATION_PROBLEM = "Lubrication Failure"
    SENSOR_DRIFT = "Sensor Drift Anomaly"
    ABNORMAL_VIBRATION = "Mechanical Vibration Spike"

@dataclass
class EngineState:
    timestamp: datetime = None
    rpm: float = 0.0
    cht: List[float] = field(default_factory=lambda: [0.0]*4)
    egt: List[float] = field(default_factory=lambda: [0.0]*4)
    oil_pressure: float = 0.0
    oil_temperature: float = 0.0
    fuel_flow: float = 0.0
    vibration: float = 0.0
    battery_voltage: float = 0.0
    injection_timing: List[float] = field(default_factory=lambda: [0.0]*4)
    altitude: float = 0.0
    oat: float = 0.0
    throttle: float = 0.0
    airspeed: float = 0.0
    engine_hours: float = 0.0

# ============================================================
# PHYSICS & DIGITAL TWIN LOGIC
# ============================================================
class PhysicsModel:
    def __init__(self):
        self.base = {
            'rpm': 2400, 'cht': 180.0, 'egt': 720.0,
            'oil_p': 65.0, 'oil_t': 95.0, 'fuel': 38.0,
            'vib': 0.15, 'bat': 28.0,
        }

    def expected(self, throttle, altitude, oat):
        tf = throttle / 75.0
        af = 1.0 - (altitude / 50000.0) * 0.15
        tempf = 1.0 + (oat - 15.0) / 200.0
        return {
            'rpm': self.base['rpm'] * tf,
            'cht': [self.base['cht'] * tf * tempf * af + np.random.normal(0, 1) for _ in range(4)],
            'egt': [self.base['egt'] * tf * tempf * af + np.random.normal(0, 2) for _ in range(4)],
            'oil_p': self.base['oil_p'] * af + np.random.normal(0, 0.3),
            'oil_t': self.base['oil_t'] * tf * tempf + np.random.normal(0, 0.5),
            'fuel': self.base['fuel'] * tf + np.random.normal(0, 0.2),
            'vib': self.base['vib'] * (0.8 + 0.4 * tf) + np.random.normal(0, 0.005),
            'bat': self.base['bat'] + np.random.normal(0, 0.1),
        }

class EngineSimulator:
    def __init__(self):
        self.physics = PhysicsModel()
        self.fault_type = FaultType.HEALTHY
        self.fault_severity = 0.0
        self.fault_cylinder = 1
        self.engine_hours = 342.5

    def set_fault(self, ft, sev=0.3, cyl=2):
        self.fault_type = ft
        self.fault_severity = np.clip(sev, 0, 1)
        self.fault_cylinder = cyl - 1

    def generate(self, throttle=70, altitude=15000, oat=-5, airspeed=120, t_off=0):
        exp = self.physics.expected(throttle, altitude, oat)
        s = EngineState()
        s.timestamp = datetime.now() + timedelta(seconds=t_off)
        s.rpm = exp['rpm'] + np.random.normal(0, 5)
        s.cht = [v + np.random.normal(0, 2) for v in exp['cht']]
        s.egt = [v + np.random.normal(0, 3) for v in exp['egt']]
        s.oil_pressure = exp['oil_p']
        s.oil_temperature = exp['oil_t']
        s.fuel_flow = exp['fuel']
        s.vibration = exp['vib']
        s.battery_voltage = exp['bat']
        s.injection_timing = [12.5 + np.random.normal(0, 0.1) for _ in range(4)]
        s.altitude, s.oat, s.throttle, s.airspeed = altitude, oat, throttle, airspeed
        s.engine_hours = self.engine_hours + t_off / 3600.0

        sv, c = self.fault_severity, self.fault_cylinder
        if self.fault_type == FaultType.INJECTOR_DEGRADATION:
            s.egt[c] += 55*sv + np.random.normal(0,3); s.fuel_flow += 4.5*sv
            s.cht[c] += 15*sv; s.vibration += 0.08*sv; s.rpm -= 30*sv
        elif self.fault_type == FaultType.MISFIRE:
            s.egt[c] -= 80*sv; s.cht[c] -= 25*sv; s.rpm -= 60*sv; s.vibration += 0.25*sv
        elif self.fault_type == FaultType.OVERHEATING:
            for i in range(4): s.cht[i] += 45*sv; s.egt[i] += 60*sv
            s.oil_temperature += 25*sv
        elif self.fault_type == FaultType.LUBRICATION_PROBLEM:
            s.oil_pressure -= 20*sv; s.oil_temperature += 30*sv; s.vibration += 0.12*sv
        elif self.fault_type == FaultType.SENSOR_DRIFT:
            s.egt[c] += 200*sv*np.random.choice([1,-1])
        elif self.fault_type == FaultType.ABNORMAL_VIBRATION:
            s.vibration += 0.4*sv
        return s

    def generate_history(self, dur_min=120, rate=10, fault_pct=0.6):
        n = (dur_min * 60) // rate
        fs = int(n * fault_pct)
        records = []
        for i in range(n):
            t = i * rate
            if t < 300: thr, alt = 90-(t/300)*15, (t/300)*5000
            elif t < 600: thr, alt = 80-((t-300)/300)*10, 5000+((t-300)/300)*10000
            elif t < dur_min*60-600: thr, alt = 70+np.random.normal(0,1), 15000+np.random.normal(0,100)
            elif t < dur_min*60-300:
                p = (t-(dur_min*60-600))/300; thr, alt = 70-p*30, 15000-p*10000
            else:
                p = (t-(dur_min*60-300))/300; thr, alt = max(40-p*15,25), max(5000-p*5000,0)
            if i >= fs and self.fault_type != FaultType.HEALTHY:
                self.fault_severity = min(((i-fs)/(n-fs))*0.8, 0.8)
            else:
                self.fault_severity = 0.0
            st = self.generate(throttle=thr, altitude=alt, oat=-5+alt*(-0.002), airspeed=120+(thr-70)*2, t_off=t)
            records.append({
                'time_sec': t, 'rpm': st.rpm,
                'cht_1': st.cht[0], 'cht_2': st.cht[1], 'cht_3': st.cht[2], 'cht_4': st.cht[3],
                'egt_1': st.egt[0], 'egt_2': st.egt[1], 'egt_3': st.egt[2], 'egt_4': st.egt[3],
                'oil_pressure': st.oil_pressure, 'oil_temperature': st.oil_temperature,
                'fuel_flow': st.fuel_flow, 'vibration': st.vibration,
                'altitude': st.altitude, 'fault_severity': self.fault_severity,
            })
        return pd.DataFrame(records)

class AIEngine:
    def __init__(self):
        self.physics = PhysicsModel()
        self.threshold = 0.15

    def residuals(self, s):
        e = self.physics.expected(s.throttle, s.altitude, s.oat)
        r = {
            'rpm': abs(s.rpm-e['rpm'])/max(e['rpm'],1),
            'egt_max': max(abs(s.egt[i]-e['egt'][i])/max(abs(e['egt'][i]),1) for i in range(4)),
            'cht_max': max(abs(s.cht[i]-e['cht'][i])/max(abs(e['cht'][i]),1) for i in range(4)),
            'oil_pressure': abs(s.oil_pressure-e['oil_p'])/max(abs(e['oil_p']),1),
            'oil_temperature': abs(s.oil_temperature-e['oil_t'])/max(abs(e['oil_t']),1),
            'fuel_flow': abs(s.fuel_flow-e['fuel'])/max(abs(e['fuel']),1),
            'vibration': abs(s.vibration-e['vib'])/max(abs(e['vib']),0.01),
        }
        for i in range(4):
            r[f'egt_cyl_{i+1}'] = abs(s.egt[i]-e['egt'][i])/max(abs(e['egt'][i]),1)
            r[f'cht_cyl_{i+1}'] = abs(s.cht[i]-e['cht'][i])/max(abs(e['cht'][i]),1)
        return r

    def classify(self, r):
        scores = {ft: 0.0 for ft in FaultType}
        evidence = {}
        for i in range(4):
            er = r.get(f'egt_cyl_{i+1}',0)
            if er > 0.05:
                scores[FaultType.INJECTOR_DEGRADATION] += er*3
                evidence[f'EGT Cyl {i+1}'] = f"+{er*100:.1f}%"
        if r.get('fuel_flow',0) > 0.05:
            scores[FaultType.INJECTOR_DEGRADATION] += r['fuel_flow']*2
            evidence['Fuel flow'] = f"+{r['fuel_flow']*100:.1f}%"
        if r.get('rpm',0) > 0.02: scores[FaultType.MISFIRE] += r['rpm']*3
        if r.get('vibration',0) > 0.3: scores[FaultType.MISFIRE] += r['vibration']*2
        if r.get('cht_max',0) > 0.1: scores[FaultType.OVERHEATING] += r['cht_max']*3
        if r.get('oil_pressure',0) > 0.1: scores[FaultType.LUBRICATION_PROBLEM] += r['oil_pressure']*4
        if max(r.get(f'egt_cyl_{i+1}',0) for i in range(4)) > 0.2: scores[FaultType.SENSOR_DRIFT] += 2.5
        if r.get('vibration',0) > 0.5: scores[FaultType.ABNORMAL_VIBRATION] += r['vibration']*3
        
        tot = sum(r.get(k,0) for k in ['rpm','egt_max','cht_max','oil_pressure','oil_temperature','fuel_flow','vibration'])
        if tot < 0.25: scores[FaultType.HEALTHY] = 2.0
        total = sum(scores.values())
        if total > 0:
            for k in scores: scores[k] /= total
        best = max(scores, key=scores.get)
        return best, scores[best], evidence

    def health(self, r):
        p = r.get('egt_max',0)*25 + r.get('cht_max',0)*20 + r.get('oil_pressure',0)*20 + r.get('vibration',0)*15 + r.get('fuel_flow',0)*10 + r.get('rpm',0)*10
        return round(max(0, min(100, 100-p)), 1)

    def rul(self, h, dr=0.5):
        if dr <= 0.01: return 200.0, 250.0
        rem = h - 60.0
        if rem <= 0: return 0.0, 0.0
        return round(rem/(dr*1.3),1), round(rem/(dr*0.7),1)

    def mission_risk(self, h, rl, mhrs):
        if h >= 90 and rl > mhrs*2: return "LOW"
        elif h >= 75 and rl > mhrs: return "MEDIUM"
        elif h >= 60: return "HIGH"
        else: return "CRITICAL"

# ============================================================
# HIGH CONTRAST CHARTS
# ============================================================
def gauge(val, title):
    c = "#059669" if val>=90 else "#D97706" if val>=75 else "#EA580C" if val>=60 else "#DC2626"
    fig = go.Figure(go.Indicator(
        mode="gauge+number", 
        value=val,
        title={'text': title, 'font': {'size': 16, 'color': '#0F172A', 'weight': 700}},
        number={'font': {'size': 34, 'color': '#0F172A', 'weight': 800}},
        gauge={
            'axis': {'range': [0,100], 'tickcolor': '#334155', 'tickfont': {'color': '#0F172A', 'size': 11}},
            'bar': {'color': c, 'thickness': 0.35},
            'bgcolor': '#F1F5F9',
            'steps': [
                {'range': [0,60], 'color': '#FEE2E2'},
                {'range': [60,75], 'color': '#FFEDD5'},
                {'range': [75,90], 'color': '#FEF9C3'},
                {'range': [90,100], 'color': '#DCFCE7'}
            ]
        }
    ))
    fig.update_layout(height=190, margin=dict(l=15,r=15,t=35,b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig

def cyl_chart(cht, egt):
    cys = ['Cyl 1','Cyl 2','Cyl 3','Cyl 4']
    fig = make_subplots(rows=1,cols=2,subplot_titles=('<b>CHT (°C)</b>','<b>EGT (°C)</b>'),horizontal_spacing=0.12)
    cc = ['#DC2626' if v>220 else '#EA580C' if v>200 else '#4F46E5' for v in cht]
    ec = ['#DC2626' if v>800 else '#EA580C' if v>760 else '#7C3AED' for v in egt]
    fig.add_trace(go.Bar(x=cys,y=cht,marker_color=cc,text=[f'<b>{v:.0f}°</b>' for v in cht],textposition='outside'),1,1)
    fig.add_trace(go.Bar(x=cys,y=egt,marker_color=ec,text=[f'<b>{v:.0f}°</b>' for v in egt],textposition='outside'),1,2)
    fig.update_layout(
        height=260, showlegend=False, margin=dict(l=10,r=10,t=35,b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#0F172A', 'size': 12}
    )
    fig.update_xaxes(showgrid=False, linecolor='#94A3B8', tickfont={'color':'#0F172A', 'size':11, 'weight':600})
    fig.update_yaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#94A3B8', tickfont={'color':'#0F172A', 'size':11})
    return fig

def ts_chart(df, cols, title, yl=""):
    fig = go.Figure()
    colors = ['#4F46E5','#059669','#DC2626','#EA580C','#7C3AED','#0284C7']
    for i,c in enumerate(cols):
        fig.add_trace(go.Scatter(x=df['time_sec']/60,y=df[c],name=f"<b>{c.replace('_',' ').title()}</b>",
            line=dict(color=colors[i%len(colors)],width=2.5),mode='lines'))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",font=dict(size=14,color='#0F172A')),
        height=290, margin=dict(l=10,r=10,t=35,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#0F172A','size':11},
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,font=dict(size=11,color='#0F172A')),
        xaxis_title="Time (min)", yaxis_title=yl
    )
    fig.update_xaxes(showgrid=True,gridcolor='#E2E8F0',linecolor='#94A3B8',tickfont={'color':'#0F172A'})
    fig.update_yaxes(showgrid=True,gridcolor='#E2E8F0',linecolor='#94A3B8',tickfont={'color':'#0F172A'})
    return fig

def res_chart(r):
    keys = ['rpm','egt_max','cht_max','oil_pressure','oil_temperature','fuel_flow','vibration']
    labels = ['RPM','EGT','CHT','Oil P','Oil T','Fuel','Vib']
    vals = [r.get(k,0)*100 for k in keys]
    colors = ['#DC2626' if v>15 else '#EA580C' if v>8 else '#D97706' if v>4 else '#059669' for v in vals]
    fig = go.Figure(go.Bar(x=labels,y=vals,marker_color=colors,text=[f'<b>{v:.1f}%</b>' for v in vals],textposition='outside'))
    fig.add_hline(y=15,line_dash="dash",line_color="#DC2626",annotation_text="Critical (15%)",annotation_font_color="#DC2626")
    fig.update_layout(
        title=dict(text="<b>Residual Error (% Deviation from Twin)</b>",font=dict(size=14,color='#0F172A')),
        yaxis_title="Deviation (%)",height=260,margin=dict(l=10,r=10,t=35,b=10),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#0F172A','size':11}
    )
    fig.update_xaxes(showgrid=False,linecolor='#94A3B8',tickfont={'color':'#0F172A','weight':600})
    fig.update_yaxes(showgrid=True,gridcolor='#E2E8F0',linecolor='#94A3B8',tickfont={'color':'#0F172A'})
    return fig

def radar_chart(s, e):
    params = ['RPM','CHT Avg','EGT Avg','Oil Press','Oil Temp','Fuel Flow']
    av = [s.rpm, np.mean(s.cht), np.mean(s.egt), s.oil_pressure, s.oil_temperature, s.fuel_flow]
    ev = [e['rpm'], np.mean(e['cht']), np.mean(e['egt']), e['oil_p'], e['oil_t'], e['fuel']]
    mx = [max(a,b,1) for a,b in zip(av,ev)]
    an = [a/m*100 for a,m in zip(av,mx)]
    en = [b/m*100 for b,m in zip(ev,mx)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=en+[en[0]],theta=params+[params[0]],fill='toself',
        fillcolor='rgba(79, 70, 229, 0.15)',line=dict(color='#4F46E5',width=2.5),name='Physics Twin'))
    fig.add_trace(go.Scatterpolar(r=an+[an[0]],theta=params+[params[0]],fill='toself',
        fillcolor='rgba(220, 38, 38, 0.15)',line=dict(color='#DC2626',width=2.5),name='Actual Engine'))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True,range=[0,120],showticklabels=False,gridcolor='#CBD5E1'),
            angularaxis=dict(tickfont=dict(size=11,color='#0F172A',weight=600),gridcolor='#CBD5E1'),
            bgcolor='rgba(0,0,0,0)'
        ),
        height=310,margin=dict(l=35,r=35,t=20,b=20),paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h',yanchor='bottom',y=-0.15,xanchor='center',x=0.5,font=dict(color='#0F172A',weight=600))
    )
    return fig

# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    with st.sidebar:
        st.markdown("## 🚁 AeroTwin Core")
        st.markdown('<p style="color:#334155;font-weight:600;font-size:0.9rem;">Digital Twin Engine Health Monitor<br>DRDO / SIH 2026 – PS-8</p>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('#### ⚙️ Fault Injection')

        fault_map = {
            "🟢 Healthy": FaultType.HEALTHY, 
            "🟡 Injector Degradation": FaultType.INJECTOR_DEGRADATION,
            "🟠 Cylinder Misfire": FaultType.MISFIRE, 
            "🔴 Thermal Overheating": FaultType.OVERHEATING,
            "🔴 Lubrication Problem": FaultType.LUBRICATION_PROBLEM,
            "🔵 Sensor Drift": FaultType.SENSOR_DRIFT, 
            "🟣 Abnormal Vibration": FaultType.ABNORMAL_VIBRATION,
        }
        sel = st.selectbox("Select Scenario", list(fault_map.keys()), index=1)
        ft = fault_map[sel]
        sev = st.slider("Fault Severity", 0.0, 1.0, 0.45, 0.05)
        cyl = st.selectbox("Target Cylinder", [1,2,3,4], index=1)
        
        st.markdown("---")
        st.markdown('#### 🛫 Flight Parameters')
        thr = st.slider("Throttle Level (%)", 30, 100, 70)
        alt = st.slider("Altitude (ft)", 0, 30000, 15000, 1000)
        mhrs = st.slider("Mission Time Remaining (hrs)", 0.5, 8.0, 3.0, 0.5)

    sim = EngineSimulator(); sim.set_fault(ft, sev, cyl)
    ai = AIEngine(); oat = 15 - alt*0.002
    state = sim.generate(throttle=thr, altitude=alt, oat=oat, airspeed=120+(thr-70)*2)
    phys = PhysicsModel(); exp = phys.expected(thr, alt, oat)
    res = ai.residuals(state)
    fault, conf, evidence = ai.classify(res)
    health = ai.health(res)
    rl, rh = ai.rul(health, sev*2)
    mrisk = ai.mission_risk(health, rl, mhrs)

    sh = EngineSimulator(); sh.set_fault(ft, sev, cyl)
    hdf = sh.generate_history(120, 10)
    hh = []
    for _, row in hdf.iterrows():
        ts = EngineState(); ts.rpm=row['rpm']
        ts.cht=[row['cht_1'],row['cht_2'],row['cht_3'],row['cht_4']]
        ts.egt=[row['egt_1'],row['egt_2'],row['egt_3'],row['egt_4']]
        ts.oil_pressure=row['oil_pressure']; ts.oil_temperature=row['oil_temperature']
        ts.fuel_flow=row['fuel_flow']; ts.vibration=row['vibration']
        ts.altitude=row['altitude']; ts.throttle=70; ts.oat=-5+row['altitude']*(-0.002)
        hh.append(ai.health(ai.residuals(ts)))
    hdf['health'] = hh

    # Main Dashboard Header
    st.markdown('<div style="text-align:center;padding:5px 0 15px 0;">'
        '<h1 style="color:#0F172A;font-weight:900;font-size:2rem;margin-bottom:2px;">🚁 Aero Piston Engine Digital Twin</h1>'
        '<p style="color:#334155;font-weight:600;font-size:1rem;">Real-Time Health Monitoring • Physics Residuals • AI Diagnostics</p></div>',
        unsafe_allow_html=True)

    # Status Bar
    rc = {'LOW':'#059669','MEDIUM':'#D97706','HIGH':'#EA580C','CRITICAL':'#DC2626'}
    rb = {'LOW':'#ECFDF5','MEDIUM':'#FEFCE8','HIGH':'#FFF7ED','CRITICAL':'#FEF2F2'}
    re = {'LOW':'🟢','MEDIUM':'🟡','HIGH':'🟠','CRITICAL':'🔴'}
    
    st.markdown(f'<div style="background:{rb[mrisk]};border:2px solid {rc[mrisk]};border-radius:12px;'
        f'padding:12px 20px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">'
        f'<span style="font-weight:800;color:{rc[mrisk]};font-size:1.05rem;">{re[mrisk]} Mission Risk: {mrisk}</span>'
        f'<span style="color:#0F172A;font-weight:600;font-size:0.95rem;">Health: <b>{health}%</b> &nbsp;|&nbsp; Diagnostic: <b>{fault.value}</b> &nbsp;|&nbsp; '
        f'AI Confidence: <b>{conf*100:.0f}%</b> &nbsp;|&nbsp; RUL: <b>{rl}-{rh}h</b> &nbsp;|&nbsp; Alt: <b>{alt:,}ft</b></span></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["👨‍✈️ Pilot View","👨‍🔧 Engineer View","🧬 Digital Twin","🛫 Mission Risk","🔁 Replay"])

    # 👨‍✈️ PILOT TAB
    with t1:
        c1,c2,c3 = st.columns([1.2,1,1])
        with c1:
            hc = '#059669' if health>=90 else '#D97706' if health>=75 else '#EA580C' if health>=60 else '#DC2626'
            st.markdown(f'<div class="health-card"><p>OVERALL ENGINE HEALTH</p><h2 style="color:{hc};">{health}%</h2>'
                f'<p>Engine Accumulated Time: <b>{state.engine_hours:.1f} hrs</b></p></div>', unsafe_allow_html=True)
            st.plotly_chart(gauge(health,"Health Score"), use_container_width=True)
        with c2:
            st.markdown('<div class="info-box"><p class="section-header">⚠️ Warning & Diagnostics</p>', unsafe_allow_html=True)
            if fault == FaultType.HEALTHY:
                st.markdown('<div class="alert-card alert-green">✅ <b>All Engine Parameters Nominal</b><br>No corrective action required.</div>', unsafe_allow_html=True)
            else:
                ac = 'alert-red' if mrisk=='CRITICAL' else 'alert-orange' if mrisk=='HIGH' else 'alert-yellow'
                st.markdown(f'<div class="alert-card {ac}"><strong>⚠️ {fault.value}</strong><br>'
                    f'📍 Target Subsystem: <b>Cylinder {cyl}</b><br>🤖 AI Confidence: <b>{conf*100:.0f}%</b><br>⏳ Estimated RUL: <b>{rl}-{rh} operating hrs</b></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="info-box"><p class="section-header">📋 Pilot Quick Gauges</p>', unsafe_allow_html=True)
            st.metric("Engine RPM", f"{state.rpm:.0f} RPM")
            st.metric("Fuel Flow", f"{state.fuel_flow:.1f} L/h")
            st.metric("Vibration Level", f"{state.vibration:.3f} g")
            st.metric("Flight Altitude", f"{alt:,} ft")
            st.markdown('</div>', unsafe_allow_html=True)

    # 👨‍🔧 ENGINEER TAB
    with t2:
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("RPM", f"{state.rpm:.0f}", f"{state.rpm-exp['rpm']:+.0f}")
        m2.metric("Oil Press", f"{state.oil_pressure:.1f} psi", f"{state.oil_pressure-exp['oil_p']:+.1f}")
        m3.metric("Oil Temp", f"{state.oil_temperature:.1f}°C", f"{state.oil_temperature-exp['oil_t']:+.1f}")
        m4.metric("Fuel Flow", f"{state.fuel_flow:.1f} L/h", f"{state.fuel_flow-exp['fuel']:+.1f}")
        m5.metric("Vibration", f"{state.vibration:.3f} g", f"{state.vibration-exp['vib']:+.3f}")
        m6.metric("Battery", f"{state.battery_voltage:.1f} V")

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<div class="info-box"><p class="section-header">🔥 Cylinder Head (CHT) & Exhaust (EGT) Temps</p>', unsafe_allow_html=True)
            st.plotly_chart(cyl_chart(state.cht, state.egt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cc2:
            st.markdown('<div class="info-box"><p class="section-header">📐 Physics Model Residuals (Actual vs Expected)</p>', unsafe_allow_html=True)
            st.plotly_chart(res_chart(res), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.plotly_chart(ts_chart(hdf,['egt_1','egt_2','egt_3','egt_4'],'Exhaust Gas Temperatures (EGT) by Cylinder','°C'), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with tc2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.plotly_chart(ts_chart(hdf,['oil_pressure','oil_temperature'],'Lubrication System Dynamics','Value'), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 🧬 DIGITAL TWIN TAB
    with t3:
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown('<div class="info-box"><p class="section-header">🔄 State Radar: Physical Engine vs Physics Twin</p>', unsafe_allow_html=True)
            st.plotly_chart(radar_chart(state, exp), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with dt2:
            st.markdown('<div class="info-box"><p class="section-header">🧠 Digital Twin Diagnostics Architecture</p>'
                '<p style="font-size:0.95rem;line-height:1.6;">'
                '1. <b>Physics Model:</b> Computes expected thermodynamic & mechanical parameters dynamically from altitude, temperature, and throttle load.<br><br>'
                '2. <b>Residual Computation:</b> <code>Residual = Actual Telemetry − Physics Baseline</code>. Isolates physical degradation from normal environmental variations.<br><br>'
                '3. <b>AI Anomaly Classifier:</b> Evaluates multi-parameter residual patterns to identify incipient faults before threshold alerts are triggered.'
                '</p></div>', unsafe_allow_html=True)

    # 🛫 MISSION RISK TAB
    with t4:
        mr1, mr2 = st.columns(2)
        with mr1:
            st.markdown('<div class="info-box"><p class="section-header">⏳ RUL vs Required Mission Endurance</p>', unsafe_allow_html=True)
            rf = go.Figure(go.Bar(
                x=['RUL (Pessimistic)','RUL (Optimistic)','Mission Remaining'],
                y=[rl,rh,mhrs],
                marker_color=['#EA580C','#059669','#4F46E5'],
                text=[f'<b>{rl}h</b>',f'<b>{rh}h</b>',f'<b>{mhrs}h</b>'],
                textposition='outside'
            ))
            rf.update_layout(height=260,yaxis_title="Flight Hours",margin=dict(l=10,r=10,t=20,b=10),
                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#0F172A'})
            rf.update_xaxes(linecolor='#94A3B8', tickfont={'color':'#0F172A', 'weight':600})
            rf.update_yaxes(showgrid=True, gridcolor='#E2E8F0', linecolor='#94A3B8', tickfont={'color':'#0F172A'})
            st.plotly_chart(rf, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with mr2:
            st.markdown('<div class="info-box"><p class="section-header">🔮 What-If Mission Extension Simulator</p>', unsafe_allow_html=True)
            se = st.slider("Simulate mission extension (extra hours)", 0.0, 4.0, 1.0, 0.5)
            ph = max(0, health - (sev*2)*(mhrs+se)*4)
            st.metric("Projected Engine Health at Landing", f"{ph:.1f}%")
            if ph < 60:
                st.markdown('<div class="alert-card alert-red">🔴 <b>Mission Abort Recommended:</b> Projected health at touchdown drops below 60% structural safety threshold.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-card alert-green">✅ <b>Extension Safe:</b> Engine degradation remains within acceptable risk tolerance.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 🔁 REPLAY TAB
    with t5:
        st.markdown('<div class="info-box"><p class="section-header">🛫 Mission Timeline & Anomaly Detection Replay</p>', unsafe_allow_html=True)
        pf = make_subplots(rows=2,cols=1,shared_xaxes=True,subplot_titles=('<b>Altitude Profile (ft)</b>','<b>Engine Health Degradation Index (%)</b>'))
        pf.add_trace(go.Scatter(x=hdf['time_sec']/60,y=hdf['altitude'],fill='tozeroy',line=dict(color='#4F46E5',width=2.5)),1,1)
        pf.add_trace(go.Scatter(x=hdf['time_sec']/60,y=hdf['health'],fill='tozeroy',line=dict(color='#059669',width=2.5)),2,1)
        pf.add_vline(x=72, line_dash="dash", line_color="#DC2626", annotation_text="Anomaly Injected (T=72m)", row=1, col=1)
        pf.update_layout(height=360,margin=dict(l=10,r=10,t=30,b=10),paper_bgcolor='rgba(0,0,0,0)',showlegend=False,font={'color':'#0F172A'})
        pf.update_xaxes(showgrid=True,gridcolor='#E2E8F0',linecolor='#94A3B8',tickfont={'color':'#0F172A'})
        pf.update_yaxes(showgrid=True,gridcolor='#E2E8F0',linecolor='#94A3B8',tickfont={'color':'#0F172A'})
        st.plotly_chart(pf, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```
