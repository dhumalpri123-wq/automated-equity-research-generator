"""
AUTOMATED EQUITY RESEARCH REPORT GENERATOR

Author: Priyraj Dhumal

Features:
- Dynamic NSE Ticker Input
- DCF Valuation
- Peter Lynch Valuation
- Relative Valuation
- Peer Comparison
- Financial Health Scorecard
- SWOT Analysis
- Trend Analysis
- Automated PDF Generation
"""




import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak

)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


ticker = input(
    "Enter NSE Ticker: "
).upper() + ".NS"
stock = yf.Ticker(ticker)

info = stock.info

company_name = info.get(
    "longName",
    ticker.replace(".NS","")
)

recommendation = info.get("recommendationKey", "N/A")

strengths = [
    "Strong ROE",
    "Healthy Profit Margins",
    "Strong Balance Sheet",
    "Consistent Revenue Growth"
]

concerns = [
    "Premium Valuation",
    "Growth Slowdown Risk",
    "Global IT Spending Risk"
]

peer_tickers = [
    "TCS.NS",
    "INFY.NS",
    "HCLTECH.NS",
    "WIPRO.NS"
]

peer_data = []

for peer in peer_tickers:

    peer_stock = yf.Ticker(peer)
    peer_info = peer_stock.info

    peer_data.append([
        peer.replace(".NS",""),
        f"₹{peer_info.get('marketCap',0)/1000000000000:.2f} T",
        f"{peer_info.get('trailingPE',0):.2f}",
        f"{peer_info.get('returnOnEquity',0)*100:.2f}%"
    ])

fcf = info.get("freeCashflow", 0)

growth_rate = 0.08      # 8%
discount_rate = 0.10    # 10%
terminal_growth = 0.03  # 3%

projected_fcfs = []

for year in range(1, 6):

    future_fcf = fcf * ((1 + growth_rate) ** year)

    projected_fcfs.append(future_fcf)

pv_fcfs = 0

for year, cashflow in enumerate(projected_fcfs, start=1):

    pv_fcfs += cashflow / ((1 + discount_rate) ** year)

terminal_value = (
    projected_fcfs[-1] * (1 + terminal_growth)
) / (discount_rate - terminal_growth)

pv_terminal = terminal_value / (
    (1 + discount_rate) ** 5
)

enterprise_value_dcf = pv_fcfs + pv_terminal

shares_outstanding = info.get("sharesOutstanding", 1)

dcf_fair_value = (
    enterprise_value_dcf / shares_outstanding
)
current_price = info.get("currentPrice", 0)

if current_price:
    dcf_upside = (
        (dcf_fair_value - current_price)
        / current_price
    ) * 100
else:
    dcf_upside = 0
eps = info.get("trailingEps",0)

growth_rate = 10

lynch_fair_value = eps * growth_rate

target_price = (
    dcf_fair_value + lynch_fair_value
) / 2

current_price = info.get("currentPrice",0)

if current_price:
    upside = (
        (lynch_fair_value - current_price)
        / current_price
    ) * 100
else:
    upside = 0

income = stock.financials

revenue = income.loc["Total Revenue"]
net_income = income.loc["Net Income"]

df = pd.DataFrame({
    "Revenue": revenue,
    "Net Income": net_income
})

df["Profit Margin %"] = (
    df["Net Income"] / df["Revenue"]
) * 100

df["Revenue Growth %"] = (
    df["Revenue"].pct_change(-1)
) * 100

df = df.dropna()


first_revenue = df["Revenue"].iloc[-1]
latest_revenue = df["Revenue"].iloc[0]

revenue_growth_total = (
    (latest_revenue - first_revenue)
    / first_revenue
) * 100

avg_margin = df["Profit Margin %"].mean()

if revenue_growth_total > 0:
    trend_rating = "POSITIVE"
else:
    trend_rating = "NEGATIVE"

print(df)


price = stock.history(period="5y")

plt.figure(figsize=(10, 5))
plt.plot(price.index, price["Close"])

plt.title("TCS Stock Price - 5 Years")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)

tcs_pe = info.get("trailingPE", 0)

average_peer_pe = (
    15.89 + 14.69 + 18.07 + 14.34
) / 4

if tcs_pe < average_peer_pe:
    valuation_status = "UNDERVALUED"
else:
    valuation_status = "OVERVALUED"

    

chart_file = (
    ticker.replace(".NS","")
    + "_Chart.png"
)

plt.savefig(chart_file)
plt.close()

plt.figure(figsize=(8,4))

revenue_chart = df["Revenue"] / 10000000

