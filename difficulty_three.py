def hand(hole_cards, community_cards):
    #Given hand and community cards for Texas Hold'em, returns the type of hand and a list of tiebreaking card ranks.
    SUITS = "♣♦♥♠"
    RANKS = "AKQJT98765432"

    is_straight = False
    is_flush = False
    is_straight_flush = False
    
    pool = hole_cards + community_cards
    pool = [c if len(c) < 3 else "T" + c[-1] for c in pool]
    pool.sort(key = lambda card: RANKS.index(card[0]))
    
    #Idenify hand type
    seq_streak = 1 #Tracks running straight
    last_p_rank = pool[0][0] 
    high_straight_rank = None #Tracks highest rank of straight if any
    
    p_streak = 1 #Tracks running streak of last_rank
    max_p_streak = 0 #Tracks highest streak of atleast one pair, used to determine full house / two pair
    dict_pair = {} #saves all pairs by rank.  used to full house and two pairs
    for c in pool[1:]:
        #change pair variables
        if c[0] == last_p_rank:
            p_streak += 1
        else:
            #reset streak
            if p_streak > 1:
                dict_pair[last_p_rank] = p_streak
                if p_streak > max_p_streak:
                    max_p_streak = p_streak
            p_streak = 1
            
            #straight isn't broken with duplicates, only gaps, so check here
            if RANKS.index(c[0]) == RANKS.index(last_p_rank) + 1:
                seq_streak += 1
                if seq_streak == 5: 
                    high_straight_rank = RANKS[RANKS.index(c[0]) - 4]
                    is_straight = True
            else:
                seq_streak = 1
        last_p_rank = c[0]
    #Gotta repeat here since ending the list counts as breaking the streak
    if p_streak > 1:
        dict_pair[c[0]] = p_streak
        if p_streak > max_p_streak:
            max_p_streak = p_streak
    
    #determine whether flush
    just_suits = [c[1] for c in pool]
    for suit in SUITS:
        if just_suits.count(suit) >= 5:
            is_flush = True
            flush_suit = suit
    
    #Determine whether any of our flushes are straight flushes
    if is_flush:
        only_flush_suits = [RANKS.index(c[0]) for c in pool if c[1] == flush_suit] #List of rank's indexs for all cards in pool belonging to the flush suit
        seq_streak = 0
        highest_rank = RANKS[only_flush_suits[0]]
        i = 0
        
        while i < len(only_flush_suits) - 1:
            if only_flush_suits[i] == only_flush_suits[i + 1] - 1:
                seq_streak += 1
            elif only_flush_suits[i] != only_flush_suits[i + 1]:
                seq_streak = 0
                highest_rank = RANKS[only_flush_suits[i + 1]]
            if seq_streak == 4:
                is_straight_flush = True
                high_straight_rank = highest_rank
                break
            i += 1
    
    #construct list of ordered ranks in pool, used for constructing tiebreakers    
    just_ranks = []
    for c in pool:
        if c[0] not in just_ranks:
            just_ranks.append(c[0])
        
    #construct list of tuples (f, r) for all pairs/of-a-kind with f being frequency of the rank, and r the rank's index in RANKS, ordered first by their frequency, then their rank.  
    #Then just convert those tuples to the ranks because that's all we need!
    #e.g., ["A♠", "K♦", "K♣", "K♥", "A♥", "Q♥", "3♦"] will be [K, A], as K is more frequent.  
    # we use this to construct tiebreakers where multipule pairs exist
    if max_p_streak > 1:
        ordered_pair_ranks = [(-dict_pair[r], RANKS.index(r)) for r in dict_pair.keys()]
        ordered_pair_ranks.sort()
        ordered_pair_ranks = [RANKS[tuple[1]] for tuple in ordered_pair_ranks]
    
    if max_p_streak == 4:
        hand = "four-of-a-kind"
        tiebreaker = [ordered_pair_ranks[0]]
        just_ranks.remove(tiebreaker[0])
        tiebreaker += just_ranks[0]
    elif is_straight_flush:
        hand = "straight-flush"
        straight_start = just_ranks.index(high_straight_rank)
        tiebreaker = [r for r in just_ranks[straight_start:straight_start + 5]]
    elif max_p_streak == 3 and len(dict_pair.keys()) > 1:
        hand = "full house"
        tiebreaker = ordered_pair_ranks[:2]
    elif is_flush:
        hand = "flush"
        tiebreaker = [c[0] for c in pool if c[1] == flush_suit][:5]
    elif is_straight:
        hand = "straight"
        straight_start = just_ranks.index(high_straight_rank)
        tiebreaker = [r for r in just_ranks[straight_start:straight_start + 5]]
    elif max_p_streak == 3:
        hand = "three-of-a-kind"
        tiebreaker = [list(dict_pair.keys())[0]]
        just_ranks.remove(tiebreaker[0])
        tiebreaker += just_ranks[:2]
    elif len(dict_pair.keys()) > 1:
        hand = "two pair"
        tiebreaker = ordered_pair_ranks[:2]
        for r in tiebreaker:
            just_ranks.remove(r)
        tiebreaker += just_ranks[0]
    elif len(dict_pair.keys()) == 1:
        hand = "pair"
        tiebreaker = [list(dict_pair.keys())[0]]
        just_ranks.remove(tiebreaker[0])
        tiebreaker += just_ranks[:3]
    else:
        hand = "nothing"
        tiebreaker = [c[0] for c in pool[:5]]
    
    #replace 'T' with '10' in tiebreaker haha
    for i, r in enumerate(tiebreaker):
        if r == "T":
            tiebreaker[i] = "10"
    
    return (hand, tiebreaker)


