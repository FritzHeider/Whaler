from colorama import Fore, Style

def cease_automatic_trading(value_in_eth):
    """Cease or adjust trading based on whale transaction"""
    if value_in_eth > 1000:
        print(Fore.MAGENTA + "Ceasing trading due to whale activity!" + Style.RESET_ALL)
        # Call your trading bot's stop function or modify trade parameters
        trading_bot.stop_trading()  # Placeholder
    elif value_in_eth > 10:
        print(Fore.MAGENTA + "Adjusting trading strategy based on significant transactions." + Style.RESET_ALL)
        # Adjust the trading algorithm dynamically
        trading_bot.modify_strategy()  # Placeholder