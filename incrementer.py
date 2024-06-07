import random
import math


def generate_random_with_initial(initial):
    print('***********'+str(initial))
    return random.randint(initial, 2 ** initial)


def check_and_increment(input_value, initial=1, counter=2):
    print((input_value, initial))


    random_number = generate_random_with_initial(initial)

    if input_value == random_number:
        print('you Win '+str(input_value))
        counter += random_number
        print('Your wallet amount is ' + str(counter))
        input_value = int(input("Enter another input bigger than "+str(random_number)+" and lesser than "+str(2**(random_number+1))))
        check_and_increment(input_value, initial=(random_number+1),counter=counter)
    else:
        print('you lost!!! your number is '+str(input_value)+' not matching with your winning amount  '+str(random_number))
        print('Your wallet amount is '+str(counter))

# Test the function with a sample input value
input_value = int(input("Enter an input value between 1 & 2: "))
check_and_increment(input_value)