plt.plot(
    revenue_chart.index.astype(str),
    revenue_chart.values,
    marker="o"
)

plt.title("Revenue Trend")
plt.ylabel("Revenue (₹ Cr)")
plt.grid(True)

revenue_chart_file = (
    ticker.replace(".NS","")
    + "_RevenueTrend.png"
)

plt.savefig(revenue_chart_file)
plt.close()

plt.figure(figsize=(8,4))

net_income_chart = df["Net Income"] / 10000000

plt.plot(
    net_income_chart.index.astype(str),
    net_income_chart.values,
    marker="o"
)

plt.title("Net Income Trend")
plt.ylabel("Net Income (₹ Cr)")
plt.grid(True)

net_income_chart_file = "NetIncome_Trend_V19.png"

plt.savefig(net_income_chart_file)
plt.close()



pdf = SimpleDocTemplate(
    f"{ticker.replace('.NS', '')}_InvestmentBanking_TearSheet_v20.pdf"
)

styles = getSampleStyleSheet()

content = []

content.append(
    Paragraph(
        "EQUITY RESEARCH REPORT",
        styles["Title"]
    )
)

content.append(
    Paragraph(
        company_name,
        styles["Heading1"]
    )
)

content.append(
    Paragraph(
        "Prepared By: Priyraj Dhumal",
        styles["BodyText"]
    )
)

content.append(PageBreak())



content.append(
    Paragraph(
        company_name,
        styles["Title"]
    )
)

content.append(
    Paragraph(
        "Executive Summary",
        styles["Heading1"]
    )
)
content.append(
    Paragraph(
        f"Target Price: ₹{target_price:.2f}",
        styles["BodyText"]
    )
)
content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Valuation Summary",
        styles["Heading2"]
    )
)

valuation_table = Table([
    ["Method", "Fair Value"],
    ["DCF", f"₹{dcf_fair_value:.2f}"],
    ["Peter Lynch", f"₹{lynch_fair_value:.2f}"],
    ["Current Price", f"₹{current_price:.2f}"]
])

valuation_table.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('GRID',(0,0),(-1,-1),1,colors.black)
]))

content.append(valuation_table)

content.append(Spacer(1,20))

content.append(Spacer(1,10))



for item in concerns:
    content.append(
        Paragraph(f"• {item}", styles["BodyText"])
    )

content.append(Spacer(1,20))

content.append(Spacer(1, 15))




