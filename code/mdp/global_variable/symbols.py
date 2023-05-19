INACTIVE, ACTIVE = 0, 1

SETTLED, UNSETTLED = 0, 1

ADOPT, OVERRIDE, WAIT, = (
    0,
    1,
    2,
)

UNDERPAYING = 0
OVERPAYING = 1

states = {0: "INACTIVE", 1: "ACTIVE"}
actions = {0: "ADOPT", 1: "OVERRIDE", 2: "WAIT"}
actions_lib = [ADOPT, OVERRIDE, WAIT]
settlement_values = [SETTLED, UNSETTLED]
