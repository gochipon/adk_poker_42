import itertools
import collections


def rank_of_five_card(card_list):
    rank_to_num = {'A': 14, 'K': 13, 'Q': 12, 'J': 11,
                   'T': 10, '10': 10, '9': 9, '8': 8, '7': 7,
                   '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}

    # サポートするスート表記（ASCIIとUnicodeの双方に対応）
    unicode_suits = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
    ascii_suits = {'S': 'S', 'H': 'H', 'D': 'D', 'C': 'C',
                   's': 'S', 'h': 'H', 'd': 'D', 'c': 'C'}

    def parse_card(token):
        # 例: 'A♥', '10♣', 'T♣', 'AH', 'Ts', 'qd' などを受け付ける
        if not token or len(token) < 2:
            raise ValueError(f"不正なカード表記: {token}")

        suit_char = token[-1]
        # スート正規化
        if suit_char in unicode_suits:
            suit = unicode_suits[suit_char]
            rank_str = token[:-1]
        elif suit_char in ascii_suits:
            suit = ascii_suits[suit_char]
            rank_str = token[:-1]
        else:
            # 末尾がスートでない場合のフォールバック（従来仕様: 2文字固定 like 'AS'）
            # ただし新仕様では基本的に末尾がスートのはず
            if len(token) == 2:
                rank_str, suit_raw = token[0], token[1]
                suit = ascii_suits.get(suit_raw, unicode_suits.get(suit_raw, None))
                if suit is None:
                    raise ValueError(f"不正なスート表記: {suit_raw}")
            else:
                raise ValueError(f"不正なカード表記: {token}")

        # ランク正規化（'10' と 'T' を同一視、英字は大文字化）
        rank_str = rank_str.upper()
        if rank_str == '10':
            rank_key = '10'
        elif len(rank_str) == 1 and rank_str in {'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'}:
            rank_key = rank_str
        else:
            # 例えば 't' などは upper 済みなのでこの条件に入らない
            raise ValueError(f"不正なランク表記: {rank_str}")

        return rank_to_num[rank_key], suit

    parsed = [parse_card(c) for c in card_list]
    ranks = [r for r, _ in parsed]
    suits = [s for _, s in parsed]

    num_cnt = collections.Counter(ranks)
    num_cnt = sorted(num_cnt.items(), key=lambda x: (-x[1], -x[0]))

    suits_cnt = collections.Counter(suits)
    is_flush = len(suits_cnt) == 1
    is_flush_draw = suits_cnt.most_common()[0][1] == 4

    num_list = sorted(list(set(ranks)))
    is_straight = (
        len(num_list) == 5 and
        (num_list[-1] - num_list[0] == 4 or num_list == [2, 3, 4, 5, 14])
    )

    # 役判定
    if len(num_cnt) == 2:
        if num_cnt[0][1] == 4:
            rank_text, rank_num = 'four of a kind', 8
        else:
            rank_text, rank_num = 'full house', 7
    elif len(num_cnt) == 3:
        if num_cnt[0][1] == 3:
            rank_text, rank_num = 'three of a kind', 4
        else:
            rank_text, rank_num = 'two pair', 3
    elif len(num_cnt) == 4:
        rank_text, rank_num = 'one pair', 2
    else:
        if is_flush and is_straight:
            rank_text, rank_num = 'straight flush', 9
        elif is_flush:
            rank_text, rank_num = 'flush', 6
        elif is_straight:
            rank_text, rank_num = 'straight', 5
        elif is_flush_draw:
            rank_text, rank_num = 'flush draw', 1
        else:
            rank_text, rank_num = 'high card', 0

    # ハンド強度を数値化
    high = rank_num * 100 ** 5 + sum(
        [item[0] * 100 ** (4 - i) for i, item in enumerate(num_cnt)]
    )
    return rank_text, rank_num, high


def rank_of_any_card(card_list):
    """
    2〜7枚のカードを受け取り、可能な役を判定する。
    - 2枚 → 簡易プリフロップ評価（ペア・スーテッド・コネクターなど）
    - 5〜7枚 → 通常の役判定（フロップ以降）
    """
    if len(card_list) < 2:
        raise ValueError("カードは最低2枚必要です。")

    # 2枚だけなら簡易評価
    if len(card_list) == 2:
        rank_to_num = {'A': 14, 'K': 13, 'Q': 12, 'J': 11,
                       'T': 10, '10': 10, '9': 9, '8': 8, '7': 7,
                       '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        unicode_suits = {'♠': 'S', '♥': 'H', '♦': 'D', '♣': 'C'}
        ascii_suits = {'S': 'S', 'H': 'H', 'D': 'D', 'C': 'C',
                       's': 'S', 'h': 'H', 'd': 'D', 'c': 'C'}

        def parse_card(token):
            suit_char = token[-1]
            if suit_char in unicode_suits:
                suit = unicode_suits[suit_char]
                rank_str = token[:-1]
            elif suit_char in ascii_suits:
                suit = ascii_suits[suit_char]
                rank_str = token[:-1]
            else:
                raise ValueError(f"不正なカード表記: {token}")
            rank_str = rank_str.upper()
            if rank_str == '10':
                rank_key = '10'
            elif len(rank_str) == 1 and rank_str in rank_to_num:
                rank_key = rank_str
            else:
                raise ValueError(f"不正なランク表記: {rank_str}")
            return rank_to_num[rank_key], suit

        parsed = [parse_card(c) for c in card_list]
        ranks = [r for r, _ in parsed]
        suits = [s for _, s in parsed]

        same_suit = suits[0] == suits[1]
        diff = abs(ranks[0] - ranks[1])
        if ranks[0] == ranks[1]:
            text = "one pair"
            rank_num = 2
        elif same_suit and diff == 1:
            text = "suited connector"
            rank_num = 1.5
        elif same_suit:
            text = "suited"
            rank_num = 1.2
        elif diff == 1:
            text = "connector"
            rank_num = 1.1
        else:
            text = "high card"
            rank_num = 1.0

        score = rank_num * 100 + sum(ranks)
        return card_list, text, score

    # 5枚以上は既存のロジック
    best_score = 0
    best_five = None
    best_text = None

    for comb in itertools.combinations(card_list, 5):
        text, rank_num, score = rank_of_five_card(comb)
        if score > best_score:
            best_score = score
            best_five = comb
            best_text = text

    return best_five, best_text, best_score
