import sys
sys.setrecursionlimit(100000000)
memo = {}
coins = [1,2,5]
amount = 11

def find_coins(coins, value):
    if value not in memo:
        if value == 0:
            return 1
        total = 0
        for coin in coins:
            if value > min(coins):
                total += find_coins(coins, value - coin)
            memo[value] = total
    return memo[value]

total = find_coins(coins, amount)
print(total)
print(f"{coins} coins can be used to make {amount}")
