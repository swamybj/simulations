def calculate_cumulative_interest_with_additional_investments(principal, annual_interest_rate, years,
                                                              monthly_investment, yearly_contributions,yearly_maintenance):
    # Calculate the monthly interest rate
    monthly_interest_rate = annual_interest_rate / 12
    total_investment=principal
    # Initialize lists to store cumulative interest for each quarter
    cumulative_interest_by_year = []

    for year in range(1, years + 1):
        year_interest = []
        cumulative_interest = 0

        # Add yearly contribution at the beginning of the year, if applicable
        if year <= len(yearly_contributions)+1 and year!=1:
            principal += yearly_contributions[year - 2]
            total_investment+=yearly_contributions[year - 2]
        # yearly maintianance
        principal+=yearly_maintenance
        total_investment += yearly_maintenance


        for month in range(1, 13):
            if month==1 and year>=3 and year%2==1:
                monthly_investment=monthly_investment-100
                if monthly_investment<=0:
                    monthly_investment=1
            interest = principal * monthly_interest_rate
            cumulative_interest += interest
            principal += interest + monthly_investment
            total_investment += monthly_investment

            # Check if it's the end of a quarter
            if month % 3 == 0:
                quarter = month // 3
                year_interest.append({
                    'Year': year,
                    'principal':principal,
                    'Quarter': quarter,
                    'Total Invested':total_investment,
                    'Total Profit':principal-total_investment,
                    'Cumulative Interest Earned': cumulative_interest
                })
        cumulative_interest_by_year.extend(year_interest)

    return cumulative_interest_by_year


def calculate_amortization_schedule(principal, annual_interest_rate, years, payments_per_year,property_price,rent_increase,rental_income,rent_increase_frequency,monthly_additional_payment):
    # Calculate the monthly interest rate and number of payments
    period_interest_rate = annual_interest_rate / payments_per_year
    total_payments = years * payments_per_year


    # Calculate the payment amount using the formula for an annuity
    payment = principal * (period_interest_rate * (1 + period_interest_rate) ** total_payments) / (
                (1 + period_interest_rate) ** total_payments - 1)

    # Initialize lists to store the schedule
    schedule = []
    remaining_principal = principal
    cumulative_principal_paid = 0
    cumulative_interest_paid = 0
    cumulative_out_of_pocket = 0
    rent_increase_temp = 0
    for i in range(1, total_payments + 1):
        property_estimated_price = property_price * ((1 + 0.048) ** int(i/12)) * (0.95)
        print(i,rent_increase_temp)
        interest_payment = remaining_principal * period_interest_rate
        principal_payment = payment - interest_payment
        remaining_principal -= principal_payment

        # Update cumulative amounts
        cumulative_principal_paid += principal_payment
        cumulative_interest_paid += interest_payment
        cumulative_out_of_pocket += payment+monthly_additional_payment-(rental_income+rent_increase_temp)
        if i % (rent_increase_frequency*12) == 0:
            rent_increase_temp = rent_increase_temp + rent_increase
        # Append the details of this payment to the schedule
        schedule.append({
            'Payment Number': i,
            'Property_price':property_price,
            'Estimated Property Price after  agent commision':property_estimated_price,
            'Year':int(i/12)+1,
            'loan_amount':principal,
            'annual_interest_rate':annual_interest_rate,
            'tenor':years,
            'Payment Amount': payment,
            'Rental Income': rental_income+rent_increase_temp,
            'Monthly Tax_HO_Insurance':monthly_additional_payment,
            'Out of Pocket':payment+monthly_additional_payment-(rental_income+rent_increase_temp),
            'Cumulative Out of Pocket': cumulative_out_of_pocket,
            'Principal Paid': principal_payment,
            'Interest Paid': interest_payment,
            'Remaining Principal': remaining_principal,
            'Cumulative Principal Paid': cumulative_principal_paid,
            'Cumulative Interest Paid': cumulative_interest_paid
        })

    return schedule

def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return f'{val}'
    return my_format

# Example usage
property_price=400000
down_payment_rate=20
down_payment=property_price*down_payment_rate/100
principal = property_price-down_payment  # Loan amount
annual_interest_rate = 0.075  # Annual interest rate (4%)
years = 30  # Loan term in years
payments_per_year = 12  # Monthly payments
ref_counts=3
ref_rate_diff=0.01
interval=12
rent_estimate=0.06
rent_increase_frequency=2
rent_increase=100
rental_management_fee_rate=10
closing_cost=10000
ref_closing_cost=5000
appraisal_cost=550
points_rate=1
hoa=75
property_tax=1.2
home_insurance=120

