import numpy as np

# Parameters
num_simulations = 10000
mean_return = 0.05
volatility = 0.2
initial_portfolio_value = 1000000
confidence_level = 0.95

# Simulate returns
simulated_returns = np.random.normal(mean_return, volatility, num_simulations)

# Calculate portfolio values and losses
portfolio_values = initial_portfolio_value * (1 + simulated_returns)
losses = initial_portfolio_value - portfolio_values

# Sort losses
losses_sorted = np.sort(losses)

# Determine VaR
var_index = int((1 - confidence_level) * num_simulations)
var_value = losses_sorted[var_index]

# Calculate CVaR
cvar = losses_sorted[var_index:].mean()

print(f"VaR at {confidence_level * 100}% confidence level: {var_value}")
print(f"CVaR at {confidence_level * 100}% confidence level: {cvar}")
