class Pool_in_forks:
    # init
    def __init__(self, variable_name):
        self.known_shares, self.unknown_shares = [], []
        self.variable_name = variable_name
        if "winner" in self.variable_name:
            self.role = "winner"
        elif "loser" in self.variable_name:
            self.role = "loser"

    def insert_pool_shares(self, row, names_in_share, pool_shares):
        role = self.role
        if row[role + "_id"] in names_in_share:
            self.known_shares.append(
                get_closest_shares(
                    row[role + "_id"],
                    row[role + "_timestamp"],
                    pool_shares,
                )
            )
        else:
            self.unknown_shares.append(row[role + "_id"])
            self.unknown_shares.append(0.01)

    def append(self, pool_name):
        self.names_in_fork.append(pool_name)

    def generate_knownness_ratio(self):
        self.num_of_all = len(self.known_shares) + len(self.unknown_shares)
        self.all_shares = self.known_shares + self.unknown_shares

        self.known_ratio = len(self.known_shares) / self.num_of_all
        self.unknown_ratio = len(self.unknown_shares) / self.num_of_all

    def __str__(self):
        return "total: {}\n{}:\n\tknown ratio: {}\n\tunknow ratio: {}".format(
            self.num_of_all,
            self.variable_name,
            self.known_ratio,
            self.unknown_ratio,
        )
