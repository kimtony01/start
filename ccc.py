import urllib.request
import json
import streamlit as st

st.set_page_config(page_title="실시간 환율 계산기", layout="centered")

@st.cache_data(ttl=3600)
def get_exchange_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['rates']
    except Exception:
        return {'USD': 1.0, 'KRW': 1340.0, 'JPY': 148.0, 'EUR': 0.92, 'CNY': 7.15}

rates = get_exchange_rates()
current_krw = rates.get('KRW', 1340.0)
high_krw = 1550.0
diff = high_krw - current_krw

st.title("실시간 환율 계산 및 맞춤 대응 전략")

st.metric(
    label="현재 USD/KRW 기준 환율",
    value=f"{current_krw:,.2f} 원",
    delta=f"-{diff:,.1f} 원 (7월 고점 대비 하락)"
)

amount = st.number_input("변환할 금액", min_value=0.0, value=1000.0, step=100.0)
currencies = ["KRW", "USD", "JPY", "EUR", "CNY"]
col1, col2 = st.columns(2)
with col1:
    from_curr = st.selectbox("보유 통화", currencies, index=0)
with col2:
    to_curr = st.selectbox("목표 통화", currencies, index=1)

converted = (amount / rates[from_curr]) * rates[to_curr]

st.subheader("계산 결과")
st.success(f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}")
st.write(f"적용 환율: 1 {from_curr} = {rates[to_curr]/rates[from_curr]:,.4f} {to_curr}")

st.subheader("참고 정보")
if from_curr == "KRW" and to_curr == "USD":
    st.info(
        f"현재 환율은 7월 고점(1,550원) 대비 약 {diff:,.0f}원 낮은 수준입니다.\n\n"
        "환전 시점을 나눠서 분산하는 방식(분할 환전)을 고려해볼 수 있고,\n"
        "환율 변동을 지켜보며 목표 환율에 지정가로 걸어두는 방법도 있습니다."
    )
elif from_curr == "USD" and to_curr == "KRW":
    st.warning(
        "달러를 원화로 바꾸는 경우, 최근 하락 이후 반등 구간을 지켜보는 접근도 있고\n"
        "급하지 않다면 일부를 외화예금 등에 거치하는 방법도 고려할 수 있습니다."
    )
else:
    st.info(
        f"{from_curr} → {to_curr} 환전은 기준 통화(주로 USD)의 변동성 영향을 받습니다.\n"
        "한 번에 몰아서 환전하기보다 여러 차례 나눠 진행하면 환율 변동 리스크를 줄일 수 있습니다."
    )

    # dadsafsavsdsaf