def volume(heightmap):
    # By filling from the bottom up, we can treat depths lower than the one we're trying to fill at as the same as an edge.
    # make a list of all heights, fill the lowest using a flood fill Algorithm until no more values of that height exist
    # assign None to any cells that exlusivly drain into an edge, or exlusivly drain into None

    # convert numpy array to list of list because thats all I ever had in mind when I made this thing
    heightmap = [list(row) for row in heightmap]


    def flood_fill(x, y):
        def scan(x, y):
            # returns true if no collision
            # collision happens should the cells height not match the initial seeds height: h
            # overwright lowest_wall as needed when collisions happen
            nonlocal lowest_wall
            cur_height = heightmap[y][x]
            if cur_height == "f":
                return False
            if cur_height == h:
                return True
            else:
                if cur_height == None or lowest_wall == None:
                    lowest_wall = None
                else:
                    lowest_wall = min(lowest_wall, cur_height)
                return False
                # attempt to flood fill at given coordinate using span filling

        # overwright the reigon flood filled with its lowest wall's value (or None, if the reigon would drain into an edge)
        # returns sum of water filled

        # Because we're filling from the bottom up, we will never see height values lower than the initial seed height.

        h = heightmap[y][x]  # h being the layer we're trying to flood fill on
        lowest_wall = 10000  # being the lowest wall we've collided with, None trumps all.  int is unbounded in python, and the game establishes no max wall height, so let's hope 10000 works

        rightmost = x  # right most x value in current line
        leftmost = x  # left most x value in current line
        line_fill_list = []  # list of cells represented by tuples (xl, xr, y) to be "filled" by lowest_wall value

        seeds = [(x, y)]  # Could use Queue here, but just a list for now
        while len(seeds):
            seed = seeds.pop(0)

            # Tracks if collided above or below, primes for seed storage
            above_collide = True
            below_collide = True

            # attempt right
            x, y = seed
            # end early if seed has been filled already
            if heightmap[y][x] == "f":
                continue

            rightmost = x
            leftmost = x
            x -= 1  # so we hit index 1 the first time
            while scan(x + 1, y):
                x += 1
                rightmost = x
                heightmap[y][x] = "f"

                # scan above
                if scan(x, y + 1):
                    if above_collide:
                        seeds.append((x, y + 1))
                        above_collide = False
                else:
                    above_collide = True

                # scan below
                if scan(x, y - 1):
                    if below_collide:
                        seeds.append((x, y - 1))
                        below_collide = False
                else:
                    below_collide = True

            # attempt left
            x, y = seed
            above_collide = True
            below_collide = True
            while scan(x - 1, y):
                x -= 1
                leftmost = x
                heightmap[y][x] = "f"
                # DRIP this away somehow?
                # scan above
                if scan(x, y + 1):
                    if above_collide:
                        seeds.append((x, y + 1))
                        above_collide = False
                else:
                    above_collide = True

                # scan below
                if scan(x, y - 1):
                    if below_collide:
                        seeds.append((x, y - 1))
                        below_collide = False
                else:
                    below_collide = True

            line_fill_list.append((leftmost, rightmost, y))

        # overwrite all ranges in line_fill_list, sum up their total change in height
        cells_filled = 0
        for line in line_fill_list:
            xl, xr, y = line
            cells_filled += xr + 1 - xl
            for x in range(xl, xr + 1):
                heightmap[y][x] = lowest_wall

        # finally, return the volume this flood_fill filled
        if lowest_wall == None:
            return 0
        else:
            return cells_filled * (lowest_wall - h)

            # construct list of all heights in acending order

    height_list = list({h for row in heightmap for h in row})
    height_list.sort()

    # Wrap heightmap in None value so we don't have to worry checking for edges
    for n, row in enumerate(heightmap):
        heightmap[n] = [None] + row + [None]
    heightmap = [[None] * len(heightmap[0])] + heightmap + [[None] * len(heightmap[0])]

    map_width = len(heightmap[0])

    vol = 0
    # floodfill all instances of lowest heights until the map is filled
    for h in height_list[:-1]:
        for y, row in enumerate(heightmap):
            while h in row:
                x = row.index(h)
                vol += flood_fill(x, y)
    return vol

