import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import openai
def generate_customized_plan(debt_data, income_data, timeline_data):
    prompt = f"Create a debt repayment plan for me with the following details: I have a  {debt_data['Type of Debt']} with a principal amount of ${debt_data['Principal Amount']} at an interest rate of {debt_data['Interest Rate']}%, minimum monthly payments of ${debt_data['Minimum Payments']}. Current monthly income is ${income_data['Income']}, monthly expenses include {income_data['Expenses']}, and savings amount is ${income_data['Savings']}. The debt was borrowed on {timeline_data['Loan Borrowed Date']} and the goal is to be debt-free by {timeline_data['Debt Repayment Goal']}."

    response = openai.Completion.create(
        engine="text-davinci-003",  # You can experiment with different engines
        prompt=prompt,
        max_tokens=300  # You can adjust the max tokens based on your preference
    )

    return response.choices[0].text.strip()
# Function to calculate the remaining balance for each debt
def calculate_remaining_balance(principal, interest_rate, monthly_payment, months):
    monthly_interest_rate = interest_rate / 12 / 100
    remaining_balance = []
    for month in range(1, months + 1):
        interest_payment = principal * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        principal -= principal_payment
        remaining_balance.append(principal)
    return remaining_balance

# Function to create a debt payoff plan
def create_debt_plan(debt_details, income, expenses, savings, goal_date):
    st.subheader("Debt Payoff Plan")

    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    goal_date = datetime.datetime.combine(goal_date, datetime.datetime.min.time())
    months_to_goal = (goal_date - today).days // 30 if goal_date > today else 0

    total_monthly_expenses = sum(expenses.values())
    available_income = income - total_monthly_expenses

    st.write(f"Monthly Income: ${income}")
    st.write(f"Monthly Expenses: ${total_monthly_expenses}")
    st.write(f"Available Income: ${available_income}")

    debt_summary = pd.DataFrame(debt_details)
    debt_summary['Remaining Balance'] = 0.0

    for index, row in debt_summary.iterrows():
        remaining_balance = calculate_remaining_balance(
            row['Principal Amount'], row['Interest Rate'],
            row['Minimum Payments'], months_to_goal
        )
        debt_summary.at[index, 'Remaining Balance'] = remaining_balance[-1]

    st.write("Debt Details:")
    st.write(debt_summary)

    total_minimum_payment = debt_summary['Minimum Payments'].sum()
    remaining_money = available_income - total_minimum_payment

    if remaining_money > 0:
        st.success("You have money available for debt repayment.")
    # else:
        # st.warning("Warning! Your minimum payments exceed your available income. Adjust your expenses or consider additional income sources.")
# Streamlit app
    customized_plan = generate_customized_plan(debt_data, income_data, timeline_data)

    # Display the customized plan
    st.subheader("Customized Debt Payoff Plan")
    st.write(customized_plan)
st.title("Debt Payoff Planner")

# Input for Debt Details
st.sidebar.header("Debt Details")
type_of_debt = st.sidebar.text_input("Type of Debt", "")
principal_amount = st.sidebar.number_input("Principal Amount", 0.0, None, 0.0)
interest_rate = st.sidebar.number_input("Interest Rate (%)", 0.0, None, 0.0)
min_payments = st.sidebar.number_input("Minimum Payments", 0.0, None, 0.0)

# Input for Current Financial Situation
st.sidebar.header("Current Financial Situation")
income = st.sidebar.number_input("Income", 0.0, None, 0.0)
expenses_input = st.sidebar.text_area("Monthly Expenses (key1: value1, key2: value2, ...)", "")
savings = st.sidebar.number_input("Savings", 0.0, None, 0.0)

# Input for Timeline
st.sidebar.header("Timeline")
current_date = st.sidebar.date_input("Current Date", datetime.date.today())
loan_date = st.sidebar.date_input("Loan Borrowed Date", datetime.date.today())
debt_goal_date = st.sidebar.date_input("Debt Repayment Goal", datetime.date.today())

# Button to create debt payoff plan
if st.sidebar.button("Create Debt Payoff Plan"):
    expenses_dict = {}
    if expenses_input:
        expenses_list = [item.strip() for item in expenses_input.split(',')]
        for item in expenses_list:
            parts = [part.strip() for part in item.split(':')]
            if len(parts) == 2:
                key, value = parts
                expenses_dict[key] = float(value)
            # else:
            #     st.warning(f"Ignored invalid input: {item}")

    debt_data = {
        'Type of Debt': type_of_debt,
        'Principal Amount': principal_amount,
        'Interest Rate': interest_rate,
        'Minimum Payments': min_payments
    }

    income_data = {
        'Income': income,
        'Expenses': expenses_dict,
        'Savings': savings
    }

    timeline_data = {
        'Current Date': current_date,
        'Loan Borrowed Date': loan_date,
        'Debt Repayment Goal': debt_goal_date
    }

    create_debt_plan([debt_data], income, expenses_dict, savings, debt_goal_date)
    
