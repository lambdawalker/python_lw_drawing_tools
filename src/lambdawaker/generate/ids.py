import secrets
import string


def generate_random_mrz():
    alpha_num = string.ascii_uppercase + string.digits
    numeric = string.digits

    # 1. Generate Data Segments within their specific ranges
    seg1 = ''.join(secrets.choice(alpha_num) for _ in range(secrets.randbelow(5) + 24))  # 24-28
    seg2 = ''.join(secrets.choice(alpha_num) for _ in range(secrets.randbelow(5) + 16))  # 16-20
    seg3 = ''.join(secrets.choice(numeric) for _ in range(secrets.randbelow(3) + 1))  # 1-3
    seg4 = ''.join(secrets.choice(alpha_num) for _ in range(secrets.randbelow(5) + 4))  # 4-8
    seg5 = ''.join(secrets.choice(alpha_num) for _ in range(secrets.randbelow(5) + 4))  # 4-8
    seg6 = ''.join(secrets.choice(alpha_num) for _ in range(secrets.randbelow(5) + 4))  # 4-8

    segments = [seg1, seg2, seg3, seg4, seg5, seg6]
    current_data_len = sum(len(s) for s in segments)

    # 2. Calculate remaining length for the 6 separators
    # (Note: Format ends with a separator, so there are 6 segments and 6 separators)
    target_total = 90
    sep_budget = target_total - current_data_len

    # Distribute the budget among 6 separators (minimum 1 char each)
    sep_lengths = [1] * 6
    remaining_sep_chars = sep_budget - 6

    for _ in range(remaining_sep_chars):
        idx = secrets.randbelow(6)
        sep_lengths[idx] += 1

    # 3. Assemble the final string
    result = ""
    for i in range(6):
        result += segments[i]
        result += "<" * sep_lengths[i]

    return result


if __name__ == "__main__":
    print(generate_random_mrz())
