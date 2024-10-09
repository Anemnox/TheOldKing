# Define the total width of the line
total_width = 80

# Define the width for each part
left_width = 20
right_width = total_width - left_width  # This ensures the total width is maintained

# Example strings
left_text = "Hello"
right_text = "World"

# Format using f-strings
formatted_string = f"{left_text:<{left_width}}{right_text:>{right_width}}"

#print(f"{formatted_string}")


class Test:
    def __init__(self, name) -> None:
        self.name = name
    
    def __eq__(self, other):
        if isinstance(other, Test):
            return str(self) == str(other)
        return None
    
    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"\33[33m{self.name}"


def get_deck_map(array):
    deck_map = {}
    for c in array:
        print(c.__hash__())
        if c in deck_map:
            deck_map[c] += 1
        else:
            deck_map[c] = 1
    return deck_map


list_test = [Test("1"), Test("1"), Test("2"), Test("1"), Test("2")]

print()
print(Test("a") == Test("a"))
print(get_deck_map(list_test))