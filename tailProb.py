import math

'''
Want to compute 2(n!)^n / n^2 !
'''

def factorial(n):
    total = 1
    for i in range(n):
        total *= (i+1)

    return total

def numZeroes(n):
    total = 0
    while n > 10:
        n /= 10
        total += 1

    return total

def main(k):
    numerator = 2 * pow(factorial(k), k)
    numerZeroes = numZeroes(numerator)

    denominator = factorial(pow(k, 2))
    denomZeroes = numZeroes(denominator)

    difZeroes = denomZeroes - numerZeroes

    print(str(k) + ": " + str(difZeroes))


for i in range(10):
    main(i+1)