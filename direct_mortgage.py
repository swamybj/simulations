import numpy as np

# Initial Variables for Real Estate
purchase_price = 400000
down_payment = 0.20 * purchase_price
loan_amount = purchase_price - down_payment
initial_interest_rate = 0.05
interest_rate_decrease = 0.005  # 50 bps
hoa = 80
insurance = 120
property_tax_rate = 0.012
maintenance_rate = 0.01
initial_rent = 2400
rent_increase_rate = 0.05  # 5% increase every 2 years
buying_closing_costs = 8000
agent_commission = 0.05
appreciation_rate = 0.048

# Initial Variables for Index Fund
initial_investment = down_payment + buying_closing_costs
annual_return_rate = 0.07


# Function to calculate monthly mortgage payment
def calculate_mortgage_payment(principal, annual_rate, months):
    monthly_rate = annual_rate / 12
    payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** -months)
    return payment


# Mortgage Payment and Interest Rate Calculation
monthly_payments = []
interest_rate = initial_interest_rate
remaining_months = 360

for quarter in range(8):
    if quarter > 0:
        interest_rate -= interest_rate_decrease
    monthly_payment = calculate_mortgage_payment(loan_amount, interest_rate, remaining_months)
    monthly_payments.append(monthly_payment)
    remaining_months -= 3

remaining_payment = calculate_mortgage_payment(loan_amount, interest_rate, remaining_months)
monthly_payments += [remaining_payment] * (10 * 12 - len(monthly_payments))

# Calculate Cash Flows for Real Estate
years = 10
cash_flows_real_estate = []
property_values = []
rents = [initial_rent * (1 + rent_increase_rate) ** (i // 2) for i in range(years)]
property_value = purchase_price

for year in range(years):
    annual_rent = rents[year] * 12
    annual_mortgage_payment = sum(monthly_payments[year * 12: (year + 1) * 12])
    annual_hoa = hoa * 12
    annual_insurance = insurance * 12
    annual_property_tax = property_value * property_tax_rate
    annual_maintenance = property_value * maintenance_rate

    total_annual_expenses = annual_mortgage_payment + annual_hoa + annual_insurance + annual_property_tax + annual_maintenance
    net_cash_flow = annual_rent - total_annual_expenses

    property_value *= (1 + appreciation_rate)
    property_values.append(property_value)
    cash_flows_real_estate.append(net_cash_flow)

# Calculate Selling Profit
selling_prices = [value - (value * agent_commission) for value in property_values]
remaining_mortgage_balances = [loan_amount - sum(monthly_payments[:year * 12]) for year in range(1, years + 1)]

real_estate_profits = [
    net_cash_flow + (selling_price - remaining_mortgage_balance)
    for net_cash_flow, selling_price, remaining_mortgage_balance in
    zip(cash_flows_real_estate, selling_prices, remaining_mortgage_balances)
]

# Calculate Investment Growth for Index Funds
index_fund_values = [initial_investment * (1 + annual_return_rate) ** year for year in range(1, years + 1)]

# Compare Results
comparison = list(zip(range(1, years + 1), real_estate_profits, index_fund_values))

print(comparison)
