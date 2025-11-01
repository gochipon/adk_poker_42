"""
U2 Agent - Equity Calculator

Fast equity calculations using Monte Carlo simulation.
Based on proven methods from codex_bot and team_codex_agent.

WITH CACHING for speed optimization.
"""

import random
from typing import List, Tuple
from itertools import combinations
from functools import lru_cache

# Card evaluation helpers
RANKS = "23456789TJQKA"
SUITS = "♠♥♦♣"

# Postflop cache (limited size)
_postflop_cache = {}
_cache_max_size = 200

def parse_card(card_str: str) -> Tuple[str, str]:
    """Parse card string like 'A♥' into rank and suit"""
    # Remove any spaces
    card_str = card_str.strip()
    # Last character is suit, rest is rank
    if len(card_str) >= 2:
        suit = card_str[-1]
        rank = card_str[:-1]

        # FIX: Convert '10' to 'T' for consistency
        if rank == '10':
            rank = 'T'

        return rank, suit
    return None, None


def make_deck(exclude_cards: List[str] = None) -> List[str]:
    """Create a deck of cards, excluding specified cards"""
    deck = [rank + suit for rank in RANKS for suit in SUITS]

    if exclude_cards:
        # Normalize excluded cards
        excluded_set = set()
        for card in exclude_cards:
            rank, suit = parse_card(card)
            if rank and suit:
                excluded_set.add(rank + suit)

        deck = [card for card in deck if card not in excluded_set]

    return deck


def normalize_cards(cards: List[str]) -> List[str]:
    """Normalize card format"""
    normalized = []
    for card in cards:
        rank, suit = parse_card(card)
        if rank and suit:
            normalized.append(rank + suit)
    return normalized


def evaluate_hand_simple(hole_cards: List[str], community: List[str]) -> int:
    """
    Simple hand evaluation for Monte Carlo simulation.
    Returns a score where higher is better.

    This is a simplified evaluator for speed. For production,
    use pokerkit or proper hand evaluator.
    """
    all_cards = hole_cards + community

    # Count ranks and suits
    rank_counts = {}
    suit_counts = {}

    for card in all_cards:
        rank, suit = parse_card(card)
        rank_counts[rank] = rank_counts.get(rank, 0) + 1
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    # Check for flush
    has_flush = any(count >= 5 for count in suit_counts.values())

    # Check for pairs, trips, quads
    counts = sorted(rank_counts.values(), reverse=True)
    max_count = counts[0] if counts else 0

    # Get high card value
    high_card = max([RANKS.index(rank) for rank, _ in [parse_card(c) for c in all_cards]])

    # Simple scoring (not perfect but fast for Monte Carlo)
    if max_count == 4:
        return 8000 + high_card  # Four of a kind
    elif max_count == 3 and len(counts) > 1 and counts[1] >= 2:
        return 7000 + high_card  # Full house
    elif has_flush:
        return 6000 + high_card  # Flush
    elif max_count == 3:
        return 4000 + high_card  # Three of a kind
    elif max_count == 2 and len(counts) > 1 and counts[1] == 2:
        return 3000 + high_card  # Two pair
    elif max_count == 2:
        return 2000 + high_card  # One pair
    else:
        return high_card  # High card