investment_principal = down_payment  # Initial investment
mm_rate = 0.06  # Annual interest rate (5%)
years =30  # Investment period in years
yearsChange=15
monthly_investment = 100  # Additional monthly investment
yearly_contributions = [5000, 5000, 5000]  # Additional yearly contributions for the next 3 years


# additional monthly or yearly cost
monthly_additional_payment=hoa+home_insurance+(property_price*property_tax/1200)
yearly_maintenance=1200

#rental income
rental_income=property_price*rent_estimate*rental_management_fee_rate/100


schedule_dict={}
# schedule = calculate_amortization_schedule(principal, annual_interest_rate, years, payments_per_year)
annual_interest_rate_change=annual_interest_rate
annual_interest_rate_term_change=annual_interest_rate
for i in range(ref_counts+1):
    print(i)
    if i==0:
        schedule = calculate_amortization_schedule(principal, annual_interest_rate, years,
                                                   payments_per_year,property_price,rent_increase,
                                                   rental_income,rent_increase_frequency,monthly_additional_payment)
        schedule_dict['BASE'] = schedule
    else:
        annual_interest_rate_change=annual_interest_rate_change-ref_rate_diff
        print(i,annual_interest_rate_change)
        schedule = calculate_amortization_schedule(schedule[interval-1]['Remaining Principal'], annual_interest_rate_change, years,
                                                   payments_per_year,property_price,rent_increase,
                                                   schedule[interval-1]['Rental Income'],rent_increase_frequency,monthly_additional_payment)
        schedule_dict['BASE-'+str(i)] = schedule

for i in range(ref_counts + 1):
    print(i)
    if i == 0:
        schedule = calculate_amortization_schedule(principal, annual_interest_rate, years, payments_per_year,
                                                   property_price,rent_increase,rental_income,rent_increase_frequency,monthly_additional_payment)
        schedule_dict['BASE'] = schedule
    else:
        annual_interest_rate_term_change = annual_interest_rate_term_change - (ref_rate_diff*1.25)
        print(i, annual_interest_rate_term_change)
        schedule = calculate_amortization_schedule(schedule[interval - 1]['Remaining Principal'],
                                                   annual_interest_rate_term_change, yearsChange,
                                                   payments_per_year, property_price,rent_increase,
                                                   schedule[interval-1]['Rental Income'],rent_increase_frequency,monthly_additional_payment)
        schedule_dict['BASE-Term-' + str(i)] = schedule


print(schedule_dict['BASE'][0:150])
out_of_pocket=432
schedule = calculate_cumulative_interest_with_additional_investments(investment_principal, mm_rate, years,
                                                                     out_of_pocket, yearly_contributions,yearly_maintenance)

# Print the schedule
for entry in schedule:
    print(entry)

print(schedule[39])
print(schedule_dict['BASE'][119])
print(schedule_dict['BASE-1'][107])
print(schedule_dict['BASE-2'][95])
print(schedule_dict['BASE-3'][83])
print('***********************')
print(schedule[19])
print(schedule_dict['BASE'][59])
print(schedule_dict['BASE-1'][47])
print(schedule_dict['BASE-2'][35])
print(schedule_dict['BASE-3'][23])


import seaborn as sns
import matplotlib.pyplot as plt

profit_after_sale=schedule_dict['BASE'][59]['Estimated Property Price after  agent commision']-schedule_dict['BASE'][59]['Property_price']

# Data
sales_data = [schedule_dict['BASE'][59]['Property_price'],
              schedule_dict['BASE'][59]['Estimated Property Price after  agent commision'],
              schedule_dict['BASE'][59]['Cumulative Out of Pocket']+closing_cost,
              down_payment,
              schedule_dict['BASE'][59]['Cumulative Principal Paid']+profit_after_sale-
              (schedule_dict['BASE'][59]['Cumulative Out of Pocket']+closing_cost),
              schedule_dict['BASE'][59]['Payment Amount']
              ]
products = ['property_price', 'FV_5Yrs', 'Expenses', 'InVested Amount','Estimated Profit','EMI']

# Explode Shoes slice
explode = [0, 0, 0, 0, 0.1, 0]

# Explode Shoes slice
explode2 = [0, 0, 0.1]


# Create pie chart
# plt.pie(sales_data, labels=products, explode=explode)

# Show plot
# plt.show()

from matplotlib import pyplot as plt
import numpy as np