content.append(
    Paragraph(
        f"Market Cap: ₹{info.get('marketCap',0)/1000000000000:.2f} Trillion",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"PE Ratio: {info.get('trailingPE','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Beta: {info.get('beta','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"EPS: {info.get('trailingEps','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"ROE: {info.get('returnOnEquity',0)*100:.2f}%",
        styles["BodyText"]
    )
)

dividend = info.get("dividendYield")

if dividend:
    dividend_text = f"{dividend:.2f}%"
else:
    dividend_text = "N/A"

content.append(
    Paragraph(
        f"Dividend Yield: {dividend_text}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"52 Week High: ₹{info.get('fiftyTwoWeekHigh','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"52 Week Low: ₹{info.get('fiftyTwoWeekLow','N/A')}",
        styles["BodyText"]
    )
)

debt = info.get("totalDebt", 0)
book_value = info.get("bookValue", 0)

if book_value:
    debt_equity = debt / book_value
else:
    debt_equity = 0

content.append(
    Paragraph(
        f"Cash: ₹{info.get('totalCash',0)/10000000:,.0f} Cr",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Debt: ₹{info.get('totalDebt',0)/10000000:,.0f} Cr",
        styles["BodyText"]
    )
)


content.append(Spacer(1, 20))




content.append(
    Paragraph(
        "Valuation Metrics",
        styles["Heading2"]
    )
)



content.append(
    Paragraph(
        f"Peter Lynch Fair Value: ₹{lynch_fair_value:.2f}",
        styles["BodyText"]
    )
)

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "DCF Valuation",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Free Cash Flow: ₹{fcf/10000000:,.0f} Cr",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"DCF Fair Value: ₹{dcf_fair_value:.2f}",
        styles["BodyText"]
    )
)

health_score = 0


investment_score = 0


investment_score += health_score


if trend_rating == "POSITIVE":
    investment_score += 1


if lynch_fair_value > current_price:
    investment_score += 1


if dcf_fair_value > current_price:
    investment_score += 1


if investment_score >= 6:
    final_rating = "BUY"
elif investment_score >= 4:
    final_rating = "HOLD"
else:
    final_rating = "SELL"



content.append(
    Paragraph(
        f"Final Rating: {final_rating}",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Current Price: ₹{current_price:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"DCF Fair Value: ₹{dcf_fair_value:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Peter Lynch Fair Value: ₹{lynch_fair_value:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"DCF Upside / Downside: {dcf_upside:.2f}%",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Peter Lynch Upside / Downside: {upside:.2f}%",
        styles["BodyText"]
    )
)

content.append(Spacer(1,10))

content.append(
    Paragraph(
        "Key Strengths",
        styles["Heading2"]
    )
)

for item in strengths:
    content.append(
        Paragraph(
            f"• {item}",
            styles["BodyText"]
        )
    )

content.append(Spacer(1,10))

content.append(
    Paragraph(
        "Key Concerns",
        styles["Heading2"]
    )
)

for item in concerns:
    content.append(
        Paragraph(
            f"• {item}",
            styles["BodyText"]
        )
    )

content.append(Spacer(1,20))

roe = info.get("returnOnEquity", 0) * 100

if roe > 15:
    roe_status = "PASS"
    health_score += 1
else:
    roe_status = "FAIL"

profit_margin = df.iloc[0]["Profit Margin %"]

if profit_margin > 10:
    margin_status = "PASS"
    health_score += 1
else:
    margin_status = "FAIL"

revenue_growth = df.iloc[0]["Revenue Growth %"]

if revenue_growth > 0:
    growth_status = "PASS"
    health_score += 1
else:
    growth_status = "FAIL"

cash = info.get("totalCash", 0)
debt = info.get("totalDebt", 0)

if cash > debt:
    debt_status = "PASS"
    health_score += 1
else:
    debt_status = "FAIL"

content.append(
    Paragraph(
        f"Current Price: ₹{info.get('currentPrice','N/A')}",
        styles["BodyText"]
    )
)

current_price = info.get("currentPrice", 0)

if current_price:

    dcf_upside = (
        (dcf_fair_value - current_price)
        / current_price
    ) * 100

else:

    dcf_upside = 0

content.append(
    Paragraph(
        f"Price To Book: {info.get('priceToBook','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Enterprise Value: ₹{info.get('enterpriseValue',0)/1000000000000:.2f} Trillion",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Forward PE: {info.get('forwardPE','N/A')}",
        styles["BodyText"]
    )
)
content.append(
    Paragraph(
        f"Current Price: ₹{info.get('currentPrice','N/A')}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"DCF Upside / Downside: {dcf_upside:.2f}%",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Recommendation Key: {info.get('recommendationKey','N/A')}",
        styles["BodyText"]
    )
)

content.append(Spacer(1, 20))




content.append(
    Paragraph(
        "Company Overview",
        styles["Heading2"]
    )
)

company_summary = info.get(
    "longBusinessSummary",
    "No company description available."
)

content.append(
    Paragraph(
        company_summary[:300] + "...",
        styles["Normal"]
    )
)
content.append(Spacer(1, 20))

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "SWOT Analysis",
        styles["Heading2"]
    )
)

swot = """
<b>Strengths</b><br/>
• Market leader in Indian IT<br/>
• High ROE and margins<br/><br/>

<b>Weaknesses</b><br/>
• Slower growth than mid-cap IT firms<br/>
• Premium valuation<br/><br/>

<b>Opportunities</b><br/>
• AI transformation demand<br/>
• Cloud migration growth<br/><br/>

<b>Threats</b><br/>
• Global recession<br/>
• Currency volatility<br/>
"""
content.append(
    Paragraph(swot, styles["BodyText"])
)


content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Investment Thesis",
        styles["Heading2"]
    )
)

thesis = """
• Market leader in Indian IT Services<br/>
• Strong ROE and healthy profit margins<br/>
• Consistent revenue growth over time<br/>
• Strong cash position and manageable debt<br/>
• Attractive valuation relative to growth
"""

content.append(
    Paragraph(
        thesis,
        styles["BodyText"]
    )
)
content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Key Risks",
        styles["Heading2"]
    )
)

risks = """
• Slowdown in global IT spending<br/>
• US recession affecting client budgets<br/>
• AI disruption to traditional IT services<br/>
• Currency fluctuation risks<br/>
• Competition from Accenture, Infosys and Wipro
"""

content.append(
    Paragraph(
        risks,
        styles["BodyText"]
    )
)
growth_rate = 10

fair_value = info.get("trailingEps",0) * growth_rate

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Peter Lynch Valuation",
        styles["Heading2"]
    )
)
content.append(
    Paragraph(
        f"Upside / Downside: {upside:.2f}%",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Estimated Fair Value: ₹{fair_value:.2f}",
        styles["BodyText"]
    )
)
current_price = info.get("currentPrice",0)