def quick_equity_estimate(hero_cards: List[str], villain_count: int,
                          community_cards: List[str] = None,
                          simulations: int = 100) -> float:
    """
    Quick Monte Carlo equity estimation WITH CACHING.

    Args:
        hero_cards: Our hole cards
        villain_count: Number of opponents
        community_cards: Board cards (if any)
        simulations: Number of Monte Carlo simulations

    Returns:
        Equity as a float between 0 and 1
    """
    if not hero_cards or len(hero_cards) != 2:
        return 0.5  # Unknown, assume 50%

    community_cards = community_cards or []

    # Normalize cards
    hero_cards = normalize_cards(hero_cards)
    community_cards = normalize_cards(community_cards)

    # Check cache (postflop only, since preflop uses lookup table)
    if community_cards:
        cache_key = (
            tuple(sorted(hero_cards)),
            villain_count,
            tuple(sorted(community_cards)),
            simulations
        )

        if cache_key in _postflop_cache:
            return _postflop_cache[cache_key]

    wins = 0
    ties = 0

    for _ in range(simulations):
        # Create deck excluding known cards
        deck = make_deck(hero_cards + community_cards)
        random.shuffle(deck)

        # Deal remaining community cards
        cards_needed = 5 - len(community_cards)
        sim_community = community_cards + deck[:cards_needed]
        deck = deck[cards_needed:]

        # Deal villain hands
        villain_hands = []
        for _ in range(villain_count):
            villain_hand = deck[:2]
            deck = deck[2:]
            villain_hands.append(villain_hand)

        # Evaluate hands
        hero_score = evaluate_hand_simple(hero_cards, sim_community)
        villain_scores = [evaluate_hand_simple(vh, sim_community) for vh in villain_hands]

        max_villain_score = max(villain_scores) if villain_scores else 0

        if hero_score > max_villain_score:
            wins += 1
        elif hero_score == max_villain_score:
            ties += 1

    equity = (wins + ties * 0.5) / simulations

    # Save to cache (if postflop and cache not full)
    if community_cards and len(_postflop_cache) < _cache_max_size:
        _postflop_cache[cache_key] = equity

    return equity


@lru_cache(maxsize=500)
def get_preflop_equity_estimate(hand_category: str, opponent_count: int) -> float:
    """
    Get quick equity estimate based on hand category.
    Useful for preflop decisions when Monte Carlo is too slow.

    CACHED for speed (same category+opponent_count = instant result).
    """
    equity_table = {
        "premium": {
            1: 0.85,
            2: 0.73,
            3: 0.63,
            4: 0.55,
        },
        "strong": {
            1: 0.70,
            2: 0.58,
            3: 0.48,
            4: 0.40,
        },
        "value": {
            1: 0.60,
            2: 0.48,
            3: 0.38,
            4: 0.30,
        },
        "speculative": {
            1: 0.55,
            2: 0.42,
            3: 0.32,
            4: 0.25,
        },
        "weak": {
            1: 0.45,
            2: 0.32,
            3: 0.24,
            4: 0.18,
        }
    }

    opponent_count = min(opponent_count, 4)  # Cap at 4
    return equity_table.get(hand_category, {}).get(opponent_count, 0.30)


def calculate_pot_odds(to_call: int, pot: int) -> float:
    """
    Calculate pot odds.

    Returns the equity needed to make a call profitable.
    """
    if to_call <= 0:
        return 0.0

    total_pot = pot + to_call
    return to_call / total_pot if total_pot > 0 else 1.0


def calculate_spr(stack: int, pot: int) -> float:
    """
    Calculate Stack-to-Pot Ratio (SPR).

    SPR affects optimal play:
    - Low SPR (<3): Committed, play for stacks
    - Medium SPR (3-13): Normal play
    - High SPR (>13): Deep stack play
    """
    if pot <= 0:
        return 100.0  # Very high

    return stack / pot


def get_equity_vs_range(hero_cards: List[str], villain_range: set,
                       community_cards: List[str] = None,
                       simulations: int = 500) -> float:
    """
    Calculate equity vs a specific range of hands.

    This is more accurate than assuming random hands,
    but slower than quick_equity_estimate.
    """
    # For now, use quick estimate with adjustment
    # In production, sample from villain_range

    equity = quick_equity_estimate(hero_cards, 1, community_cards, simulations)

    # Adjust based on range tightness (simplified)
    # Tight range = we have less equity
    # Loose range = we have more equity
    range_size = len(villain_range)

    if range_size < 50:  # Very tight range
        equity *= 0.85
    elif range_size < 100:  # Tight range
        equity *= 0.92
    elif range_size > 200:  # Loose range
        equity *= 1.05

    return min(max(equity, 0.0), 1.0)
