# Named constant mapping for kinetic parameters
# ponytail: Simple static dictionary mapping. If scaling or dynamic decay modeling is needed, this can be moved to a database or config file.
KINETIC_PARAMS = {
    2: {"w_initial": 20.0,  "decay_rate": 10.0},
    3: {"w_initial": 50.0,  "decay_rate": 3.5},
    4: {"w_initial": 100.0, "decay_rate": 1.0},
}

# Score 5 constants: Layer 3 is programmed to never decay or prune infinite weights.
W_INITIAL_CORE = float("inf")
DECAY_RATE_CORE = 0.0

def get_kinetic_params(score: int) -> dict:
    """
    Returns the kinetic parameters (w_initial, decay_rate) for the given score (2-4).
    
    W_current = W_initial - (decay_rate * elapsed_days) is the decay formula Layer 3 will use
    later to determine pruning. Layer 2 only sets the initial values, it does not run decay itself.
    """
    if score in KINETIC_PARAMS:
        return KINETIC_PARAMS[score]
    raise ValueError(f"Invalid score for kinetic params: {score}. Only scores 2, 3, 4 are supported.")