def validate_battlefield(field):
    def grab_ship(row, col):
        size = 1
        #because scanning prioritizes top and left, we only have to look right and down each step
        while True:
            field[row][col] = 0
            
            if size == 4:
                return size
            
            right = field[row][col + 1]
            down = field[row + 1][col]
            
            #ships touching, return False for error handling
            if 1 == right == down:
                return False

            if field[row + 1][col + 1] or field[row - 1][col - 1] or field[row - 1][col + 1] or field[row + 1][col - 1]:
                return False
            
            if 0 == right == down:
                field[row][col] = 0
                return size

            if size == 1:
                #set direction of the ship we're scanning
                if right:
                    dir = (0, 1)
                    col += 1
                if down:
                    dir = (1, 0)
                    row += 1
                size += 1
                continue

            if dir[0]:
                if not down:
                    return size
                size += 1
                row += 1
            else:
                if not right:
                    return size
                size += 1
                col += 1

    #wrap field in extra zeros so we don't have to worry about list limits
    field = [[0]* len(field)] + field + [[0]* len(field)]
    field = [[0] + row + [0] for row in field]
    
    ship_ct_dict = {1:4, 2:3, 3:2, 4:1} # size:count
    for i, row in enumerate(field):
        while 1 in row:
            seed_col = row.index(1)
            new_size = grab_ship(i, seed_col)
            if not new_size:
                return False
            #too many of this size already found
            if ship_ct_dict[new_size] == 0:
                return False
            ship_ct_dict[new_size] -= 1

    #all values must be zero by the end
    return not any(ship_ct_dict.values())

def sudoku(puzzle):
    # Solves easy sudoku.  determinable sudokus without the need for guessing unknowns and testing them.  
    def get_potentials(puzzle, n):
        if puzzle[n // 9][n % 9] == 0:
            potentials = [i + 1 for i in range(9)]
        else:
            potentials = puzzle[n // 9][n % 9]
        pools = [get_col(puzzle, n), get_row(puzzle, n), get_cel(puzzle, n)]
        for pool in pools:
            potentials = [x for x in potentials if x not in pool]
        if len(potentials) == 1:
            return potentials[0]
        else:
            return potentials

    def get_col(puzzle, n):
        x = n % 9
        return [puzzle[i][x] for i in range(9)]

    def get_row(puzzle, n):
        y = n // 9
        return puzzle[y]

    def get_cel(puzzle, n):
        # get 9x9 cel that n lies in
        x = ((n % 9) // 3) * 3
        y = ((n // 9) // 3) * 3
        return [puzzle[y + i][x:x + 3][j] for j in range(3) for i in range(3)]

    empty = 0
    for row in puzzle:
        empty += row.count(0)

    while empty != 0:
        for i in range(81):
            x = i % 9
            y = i // 9
            n = puzzle[y][x]
            if isinstance(n, list) or n == 0:
                puzzle[y][x] = get_potentials(puzzle, i)
                if not isinstance(puzzle[y][x], list):
                    empty -= 1

    return puzzle