fig, axs = plt.subplots(3, 2)

alt_inv_data=[schedule[19]['Total Invested'],schedule[19]['Total Profit'],schedule[19]['Total Profit']*0.15]
alt_products = ['Invested Amount', 'Profit after 5 Yres','Estimated Taxes']
# First pie chart
axs[0, 0].pie(alt_inv_data, labels=alt_products, explode=explode2, autopct=autopct_format(alt_inv_data))
axs[0, 0].set_title('Alternative investement in Indexes @6%')

# Fourth pie chart
axs[0, 1].pie(sales_data, labels=products, explode=explode, autopct=autopct_format(sales_data))
axs[0, 1].set_title('Property @7.5%')

sales_data = [schedule_dict['BASE'][59]['Property_price'],
              schedule_dict['BASE'][59]['Estimated Property Price after  agent commision'],
              schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-1'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-2'][35]['Cumulative Out of Pocket']
              +closing_cost,
              down_payment,
              schedule_dict['BASE'][11]['Cumulative Principal Paid']+schedule_dict['BASE-1'][11]['Cumulative Principal Paid']+schedule_dict['BASE-2'][35]['Cumulative Principal Paid']+profit_after_sale-
              (schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-1'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-2'][35]['Cumulative Out of Pocket']+closing_cost),
              schedule_dict['BASE'][59]['Payment Amount']
              ]



# Second pie chart
axs[1, 1].pie(sales_data, labels=products, explode=explode, autopct=autopct_format(sales_data))
axs[1, 1].set_title('Property @7.5% - 100bps Refinanced Twice in next 2 years')

sales_data = [schedule_dict['BASE'][59]['Property_price'],
              schedule_dict['BASE'][59]['Estimated Property Price after  agent commision'],
              schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-1'][47]['Cumulative Out of Pocket']
              +closing_cost,
              down_payment,
              schedule_dict['BASE'][11]['Cumulative Principal Paid']+schedule_dict['BASE-1'][47]['Cumulative Principal Paid']+profit_after_sale-
              (schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-1'][47]['Cumulative Out of Pocket']+closing_cost),
              schedule_dict['BASE'][59]['Payment Amount']
              ]
# Third pie chart
axs[1, 0].pie(sales_data, labels=products, explode=explode, autopct=autopct_format(sales_data))
axs[1, 0].set_title('Property @7.5% - 100bps Refinance after 1 year')

sales_data = [schedule_dict['BASE'][59]['Property_price'],
              schedule_dict['BASE'][59]['Estimated Property Price after  agent commision'],
              schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-Term-1'][47]['Cumulative Out of Pocket']
              +closing_cost,
              down_payment,
              schedule_dict['BASE'][11]['Cumulative Principal Paid']+schedule_dict['BASE-Term-1'][47]['Cumulative Principal Paid']+profit_after_sale-
              (schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-Term-1'][47]['Cumulative Out of Pocket']+closing_cost),
              schedule_dict['BASE'][59]['Payment Amount']
              ]

# Third pie chart
axs[2, 1].pie(sales_data, labels=products, explode=explode, autopct=autopct_format(sales_data))
axs[2, 1].set_title('Property @7.5% - 125bps + 15 yrs Term Refinanced after 1 year')

sales_data = [schedule_dict['BASE'][59]['Property_price'],
              schedule_dict['BASE'][59]['Estimated Property Price after  agent commision'],
              schedule_dict['BASE'][11]['Cumulative Out of Pocket']+
              schedule_dict['BASE-Term-1'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-Term-2'][35]['Cumulative Out of Pocket']
              +closing_cost,
              down_payment,
              schedule_dict['BASE'][11]['Cumulative Principal Paid']+schedule_dict['BASE-Term-1'][11]['Cumulative Principal Paid']
              +schedule_dict['BASE-Term-2'][35]['Cumulative Principal Paid']+profit_after_sale-
              (schedule_dict['BASE'][11]['Cumulative Out of Pocket']+schedule_dict['BASE-Term-1'][11]['Cumulative Out of Pocket']+
               schedule_dict['BASE-Term-2'][35]['Cumulative Out of Pocket']+closing_cost),
              schedule_dict['BASE'][59]['Payment Amount']
              ]

# Third pie chart
axs[2, 0].pie(sales_data, labels=products, explode=explode, autopct=autopct_format(sales_data))
axs[2, 0].set_title('Property @7.5% - 125bps + 15 yrs Term Refinanced Twice in next 2 years')

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plot
plt.show()