#!/usr/bin/env python3
import sys

def check_bug1():
    try:
        from bug1 import divide_numbers
        result = divide_numbers(10, 0)
        print(f"BUG1: PASS - No ZeroDivisionError (got {result})")
        return True
    except ZeroDivisionError:
        print("BUG1: FAIL - ZeroDivisionError detected")
        return False
    except Exception as e:
        print(f"BUG1: ERROR - {e}")
        return False

def check_bug2():
    try:
        from bug2 import get_user_data
        result = get_user_data({"key": "value"}, "nonexistent")
        print(f"BUG2: PASS - No KeyError (got {result})")
        return True
    except KeyError:
        print("BUG2: FAIL - KeyError detected")
        return False
    except Exception as e:
        print(f"BUG2: ERROR - {e}")
        return False

def check_bug3():
    try:
        from bug3 import parse_number
        result = parse_number("not_a_number")
        print(f"BUG3: PASS - No ValueError (got {result})")
        return True
    except ValueError:
        print("BUG3: FAIL - ValueError detected")
        return False
    except Exception as e:
        print(f"BUG3: ERROR - {e}")
        return False

if __name__ == "__main__":
    all_pass = True
    all_pass &= check_bug1()
    all_pass &= check_bug2()
    all_pass &= check_bug3()
    
    if all_pass:
        print("\nAll checks PASSED")
        sys.exit(0)
    else:
        print("\nSome checks FAILED")
        sys.exit(1)
