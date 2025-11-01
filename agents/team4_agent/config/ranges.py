"""
U2 Agent - Preflop Hand Ranges

Standard poker hand ranges for different positions and situations.
Based on GTO principles but adapted for exploitative play.
"""

# Premium hands (top ~5% of hands)
PREMIUM_HANDS = {
    "AA", "KK", "QQ", "JJ", "TT",
    "AKs", "AQs", "AJs", "AKo"
}

# Strong hands (top ~10-12% of hands)
STRONG_HANDS = {
    "99", "88", "77",
    "ATs", "KQs", "KJs", "QJs", "JTs",
    "AQo", "AJo", "KQo"
}

# Value hands (playable from good position)
VALUE_HANDS = {
    "66", "55", "44", "33", "22",
    "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
    "KTs", "K9s", "QTs", "Q9s", "T9s", "98s", "87s", "76s", "65s",
    "ATo", "KJo", "KTo", "QJo", "QTo", "JTo"
}

# Speculative hands (suited connectors, small pairs)
SPECULATIVE_HANDS = {
    "T8s", "97s", "86s", "75s", "64s", "54s",
    "J9s", "T9s", "98s", "87s", "76s", "65s", "54s",
}

# Opening ranges by position (5-max)
OPENING_RANGES = {
    "UTG": PREMIUM_HANDS | STRONG_HANDS | {"66", "55", "A9s", "KTs", "QJs"},
    "HJ": PREMIUM_HANDS | STRONG_HANDS | {"66", "55", "44", "A9s", "A8s", "KTs", "K9s", "QTs", "JTs", "T9s"},
    "CO": PREMIUM_HANDS | STRONG_HANDS | VALUE_HANDS,
    "BTN": PREMIUM_HANDS | STRONG_HANDS | VALUE_HANDS | SPECULATIVE_HANDS,
    "SB": PREMIUM_HANDS | STRONG_HANDS | {"66", "55", "A9s", "A8s", "KTs", "QJs", "JTs"},
}

# 3-bet ranges by position
THREE_BET_RANGES = {
    "UTG": PREMIUM_HANDS,
    "HJ": PREMIUM_HANDS | {"99", "88", "ATs", "KQs"},
    "CO": PREMIUM_HANDS | {"99", "88", "77", "ATs", "A9s", "KQs", "KJs"},
    "BTN": PREMIUM_HANDS | STRONG_HANDS | {"A9s", "A8s", "A5s", "KTs", "QJs", "JTs", "T9s"},  # Wide button 3-bet
    "SB": PREMIUM_HANDS | {"99", "88", "ATs", "KQs"},
}

def hand_to_notation(cards):
    """
    Convert hand cards to poker notation (e.g., 'AKs', 'QQ', '76o')

    Args:
        cards: List of card strings like ["A♥", "K♠"]

    Returns:
        Hand notation string like "AKs" or "AKo"
    """
    if len(cards) != 2:
        return None

    # Remove suit symbols
    ranks = []
    suits = []
    for card in cards:
        # Handle different suit symbols
        card_clean = card.replace("♠", "").replace("♥", "").replace("♦", "").replace("♣", "")

        # FIX: Convert '10' to 'T' for consistency
        if card_clean == '10':
            card_clean = 'T'

        ranks.append(card_clean)
        # Get suit
        if "♠" in card or "s" in card.lower():
            suits.append("s")
        elif "♥" in card or "h" in card.lower():
            suits.append("h")
        elif "♦" in card or "d" in card.lower():
            suits.append("d")
        elif "♣" in card or "c" in card.lower():
            suits.append("c")
        else:
            suits.append("")

    rank_order = "AKQJT98765432"

    # Sort ranks by strength
    try:
        if rank_order.index(ranks[0]) < rank_order.index(ranks[1]):
            high_rank, low_rank = ranks[0], ranks[1]
        else:
            high_rank, low_rank = ranks[1], ranks[0]
    except ValueError:
        # Invalid rank - return None
        return None

    # Check if pocket pair
    if high_rank == low_rank:
        return high_rank + high_rank

    # Check if suited
    suited = "s" if suits[0] == suits[1] else "o"

    return high_rank + low_rank + suited


def is_hand_in_range(hand_notation, range_set):
    """Check if hand notation is in a given range"""
    if hand_notation is None:
        return False
    return hand_notation in range_set


def get_hand_strength_category(hand_notation):
    """Categorize hand strength for quick decisions"""
    if hand_notation in PREMIUM_HANDS:
        return "premium"
    elif hand_notation in STRONG_HANDS:
        return "strong"
    elif hand_notation in VALUE_HANDS:
        return "value"
    elif hand_notation in SPECULATIVE_HANDS:
        return "speculative"
    else:
        return "weak"


def should_open_from_position(hand_notation, position):
    """Determine if we should open raise from this position"""
    opening_range = OPENING_RANGES.get(position, set())
    return is_hand_in_range(hand_notation, opening_range)


def should_3bet(hand_notation, position):
    """Determine if we should 3-bet from this position"""
    three_bet_range = THREE_BET_RANGES.get(position, set())
    return is_hand_in_range(hand_notation, three_bet_range)