if current_price < fair_value:
    rating = "BUY"
elif current_price < fair_value * 1.2:
    rating = "HOLD"
else:
    rating = "SELL"

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Investment Recommendation",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Rating: {rating}",
        styles["BodyText"]
    )
)

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Analyst Consensus",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Wall Street Consensus: {recommendation.upper()}",
        styles["BodyText"]
    )
)

recommendation = info.get(
    "recommendationKey",
    "N/A"
).upper()

content.append(
    Paragraph(
        f"Street Rating: {recommendation}",
        styles["BodyText"]
    )
)

content.append(Spacer(1,20))
tcs_pe = info.get("trailingPE", 0)
content.append(
    Paragraph(
        "Relative Valuation",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"TCS PE: {tcs_pe:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Peer Average PE: {average_peer_pe:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Valuation Status: {valuation_status}",
        styles["BodyText"]
    )
)

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Peer Comparison",
        styles["Heading2"]
    )
)

peer_table_data = [
    ["Company", "Market Cap", "PE", "ROE"]
]

peer_table_data.extend(peer_data)

peer_table = Table(peer_table_data)

peer_table.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('GRID',(0,0),(-1,-1),1,colors.black)
]))

peer_pe_list = []

for peer in peer_tickers:

    peer_stock = yf.Ticker(peer)
    peer_info = peer_stock.info

    peer_pe = peer_info.get("trailingPE", 0)

    if peer_pe:
        peer_pe_list.append(peer_pe)

        average_peer_pe = sum(peer_pe_list) / len(peer_pe_list)

tcs_pe = info.get("trailingPE", 0)

if tcs_pe < average_peer_pe:
    valuation_status = "UNDERVALUED"
else:
    valuation_status = "OVERVALUED"

content.append(peer_table)

content.append(Spacer(1,20))

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Financial Health Scorecard",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"ROE: {roe_status}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Profit Margin: {margin_status}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Revenue Growth: {growth_status}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Debt Position: {debt_status}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Overall Score: {health_score}/4",
        styles["Heading3"]
    )
)

content.append(Spacer(1,20))


content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Trend Analysis",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Revenue Growth (Multi-Year): {revenue_growth_total:.2f}%",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Average Profit Margin: {avg_margin:.2f}%",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Overall Trend Rating: {trend_rating}",
        styles["BodyText"]
    )
)

content.append(Spacer(1,20))

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Investment Scorecard",
        styles["Heading2"]
    )
)

content.append(
    Paragraph(
        f"Financial Health Score: {health_score}/4",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Trend Analysis: {trend_rating}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Peter Lynch Fair Value: ₹{lynch_fair_value:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"DCF Fair Value: ₹{dcf_fair_value:.2f}",
        styles["BodyText"]
    )
)

content.append(
    Paragraph(
        f"Overall Investment Score: {investment_score}/7",
        styles["Heading3"]
    )
)

content.append(
    Paragraph(
        f"FINAL RATING: {final_rating}",
        styles["Heading1"]
    )
)

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Financial Performance",
        styles["Heading2"]
    )
)

table_data = [
    [
        "Year",
        "Revenue",
        "Net Income",
        "Profit Margin %",
        "Revenue Growth %"
    ]
]

for year in df.index:

    table_data.append([
        str(year.date()),
        f"₹{df.loc[year,'Revenue']/10000000:,.0f} Cr",
        f"₹{df.loc[year,'Net Income']/10000000:,.0f} Cr",
        f"{df.loc[year,'Profit Margin %']:.2f}",
        f"{df.loc[year,'Revenue Growth %']:.2f}"
    ])

table = Table(table_data)

table.setStyle(
    TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
)

content.append(table)

content.append(PageBreak())




content.append(
    Paragraph(
        "5 Year Stock Price Chart",
        styles["Heading2"]
    )
)

content.append(
    Image(chart_file, width=500, height=300)
)

content.append(PageBreak())

content.append(
    Paragraph(
        "Revenue Trend",
        styles["Heading2"]
    )
)

content.append(
    Image(
        revenue_chart_file,
        width=450,
        height=250
    )
)

content.append(Spacer(1,20))

content.append(
    Paragraph(
        "Net Income Trend",
        styles["Heading2"]
    )
)

content.append(
    Image(
        net_income_chart_file,
        width=450,
        height=250
    )
)


target_price = (
    dcf_fair_value + lynch_fair_value
) / 2


pdf.build(content)

print("Investment Banking Tear Sheet Created Successfully!")