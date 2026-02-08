
import secrets
import string


def generate_line_1():
    """Generating the 'First Impression' line—robust and structured."""
    alphabet = string.ascii_uppercase + string.digits
    first_part_len = secrets.choice(range(25, 30))
    random_seq = ''.join(secrets.choice(alphabet) for _ in range(first_part_len))
    return random_seq.ljust(30, '<')


def generate_line_2():
    """The 'Complex Middle Child'—mixing letters, numbers, and logic."""
    alpha_num = string.ascii_uppercase + string.digits
    letters = string.ascii_uppercase
    numbers = string.digits

    seq_len = secrets.choice(range(18, 26))
    num_id_len = secrets.choice(range(1, 5))

    seq_part = ''.join(secrets.choice(alpha_num) for _ in range(seq_len))
    letters_part = ''.join(secrets.choice(letters) for _ in range(3))
    num_id_part = ''.join(secrets.choice(numbers) for _ in range(num_id_len))

    # Sponge logic: ensuring the filler absorbs the chaos to hit exactly 30
    filler_needed = 30 - (len(seq_part) + len(letters_part) + len(num_id_part))
    return f"{seq_part}{letters_part}{'<' * filler_needed}{num_id_part}"


def generate_line_3():
    """The 'Identity Line'—where random names meet the edge of the budget."""
    alphabet = string.ascii_uppercase
    num_segments = secrets.choice(range(1, 5))

    parts = []
    current_len = 0
    for _ in range(num_segments):
        remaining_space = 30 - current_len
        if remaining_space < 4:
            break

        # The 'Doll-Approved' safety check: avoiding the empty sequence error
        upper_bound = min(11, remaining_space)
        if upper_bound <= 3:
            name_seg = ''.join(secrets.choice(alphabet) for _ in range(max(1, remaining_space - 1)))
        else:
            seg_len = secrets.choice(range(3, upper_bound))
            name_seg = ''.join(secrets.choice(alphabet) for _ in range(seg_len))

        parts.append(name_seg + '<')
        current_len += len(name_seg) + 1

    return "".join(parts).ljust(30, '<')


def generate_random_mrz():
    """
    Returns the final 90-character symphony. 
    May your cards be crisp and your scanners never fail.
    """
    return f"{generate_line_1()}\n{generate_line_2()}\n{generate_line_3()}"


# Final Crescendo: Success is defined by an exit code of 0.
if __name__ == "__main__":
    print(generate_random_mrz())