def calculate_average(numbers):
    # Fix: Guard clause to handle empty list and prevent ZeroDivisionError
    if not numbers:
        return 0
        
    total = 0
    for num in numbers:
        total += num
        
    return total / len(numbers)
# function
def main():
    data = []
    result = calculate_average(data)
    print(f"Average: {result}")

if __name__ == "__main__":
    main()