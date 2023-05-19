class State:
    def __init__(self, state_in_list):
        self.a, self.a_prime, self.h, self.f, self.s = state_in_list

    def __str__(self):
        return "({}, {}, {}, {}, {})".format(
            self.a, self.a_prime, self.h, self.f, self.s
        )

    def retrieve_elements(self):
        return (self.a, self.a_prime, self.h, self.f, self.s)
