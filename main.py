import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="청소년 건강 & 생활시간 대시보드",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 커스텀 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
}
.hero-banner {
    background: linear-gradient(120deg, rgba(99,102,241,0.25), rgba(168,85,247,0.25));
    border: 1px solid rgba(168,85,247,0.35);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.8rem;
    text-align: center;
}
.hero-banner h1 {
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero-banner p { color: rgba(255,255,255,0.60); font-size: 0.95rem; margin: 0; }
.kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px; padding: 1.2rem 1.4rem; text-align: center;
}
.kpi-label { font-size:0.75rem; color:rgba(255,255,255,0.50); text-transform:uppercase; letter-spacing:.07em; margin-bottom:.4rem; }
.kpi-value { font-size:1.9rem; font-weight:800; color:#a78bfa; line-height:1; }
.kpi-pos   { color:#34d399; font-size:0.8rem; }
.kpi-neg   { color:#f87171; font-size:0.8rem; }
.section-header {
    font-size:1.1rem; font-weight:700; color:#e2e8f0;
    margin:1.6rem 0 0.8rem;
    padding-bottom:.5rem;
    border-bottom:1px solid rgba(255,255,255,0.08);
}
.insight-box {
    background:rgba(99,102,241,0.12); border-left:3px solid #6366f1;
    border-radius:0 12px 12px 0; padding:.9rem 1.2rem;
    color:rgba(255,255,255,0.80); font-size:.88rem; line-height:1.65; margin-top:.6rem;
}
.warn-box {
    background:rgba(251,191,36,0.10); border-left:3px solid #fbbf24;
    border-radius:0 12px 12px 0; padding:.9rem 1.2rem;
    color:rgba(255,255,255,0.80); font-size:.88rem; line-height:1.65; margin-top:.6rem;
}
.tag {
    display:inline-block; background:rgba(167,139,250,0.2); color:#a78bfa;
    border-radius:999px; padding:.15rem .65rem; font-size:.72rem; font-weight:600; margin-right:.3rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────
@st.cache_data
def load_sleep_data():
    df = pd.read_excel(
        "청소년+평균수면시간+및+주관적+건강인지율_20260611112856_분석(2007_대비_증감).xlsx",
        sheet_name="데이터", header=[0, 1],
    )
    df.columns = ["시점", "수면_전체", "수면_남", "수면_여",
                  "건강인지_전체", "건강인지_남", "건강인지_여"]
    df = df[df["시점"] != "시점"].copy()
    df["시점"] = pd.to_numeric(df["시점"], errors="coerce")
    df = df.dropna(subset=["시점"])
    df["시점"] = df["시점"].astype(int)
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_lifetime_data():
    raw = pd.read_excel(
        "필수생활시간_20260611113006.xlsx",
        sheet_name="데이터", header=None,
    )

    def hhmm(val):
        if pd.isna(val) or val == "-":
            return None
        s = str(val).strip()
        if ":" in s:
            h, m = s.split(":")
            return int(h) * 60 + int(m)
        return None

    years    = ["1999", "2004", "2009", "2014", "2019", "2024"]
    row_map  = {3: "필수생활시간", 4: "수면", 5: "식사및간식",
                8: "개인건강관리", 9: "개인위생및외모관리"}
    records  = []
    for i, yr in enumerate(years):
        base = 2 + i * 12
        r = {"연도": int(yr)}
        for ridx, lbl in row_map.items():
            for gi, gk in enumerate(["계", "남", "여"]):
                r[f"{lbl}_{gk}"] = hhmm(raw.iloc[ridx, base + gi])
            for dk, doff in [("평일", 3), ("토요일", 6), ("일요일", 9)]:
                r[f"{lbl}_{dk}"] = hhmm(raw.iloc[ridx, base + doff])
        records.append(r)
    return pd.DataFrame(records)


def min_to_hhmm(m):
    if m is None or (isinstance(m, float) and pd.isna(m)):
        return "-"
    m = int(m)
    return f"{m // 60}시간 {m % 60:02d}분"


sleep_df = load_sleep_data()
life_df  = load_lifetime_data()


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ 대시보드 설정")
    st.markdown("---")
    page = st.radio(
        "분석 섹션 선택",
        ["🏠 전체 요약", "🌙 수면 & 건강인지율", "⏰ 필수생활시간"],
    )
    st.markdown("---")

    if page == "🌙 수면 & 건강인지율":
        st.markdown("### 🔍 상세 필터")
        gender_s = st.multiselect(
            "성별 선택", ["전체", "남학생", "여학생"],
            default=["전체", "남학생", "여학생"],
        )
        year_range = st.slider(
            "연도 범위",
            int(sleep_df["시점"].min()), int(sleep_df["시점"].max()),
            (int(sleep_df["시점"].min()), int(sleep_df["시점"].max())),
        )

    elif page == "⏰ 필수생활시간":
        st.markdown("### 🔍 상세 필터")
        g_raw    = st.selectbox("성별", ["전체(계)", "남자", "여자"])
        g_key    = {"전체(계)": "계", "남자": "남", "여자": "여"}[g_raw]
        daytype  = st.selectbox("요일 유형", ["요일평균", "평일", "토요일", "일요일"])
        dt_key   = {"요일평균": "계", "평일": "평일", "토요일": "토요일", "일요일": "일요일"}[daytype]

    st.markdown("---")
    st.markdown(
        """<div style='font-size:.75rem;color:rgba(255,255,255,.35);line-height:1.7'>
        📌 출처: 질병관리청 청소년건강행태조사<br>
        📌 출처: 서울특별시 생활시간조사<br>
        🗓️ 다운로드: 2026.06.11
        </div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════
# 페이지 ① — 전체 요약
# ══════════════════════════════════════════════
if page == "🏠 전체 요약":
    st.markdown("""
    <div class="hero-banner">
        <h1>🌙 청소년 건강 & 생활시간 대시보드</h1>
        <p>청소년 수면 변화 · 주관적 건강인지율 · 서울시민 필수생활시간 종합 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ──
    latest_s = sleep_df[sleep_df["시점"] == sleep_df["시점"].max()].iloc[0]
    latest_l = life_df[life_df["연도"] == life_df["연도"].max()].iloc[0]
    first_l  = life_df[life_df["연도"] == life_df["연도"].min()].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    sv  = float(latest_s["수면_전체"])
    hv  = float(latest_s["건강인지_전체"]) if not pd.isna(latest_s["건강인지_전체"]) else 0
    slv = int(latest_l["수면_계"])
    lv  = int(latest_l["필수생활시간_계"])

    def delta_cls(v):
        return "kpi-pos" if v >= 0 else "kpi-neg"

    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">수면 증감 (전체 최신)</div>
            <div class="kpi-value">{sv:+.1f}h</div>
            <span class="{delta_cls(sv)}">2007년 대비</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">건강인지율 증감</div>
            <div class="kpi-value">{hv:+.1f}%p</div>
            <span class="{delta_cls(hv)}">2007년 대비</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">2024 하루 수면 (서울)</div>
            <div class="kpi-value">{slv//60}h{slv%60:02d}m</div>
            <span class="kpi-pos">요일평균</span>
        </div>""", unsafe_allow_html=True)
    with c4:
        delta_life = lv - int(first_l["필수생활시간_계"])
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">2024 필수생활시간 (서울)</div>
            <div class="kpi-value">{lv//60}h{lv%60:02d}m</div>
            <span class="{delta_cls(delta_life)}">1999 대비 {'+' if delta_life>=0 else ''}{delta_life}분</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 차트 2열 ──
    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="section-header">📉 청소년 수면시간 증감 추이</div>', unsafe_allow_html=True)
        s_chart = sleep_df[["시점", "수면_전체", "수면_남", "수면_여"]].set_index("시점")
        s_chart.columns = ["전체", "남학생", "여학생"]
        st.line_chart(s_chart, use_container_width=True, height=260)
        st.markdown('<div class="insight-box">🔍 2017년 이후 지속 감소 추세. 여학생 감소폭이 더 뚜렷하며 2022년 최저점 기록.</div>', unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="section-header">💪 주관적 건강인지율 증감 추이</div>', unsafe_allow_html=True)
        h_chart = sleep_df[["시점", "건강인지_전체", "건강인지_남", "건강인지_여"]].set_index("시점")
        h_chart.columns = ["전체", "남학생", "여학생"]
        st.area_chart(h_chart, use_container_width=True, height=260)
        st.markdown('<div class="insight-box">🔍 2015년까지 꾸준히 상승 후 하락 반전. 여학생은 2021년부터 기준치(0) 이하 진입.</div>', unsafe_allow_html=True)

    # ── 생활시간 바 ──
    st.markdown('<div class="section-header">⏱️ 서울시민 필수생활시간 구성 변화 (1999→2024, 분)</div>', unsafe_allow_html=True)
    bar_df = life_df[["연도", "수면_계", "식사및간식_계", "개인위생및외모관리_계"]].set_index("연도")
    bar_df.columns = ["수면", "식사 및 간식", "개인위생 및 외모"]
    st.bar_chart(bar_df, use_container_width=True, height=280)
    st.markdown('<div class="warn-box">⚡ 25년간 세 항목 모두 증가 → 필수생활시간이 1999년 대비 2024년 약 <strong>65분 증가</strong>했습니다.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 페이지 ② — 수면 & 건강인지율
# ══════════════════════════════════════════════
elif page == "🌙 수면 & 건강인지율":
    st.markdown("""
    <div class="hero-banner">
        <h1>🌙 수면 & 주관적 건강인지율</h1>
        <p>질병관리청 청소년건강행태조사 · 2007년 대비 증감 분석 (2007~2025)</p>
    </div>
    """, unsafe_allow_html=True)

    filtered = sleep_df[
        (sleep_df["시점"] >= year_range[0]) &
        (sleep_df["시점"] <= year_range[1])
    ].copy()

    g_map = {
        "전체":   ("수면_전체",  "건강인지_전체"),
        "남학생": ("수면_남",    "건강인지_남"),
        "여학생": ("수면_여",    "건강인지_여"),
    }

    # ── 수면 차트 ──
    st.markdown('<div class="section-header">📊 주중 평균 수면시간 증감 (시간)</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="tag">2007 기준 = 0</span> <span class="tag">선택: {year_range[0]}~{year_range[1]}</span>', unsafe_allow_html=True)

    if gender_s:
        sc = filtered[["시점"] + [g_map[g][0] for g in gender_s]].set_index("시점")
        sc.columns = gender_s
        st.line_chart(sc, use_container_width=True, height=300)

    c1, c2, c3 = st.columns(3)
    for col, g in zip([c1, c2, c3], ["전체", "남학생", "여학생"]):
        scol = g_map[g][0]
        vals = filtered[scol].dropna()
        v    = vals.iloc[-1] if len(vals) else 0
        wy   = filtered.loc[filtered[scol].idxmin(), "시점"] if len(vals) else "-"
        with col:
            st.metric(
                label=f"{'🔴' if v < 0 else '🟢'} {g}",
                value=f"{v:+.2f}h",
                delta=f"최저 {wy}년",
                delta_color="inverse",
            )

    # ── 건강인지율 차트 ──
    st.markdown('<div class="section-header">💪 주관적 건강인지율 증감 (%p)</div>', unsafe_allow_html=True)
    if gender_s:
        hc = filtered[["시점"] + [g_map[g][1] for g in gender_s]].set_index("시점")
        hc.columns = gender_s
        st.area_chart(hc, use_container_width=True, height=300)

    c1, c2, c3 = st.columns(3)
    for col, g in zip([c1, c2, c3], ["전체", "남학생", "여학생"]):
        hcol = g_map[g][1]
        vals = filtered[hcol].dropna()
        v    = vals.iloc[-1] if len(vals) else 0
        py   = filtered.loc[filtered[hcol].idxmax(), "시점"] if len(vals) else "-"
        with col:
            st.metric(
                label=f"{'🔴' if v < 0 else '🟢'} {g}",
                value=f"{v:+.1f}%p",
                delta=f"최고 {py}년",
            )

    # ── 상관 분석 ──
    st.markdown('<div class="section-header">🔗 수면 vs 건강인지율 상관 분석</div>', unsafe_allow_html=True)
    scat = filtered[["수면_전체", "건강인지_전체"]].dropna()
    scat.columns = ["수면 증감(h)", "건강인지율 증감(%p)"]
    st.scatter_chart(scat, x="수면 증감(h)", y="건강인지율 증감(%p)", use_container_width=True, height=280)
    if len(scat) > 1:
        corr = scat.corr().iloc[0, 1]
        st.markdown(f'<div class="insight-box">📐 피어슨 상관계수 <strong>{corr:.3f}</strong> — 수면시간과 건강인지율 사이에 {"<strong>정(+)의 상관관계</strong>가 있습니다 (수면↑ → 건강인지율↑)." if corr > 0 else "<strong>부(-)의 상관관계</strong>가 나타납니다."}</div>', unsafe_allow_html=True)

    # ── 성별 비교 바 차트 ──
    st.markdown('<div class="section-header">👫 남학생 vs 여학생 비교 (최근 5개년)</div>', unsafe_allow_html=True)
    last5 = filtered.tail(5)[["시점", "수면_남", "수면_여", "건강인지_남", "건강인지_여"]].set_index("시점")
    ca, cb = st.columns(2)
    with ca:
        st.caption("수면시간 증감 (h)")
        st.bar_chart(last5[["수면_남", "수면_여"]].rename(columns={"수면_남": "남학생", "수면_여": "여학생"}),
                     use_container_width=True, height=220)
    with cb:
        st.caption("건강인지율 증감 (%p)")
        st.bar_chart(last5[["건강인지_남", "건강인지_여"]].rename(columns={"건강인지_남": "남학생", "건강인지_여": "여학생"}),
                     use_container_width=True, height=220)

    with st.expander("📋 원본 데이터 보기"):
        show = filtered.copy()
        show.columns = ["연도", "수면(전체)", "수면(남)", "수면(여)",
                        "건강인지(전체)", "건강인지(남)", "건강인지(여)"]
        st.dataframe(show.set_index("연도"), use_container_width=True)


# ══════════════════════════════════════════════
# 페이지 ③ — 필수생활시간
# ══════════════════════════════════════════════
elif page == "⏰ 필수생활시간":
    st.markdown("""
    <div class="hero-banner">
        <h1>⏰ 서울시민 필수생활시간</h1>
        <p>서울특별시 생활시간조사 · 1999~2024년 5년 주기 분석</p>
    </div>
    """, unsafe_allow_html=True)

    # 컬럼 suffix: 요일평균 + 성별 → {항목}_{g_key}, 요일별 → {항목}_{dt_key}
    suffix = g_key if dt_key == "계" else dt_key

    items_map = {
        "필수생활시간":      f"필수생활시간_{suffix}",
        "수면":             f"수면_{suffix}",
        "식사 및 간식":     f"식사및간식_{suffix}",
        "개인건강관리":      f"개인건강관리_{suffix}",
        "개인위생·외모관리": f"개인위생및외모관리_{suffix}",
    }
    emojis = ["🕐", "😴", "🍽️", "💊", "🚿"]

    # ── KPI 카드 ──
    latest = life_df.iloc[-1]
    first  = life_df.iloc[0]
    cols   = st.columns(5)
    for col, (label, key), em in zip(cols, items_map.items(), emojis):
        v_now   = latest.get(key)
        v_first = first.get(key)
        delta_m = int(v_now) - int(v_first) if v_now is not None and v_first is not None else None
        delta_s = f"{'+' if delta_m >= 0 else ''}{delta_m}분" if delta_m is not None else "-"
        dcls    = "kpi-pos" if (delta_m or 0) >= 0 else "kpi-neg"
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{em} {label}</div>
                <div class="kpi-value" style="font-size:1.4rem">{min_to_hhmm(v_now)}</div>
                <span class="{dcls}">{delta_s} vs 1999</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 추이 라인 차트 ──
    label_disp = f"{daytype} / {'전체' if g_key == '계' else g_key}"
    st.markdown(f'<div class="section-header">📈 항목별 추이 — {label_disp} (분)</div>', unsafe_allow_html=True)

    trend_cols = {k: v for k, v in items_map.items() if k != "필수생활시간"}
    valid = {k: v for k, v in trend_cols.items() if v in life_df.columns}
    trend_df = life_df[["연도"] + list(valid.values())].set_index("연도")
    trend_df.columns = list(valid.keys())
    st.line_chart(trend_df, use_container_width=True, height=300)

    # ── 막대 비교 ──
    st.markdown('<div class="section-header">📊 항목별 절댓값 비교 (분)</div>', unsafe_allow_html=True)
    st.bar_chart(trend_df, use_container_width=True, height=270)

    # ── 요일별 비교 (2024) ──
    st.markdown('<div class="section-header">📅 2024년 요일별 비교</div>', unsafe_allow_html=True)
    row24 = life_df[life_df["연도"] == 2024].iloc[0]
    day_map = {"요일평균": "계", "평일": "평일", "토요일": "토요일", "일요일": "일요일"}
    sub_items = ["수면", "식사및간식", "개인위생및외모관리"]
    sub_labels = ["수면", "식사 및 간식", "개인위생·외모"]
    day_data = {}
    for dlabel, dkey in day_map.items():
        day_data[dlabel] = [row24.get(f"{s}_{dkey}") for s in sub_items]
    day_df = pd.DataFrame(day_data, index=sub_labels).T
    st.bar_chart(day_df, use_container_width=True, height=260)

    sleep_wkday = row24.get("수면_평일", 0) or 0
    sleep_sun   = row24.get("수면_일요일", 0) or 0
    diff_s = int(sleep_sun) - int(sleep_wkday)
    st.markdown(f'<div class="insight-box">🛋️ 2024년 일요일 수면은 평일 대비 <strong>{diff_s}분</strong> 더 깁니다. 주말 수면 보충 패턴이 뚜렷하게 나타납니다.</div>', unsafe_allow_html=True)

    # ── 수면시간 연도별 성별 비교 ──
    st.markdown('<div class="section-header">👫 연도별 수면시간 성별 비교 (요일평균, 분)</div>', unsafe_allow_html=True)
    gender_comp = life_df[["연도", "수면_계", "수면_남", "수면_여"]].set_index("연도")
    gender_comp.columns = ["전체", "남자", "여자"]
    st.line_chart(gender_comp, use_container_width=True, height=250)

    with st.expander("📋 원본 데이터 보기 (분 단위)"):
        show_cols = ["연도"] + [v for v in items_map.values() if v in life_df.columns]
        st.dataframe(life_df[show_cols].set_index("연도"), use_container_width=True)
