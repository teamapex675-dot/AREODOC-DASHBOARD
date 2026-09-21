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
# PAGE CONFIGURATION & THEME
# ============================================================
st.set_page_config(
    page_title="AeroTwin – Digital Twin Dashboard",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom White/Clean CSS
st.markdown("""
<style>
    .stApp { background-color: #FAFBFC; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F0F4F8 100%);
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important; font-size: 0.8rem !important;
        font-weight: 500 !important; text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] { color: #1E293B !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background: #FFFFFF; border-radius: 12px;
        padding: 4px; border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 8px 20px; color: #64748B; font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #EEF2FF !important; color: #4338CA !important; font-weight: 600;
    }
    .health-card {
        background: #FFFFFF; border-radius: 16px; padding: 20px;
        border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        text-align: center; margin-bottom: 16px;
    }
    .health-card h2 { margin: 0; font-size: 2.5rem; font-weight: 800; }
    .health-card p { color: #64748B; margin: 4px 0 0 0; font-size: 0.9rem; }
    .alert-card {
        border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; border-left: 4px solid;
    }
    .alert-green { background: #F0FDF4; border-color: #22C55E; color: #166534; }
    .alert-yellow { background: #FEFCE8; border-color: #EAB308; color: #854D0E; }
    .alert-orange { background: #FFF7ED; border-color: #F97316; color: #9A3412; }
    .alert-red { background: #FEF2F2; border-color: #EF4444; color: #991B1B; }
    .alert-blue { background: #EFF6FF; border-color: #3B82F6; color: #1E40AF; }
    .info-box {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 18px; margin-bottom: 16px;
    }
    .section-header {
        color: #1E293B; font-size: 1.05rem; font-weight: 700;
        margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid #EEF2FF;
    }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DOMAIN MODELS & ENUMS
# ============================================================
class FaultType(Enum):
    HEALTHY = "Healthy"
    INJECTOR_DEGRADATION = "Injector Degradation"
    MISFIRE = "Misfire"
    OVERHEATING = "Overheating"
    LUBRICATION_PROBLEM = "Lubrication Problem"
    SENSOR_DRIFT = "Sensor Drift"
    ABNORMAL_VIBRATION = "Abnormal Vibration"

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
# VISUALIZATION FUNCTIONS
# ============================================================
def gauge(val, title):
    c = "#22C55E" if val>=90 else "#EAB308" if val>=75 else "#F97316" if val>=60 else "#EF4444"
    fig = go.Figure(go.Indicator(mode="gauge+number", value=val,
        title={'text':title,'font':{'size':14,'color':'#64748B'}},
        number={'font':{'size':30,'color':'#1E293B'}},
        gauge={'axis':{'range':[0,100],'tickcolor':'#CBD5E1'},
               'bar':{'color':c,'thickness':0.3},'bgcolor':'#F1F5F9',
               'steps':[{'range':[0,60],'color':'#FEF2F2'},{'range':[60,75],'color':'#FFF7ED'},
                        {'range':[75,90],'color':'#FEFCE8'},{'range':[90,100],'color':'#F0FDF4'}]}))
    fig.update_layout(height=190, margin=dict(l=15,r=15,t=35,b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def cyl_chart(cht, egt):
    cys = ['Cyl 1','Cyl 2','Cyl 3','Cyl 4']
    fig = make_subplots(rows=1,cols=2,subplot_titles=('CHT (°C)','EGT (°C)'),horizontal_spacing=0.12)
    cc = ['#EF4444' if v>220 else '#F97316' if v>200 else '#6366F1' for v in cht]
    ec = ['#EF4444' if v>800 else '#F97316' if v>760 else '#8B5CF6' for v in egt]
    fig.add_trace(go.Bar(x=cys,y=cht,marker_color=cc,text=[f'{v:.0f}' for v in cht],textposition='outside'),1,1)
    fig.add_trace(go.Bar(x=cys,y=egt,marker_color=ec,text=[f'{v:.0f}' for v in egt],textposition='outside'),1,2)
    fig.update_layout(height=260,showlegend=False,margin=dict(l=10,r=10,t=35,b=10),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#64748B','size':11})
    fig.update_xaxes(showgrid=False,linecolor='#E2E8F0')
    fig.update_yaxes(showgrid=True,gridcolor='#F1F5F9',linecolor='#E2E8F0')
    return fig

def ts_chart(df, cols, title, yl=""):
    fig = go.Figure()
    colors = ['#6366F1','#8B5CF6','#EC4899','#F97316','#22C55E','#3B82F6']
    for i,c in enumerate(cols):
        fig.add_trace(go.Scatter(x=df['time_sec']/60,y=df[c],name=c.replace('_',' ').title(),
            line=dict(color=colors[i%len(colors)],width=2),mode='lines'))
    fig.update_layout(title=dict(text=title,font=dict(size=13,color='#334155')),height=290,
        margin=dict(l=10,r=10,t=35,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font={'color':'#64748B','size':11},
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,font=dict(size=10)),
        xaxis_title="Time (min)",yaxis_title=yl)
    fig.update_xaxes(showgrid=True,gridcolor='#F1F5F9',linecolor='#E2E8F0')
    fig.update_yaxes(showgrid=True,gridcolor='#F1F5F9',linecolor='#E2E8F0')
    return fig

def res_chart(r):
    keys = ['rpm','egt_max','cht_max','oil_pressure','oil_temperature','fuel_flow','vibration']
    labels = ['RPM','EGT','CHT','Oil P','Oil T','Fuel','Vib']
    vals = [r.get(k,0)*100 for k in keys]
    colors = ['#EF4444' if v>15 else '#F97316' if v>8 else '#EAB308' if v>4 else '#22C55E' for v in vals]
    fig = go.Figure(go.Bar(x=labels,y=vals,marker_color=colors,text=[f'{v:.1f}%' for v in vals],textposition='outside'))
    fig.add_hline(y=15,line_dash="dash",line_color="#EF4444",annotation_text="Alert",annotation_font_color="#EF4444")
    fig.update_layout(title=dict(text="Residuals (Actual vs Expected)",font=dict(size=13,color='#334155')),
        yaxis_title="Deviation (%)",height=260,margin=dict(l=10,r=10,t=35,b=10),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#64748B','size':11})
    return fig

def radar_chart(s, e):
    params = ['RPM','CHT avg','EGT avg','Oil P','Oil T','Fuel']
    av = [s.rpm, np.mean(s.cht), np.mean(s.egt), s.oil_pressure, s.oil_temperature, s.fuel_flow]
    ev = [e['rpm'], np.mean(e['cht']), np.mean(e['egt']), e['oil_p'], e['oil_t'], e['fuel']]
    mx = [max(a,b,1) for a,b in zip(av,ev)]
    an = [a/m*100 for a,m in zip(av,mx)]
    en = [b/m*100 for b,m in zip(ev,mx)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=en+[en[0]],theta=params+[params[0]],fill='toself',
        fillcolor='rgba(99,102,241,0.1)',line=dict(color='#6366F1',width=2),name='Physics Twin'))
    fig.add_trace(go.Scatterpolar(r=an+[an[0]],theta=params+[params[0]],fill='toself',
        fillcolor='rgba(239,68,68,0.1)',line=dict(color='#EF4444',width=2),name='Actual Engine'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,120],showticklabels=False),
        bgcolor='rgba(0,0,0,0)'),height=310,margin=dict(l=35,r=35,t=20,b=20),paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h',yanchor='bottom',y=-0.15,xanchor='center',x=0.5))
    return fig

# ============================================================
# MAIN APPLICATION
# ============================================================
def main():
    with st.sidebar:
        st.markdown("## 🚁 AeroTwin")
        st.markdown('<p style="color:#64748B;font-size:0.85rem;">Digital Twin Engine Health Monitor<br>SIH 2026 – PS-8</p>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('##### ⚙️ Simulation Controls')

        fault_map = {
            "🟢 Healthy": FaultType.HEALTHY, "🟡 Injector Degradation": FaultType.INJECTOR_DEGRADATION,
            "🟠 Misfire": FaultType.MISFIRE, "🔴 Overheating": FaultType.OVERHEATING,
            "🔴 Lubrication Problem": FaultType.LUBRICATION_PROBLEM,
            "🔵 Sensor Drift": FaultType.SENSOR_DRIFT, "🟣 Abnormal Vibration": FaultType.ABNORMAL_VIBRATION,
        }
        sel = st.selectbox("Inject Fault Scenario", list(fault_map.keys()), index=1)
        ft = fault_map[sel]
        sev = st.slider("Severity", 0.0, 1.0, 0.45, 0.05)
        cyl = st.selectbox("Cylinder Target", [1,2,3,4], index=1)
        st.markdown("---")
        st.markdown('##### 🛫 Mission Profile')
        thr = st.slider("Throttle (%)", 30, 100, 70)
        alt = st.slider("Altitude (ft)", 0, 30000, 15000, 1000)
        mhrs = st.slider("Remaining Time (hrs)", 0.5, 8.0, 3.0, 0.5)

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
        '<h2 style="color:#1E293B;margin-bottom:2px;">🚁 Aero Piston Engine Digital Twin</h2>'
        '<p style="color:#64748B;font-size:0.9rem;">Real-time Telemetry • Physics Residuals • Fault Prognostics</p></div>',
        unsafe_allow_html=True)

    # Status Bar
    rc = {'LOW':'#22C55E','MEDIUM':'#EAB308','HIGH':'#F97316','CRITICAL':'#EF4444'}
    rb = {'LOW':'#F0FDF4','MEDIUM':'#FEFCE8','HIGH':'#FFF7ED','CRITICAL':'#FEF2F2'}
    re = {'LOW':'🟢','MEDIUM':'🟡','HIGH':'🟠','CRITICAL':'🔴'}
    st.markdown(f'<div style="background:{rb[mrisk]};border:1px solid {rc[mrisk]};border-radius:10px;'
        f'padding:10px 18px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">'
        f'<span style="font-weight:700;color:{rc[mrisk]};font-size:0.95rem;">{re[mrisk]} Mission Risk: {mrisk}</span>'
        f'<span style="color:#64748B;font-size:0.85rem;">Health: <b>{health}%</b> | Fault: <b>{fault.value}</b> | '
        f'Confidence: <b>{conf*100:.0f}%</b> | RUL: <b>{rl}-{rh}h</b> | Alt: <b>{alt:,}ft</b></span></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["👨‍✈️ Pilot View","👨‍🔧 Engineer View","🧬 Digital Twin","🛫 Mission Risk","🔁 Replay"])

    with t1:
        c1,c2,c3 = st.columns([1.2,1,1])
        with c1:
            hc = '#22C55E' if health>=90 else '#EAB308' if health>=75 else '#F97316' if health>=60 else '#EF4444'
            st.markdown(f'<div class="health-card"><p>ENGINE HEALTH</p><h2 style="color:{hc};">{health}%</h2>'
                f'<p>Engine Total Hours: {state.engine_hours:.1f}h</p></div>', unsafe_allow_html=True)
            st.plotly_chart(gauge(health,"Health Score"), use_container_width=True)
        with c2:
            st.markdown('<div class="info-box"><p class="section-header">⚠️ Warning & Alerts</p>', unsafe_allow_html=True)
            if fault == FaultType.HEALTHY:
                st.markdown('<div class="alert-card alert-green">✅ All systems nominal</div>', unsafe_allow_html=True)
            else:
                ac = 'alert-red' if mrisk=='CRITICAL' else 'alert-orange' if mrisk=='HIGH' else 'alert-yellow'
                st.markdown(f'<div class="alert-card {ac}"><strong>⚠️ {fault.value}</strong><br>'
                    f'📍 Target: Cylinder {cyl}<br>🤖 AI Confidence: {conf*100:.0f}%<br>⏳ RUL: {rl}-{rh} hrs</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="info-box"><p class="section-header">📋 Quick Flight Data</p>', unsafe_allow_html=True)
            st.metric("RPM", f"{state.rpm:.0f}"); st.metric("Fuel Flow", f"{state.fuel_flow:.1f} L/h")
            st.metric("Vibration", f"{state.vibration:.3f} g"); st.metric("Altitude", f"{alt:,} ft")
            st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("RPM", f"{state.rpm:.0f}", f"{state.rpm-exp['rpm']:.0f}")
        m2.metric("Oil P", f"{state.oil_pressure:.1f} psi", f"{state.oil_pressure-exp['oil_p']:.1f}")
        m3.metric("Oil T", f"{state.oil_temperature:.1f}°C", f"{state.oil_temperature-exp['oil_t']:.1f}")
        m4.metric("Fuel Flow", f"{state.fuel_flow:.1f} L/h", f"{state.fuel_flow-exp['fuel']:.1f}")
        m5.metric("Vibration", f"{state.vibration:.3f} g", f"{state.vibration-exp['vib']:.3f}")
        m6.metric("Battery", f"{state.battery_voltage:.1f} V")

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown('<div class="info-box"><p class="section-header">🔥 Cylinder CHT / EGT Status</p>', unsafe_allow_html=True)
            st.plotly_chart(cyl_chart(state.cht, state.egt), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cc2:
            st.markdown('<div class="info-box"><p class="section-header">📐 Physics Residuals</p>', unsafe_allow_html=True)
            st.plotly_chart(res_chart(res), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        tc1, tc2 = st.columns(2)
        with tc1:
            st.plotly_chart(ts_chart(hdf,['egt_1','egt_2','egt_3','egt_4'],'🌡️ Cylinder Exhaust Gas Temp (EGT)','°C'), use_container_width=True)
        with tc2:
            st.plotly_chart(ts_chart(hdf,['oil_pressure','oil_temperature'],'🛢️ Oil Health Metrics','Value'), use_container_width=True)

    with t3:
        dt1, dt2 = st.columns(2)
        with dt1:
            st.markdown('<div class="info-box"><p class="section-header">🔄 State Radar (Actual vs Twin)</p>', unsafe_allow_html=True)
            st.plotly_chart(radar_chart(state, exp), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with dt2:
            st.markdown('<div class="info-box"><p class="section-header">🧠 Digital Twin Mechanism</p>'
                '<p style="color:#64748B;font-size:0.9rem;">1. <b>Physics Model</b> calculates expected thermodynamic outputs based on throttle & altitude.<br>'
                '2. <b>Residual Extraction</b> isolates sensor deviations: <code>Residual = Actual - Physics</code><br>'
                '3. <b>AI Prognostics</b> classify anomalies before fixed threshold alarms trip.</p></div>', unsafe_allow_html=True)

    with t4:
        mr1, mr2 = st.columns(2)
        with mr1:
            st.markdown('<div class="info-box"><p class="section-header">⏳ RUL vs Mission Time</p>', unsafe_allow_html=True)
            rf = go.Figure(go.Bar(x=['RUL Low','RUL High','Mission Left'],y=[rl,rh,mhrs],
                marker_color=['#F97316','#22C55E','#6366F1'],text=[f'{rl}h',f'{rh}h',f'{mhrs}h'],textposition='outside'))
            rf.update_layout(height=260,yaxis_title="Hours",margin=dict(l=10,r=10,t=20,b=10),
                paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font={'color':'#64748B'})
            st.plotly_chart(rf, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with mr2:
            st.markdown('<div class="info-box"><p class="section-header">🔮 What-If Scenario</p>', unsafe_allow_html=True)
            se = st.slider("Extend mission duration by (hours)", 0.0, 4.0, 1.0, 0.5)
            ph = max(0, health - (sev*2)*(mhrs+se)*4)
            st.metric("Projected Health at Mission End", f"{ph:.1f}%")
            if ph < 60:
                st.markdown('<div class="alert-card alert-red">🔴 Abort planned extension: Mission exceeds safe engine RUL.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-card alert-green">✅ Mission extension within acceptable risk envelope.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with t5:
        st.markdown('<div class="info-box"><p class="section-header">🛫 Flight Timeline Replay</p>', unsafe_allow_html=True)
        pf = make_subplots(rows=2,cols=1,shared_xaxes=True,subplot_titles=('Altitude Profile','Degradation Curve'))
        pf.add_trace(go.Scatter(x=hdf['time_sec']/60,y=hdf['altitude'],fill='tozeroy',line=dict(color='#6366F1')),1,1)
        pf.add_trace(go.Scatter(x=hdf['time_sec']/60,y=hdf['health'],fill='tozeroy',line=dict(color='#22C55E')),2,1)
        pf.add_vline(x=72, line_dash="dash", line_color="#EF4444", annotation_text="Anomaly Start", row=1, col=1)
        pf.update_layout(height=360,margin=dict(l=10,r=10,t=30,b=10),paper_bgcolor='rgba(0,0,0,0)',showlegend=False)
        st.plotly_chart(pf, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
