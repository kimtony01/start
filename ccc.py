import urllib.request
import json
import streamlit as st

st.set_page_config(page_title="실시간 환율 계산기", page_icon="💱", layout="centered")

# ---------- 스타일 ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #888;
        margin-bottom: 1.8rem;
    }
    .rate-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.2rem;
    }
    .rate-card h3 { margin: 0; font-size: 1rem; opacity: 0.85; font-weight: 400; }
    .rate-card .big { font-size: 2rem; font-weight: 700; margin: 0.2rem 0; }
    .result-card {
        background: #f7f9fc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-top: 0.8rem;
    }
    .mini-rate {
        background: white;
        border: 1px solid #e8eaf0;
        border-radius: 12px;
        padding: 0.8rem;
        text-align: center;
    }
    .mini-rate .code { color: #888; font-size: 0.8rem; }
    .mini-rate .val { font-weight: 700; font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

CURRENCY_META = {
    "KRW": {"name": "대한민국 원", "flag": "🇰🇷"},
    "USD": {"name": "미국 달러", "flag": "🇺🇸"},
    "JPY": {"name": "일본 엔", "flag": "🇯🇵"},
    "EUR": {"name": "유로", "flag": "🇪🇺"},
    "CNY": {"name": "중국 위안", "flag": "🇨🇳"},
    "GBP": {"name": "영국 파운드", "flag": "🇬🇧"},
}

@st.cache_data(ttl=3600)
def get_exchange_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['rates'], data.get('time_last_update_utc', '알 수 없음')
    except Exception:
        fallback = {'USD': 1.0, 'KRW': 1340.0, 'JPY': 148.0, 'EUR': 0.92, 'CNY': 7.15, 'GBP': 0.78}
        return fallback, "오프라인 기본값 (API 연결 실패)"

rates, last_update = get_exchange_rates()
current_krw = rates.get('KRW', 1340.0)
high_krw = 1550.0
diff = high_krw - current_krw
diff_pct = diff / high_krw * 100

# ---------- 헤더 ----------
st.markdown('<div class="main-title">💱 실시간 환율 계산기</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">최근 업데이트: {last_update}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="rate-card">
    <h3>USD → KRW 기준 환율</h3>
    <div class="big">{current_krw:,.2f} 원</div>
    <div>7월 고점(1,550원) 대비 {diff:,.1f}원 낮음 ({diff_pct:.1f}% ↓)</div>
</div>
""", unsafe_allow_html=True)

# 주요 통화 미니 카드
st.write("**주요 통화 환율 (1 USD 기준)**")
main_codes = ["KRW", "JPY", "EUR", "CNY", "GBP"]
cols = st.columns(len(main_codes))
for col, code in zip(cols, main_codes):
    if code in rates:
        meta = CURRENCY_META.get(code, {"flag": "", "name": code})
        with col:
            st.markdown(f"""
            <div class="mini-rate">
                <div>{meta['flag']}</div>
                <div class="code">{code}</div>
                <div class="val">{rates[code]:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------- 변환기 ----------
st.subheader("🔄 통화 변환")
amount = st.number_input("변환할 금액", min_value=0.0, value=1000.0, step=100.0)

currencies = list(CURRENCY_META.keys())
col1, col2 = st.columns(2)
with col1:
    from_curr = st.selectbox(
        "보유 통화", currencies, index=0,
        format_func=lambda c: f"{CURRENCY_META[c]['flag']} {c} - {CURRENCY_META[c]['name']}"
    )
with col2:
    to_curr = st.selectbox(
        "목표 통화", currencies, index=1,
        format_func=lambda c: f"{CURRENCY_META[c]['flag']} {c} - {CURRENCY_META[c]['name']}"
    )

converted = (amount / rates[from_curr]) * rates[to_curr]
unit_rate = rates[to_curr] / rates[from_curr]

st.markdown(f"""
<div class="result-card">
    <div style="font-size:0.9rem; color:#888;">계산 결과</div>
    <div style="font-size:1.6rem; font-weight:800; margin:0.3rem 0;">
        {amount:,.2f} {from_curr} → {converted:,.2f} {to_curr}
    </div>
    <div style="color:#555;">적용 환율: 1 {from_curr} = {unit_rate:,.4f} {to_curr}</div>
</div>
""", unsafe_allow_html=True)

# 다른 통화로도 한눈에 보기
with st.expander("다른 통화로는 얼마일까? 한눈에 보기"):
    other_codes = [c for c in currencies if c != from_curr]
    rows = []
    for c in other_codes:
        val = (amount / rates[from_curr]) * rates[c]
        rows.append(f"- {CURRENCY_META[c]['flag']} **{val:,.2f} {c}** ({CURRENCY_META[c]['name']})")
    st.markdown("\n".join(rows))

st.divider()

# ---------- 참고 정보 ----------
st.subheader("📌 참고 정보")
if from_curr == "KRW" and to_curr == "USD":
    st.info(
        f"현재 환율은 7월 고점(1,550원) 대비 약 {diff:,.0f}원({diff_pct:.1f}%) 낮은 수준입니다.\n\n"
        "- 환전 시점을 나눠서 분산하는 방식(분할 환전)을 고려해볼 수 있습니다.\n"
        "- 환율 변동을 지켜보며 목표 환율에 지정가로 걸어두는 방법도 있습니다.\n\n"
        "※ 이는 일반적인 참고 정보이며 투자·환전 조언이 아닙니다."
    )
elif from_curr == "USD" and to_curr == "KRW":
    st.warning(
        "달러를 원화로 바꾸는 경우 참고할 수 있는 방법입니다.\n\n"
        "- 급락 이후 반등 구간을 지켜보는 접근도 있습니다.\n"
        "- 급하지 않은 자금이라면 외화예금 등 거치 상품을 알아볼 수도 있습니다.\n\n"
        "※ 이는 일반적인 참고 정보이며 투자·환전 조언이 아닙니다."
    )
else:
    st.info(
        f"{from_curr} → {to_curr} 환전은 기준 통화(주로 USD)의 변동성 영향을 받습니다.\n\n"
        "- 한 번에 몰아서 환전하기보다 여러 차례 나눠 진행하면 리스크를 줄일 수 있습니다.\n"
        "- 큰 금액일수록 환전 수수료와 스프레드도 함께 비교해보는 것이 좋습니다.\n\n"
        "※ 이는 일반적인 참고 정보이며 투자·환전 조언이 아닙니다."
    )

st.caption("데이터 출처: open.er-api.com · 1시간마다 자동 갱신")