import numpy as np
import json

def smart_input(prompt : str, try_tests : list = [], test_fail_mes : list = None, conditions : list = [], condition_fail_mes : list = None):
    '''Prompts the user for an input
    checks the given conditions (must be inputted as lambdas) and gives the user the gieven error message if failed
    tries the given commands (also must be inputted as lambdas) and gives error message if failed
    re-prompts the user for input if conditions/tests are failed, returns if passed'''
    conditions_met = False
    tests_passed = False
    while (not conditions_met) or (not tests_passed):
        given_input = input(prompt)
        conditions_met = True
        tests_passed = True

        for j in range(len(try_tests)):
            try:
                try_tests[j](given_input)
            except:
                print(test_fail_mes[j])
                tests_passed = False 
        
        for i in range(len(conditions)):
            if not conditions[i](given_input):
                print(condition_fail_mes[i])
                conditions_met = False
        
    return given_input

def sequence(seq_name, start, end):
    """Given a sequence name and range, returns the sequence in that range"""
    
    with open('modules/seq.json') as file:
        seqs = json.load(file)
    
    try:
        seq = seqs[seq_name]
    except:
        raise Exception("Error in sc_seq.sequence(), sequence {} has not been added to the sequence module".format(seq_name))
    
    return seq[start:end]

def name_staples(design):
    '''Given a completed design object, names the staples with following convention:
    helix_index
    index numbered starting at 0 on the left (reverse) side of the seed to the right (forward)'''

    stp_on_helix_count = {}
    for strand in design.strands:
        if not strand.is_scaffold:
            helix = strand.domains[1].helix #helix of stp defined as helix staple is centered on, ie the second domain of the strand (this assumes s shape stps)
            if 'h{}'.format(helix) not in stp_on_helix_count.keys(): #if this is the first stp on this helix
                stp_on_helix_count['h{}'.format(helix)] = 0
            else:
                stp_on_helix_count['h{}'.format(helix)] += 1
            strand.set_name('stp{}_{}'.format(helix, stp_on_helix_count['h{}'.format(helix)]))

    return design

def is_in_outline(shape_outline, helix, position):
    """Given the shape outline, a helix number, and position, rutures True or False if that position exists in the outline"""
    outline = shape_outline[helix]
    row_type = outline[0]
    lines = outline[1]
    for i in range(row_type + 1):
        line = lines[i]
        if position in range(line[0], line[1]):
            return True
    return False

def forward_strand(helix, scaffold_or_staple, sca_forward_even = True):
    """Given the helix number and wheather the strand is a scaffold or staple, returns the orintation of the strand
    Defalt is scaffold is forward on even strands
    Forward: returns True
    Not Forward: returns False"""
    if sca_forward_even:
        if scaffold_or_staple == 'scaffold':
            forward = helix % 2 == 0
        elif scaffold_or_staple == 'staple':
            forward = helix % 2 == 1
        else:
            raise Exception("Invalid input in forward_strand function, must be either 'scaffold' or 'stapple'")
    else:
        if scaffold_or_staple == 'staple':
            forward = helix % 2 == 0
        elif scaffold_or_staple == 'scaffold':
            forward = helix % 2 == 1
        else:
            raise Exception("Invalid input in forward_strand function, must be either 'scaffold' or 'stapple'")

    return forward

def check_valid_outline(shape_outline, hex_or_square):
    """Given the shape outline, and if it lies on a hex or square lattice, checks the min, divisability by 7 or 8, and if it has a center lying on a multiple of 7 or 8"""
    
    if hex_or_square == 'hex':
        multiple = 7
    elif hex_or_square == 'square':
        multiple = 8
    else:
        raise Exception("Error in check_valid_outline(), input for hex_or_square must be eihter 'hex' or 'square'")
    
    min_spot = np.inf
    max_spot = 0
    #for each helix
    for line_outline in shape_outline:
        row_type = line_outline[0]
        lines = line_outline[1]
        for j in range(row_type + 1):
            line = lines[j]
            if line[0] < min_spot:
                min_spot = line[0]
            if line[1] > max_spot:
                max_spot = line[1]

    if min_spot != 0:
        print('Warning: The min value of this outline is {}. To avoid possible erros, make the min value zero'.format(min_spot))

    if max_spot % multiple != 0:
        print('Warning: The design is on a {} lattice not divisable by {}, as its legnth is currently {}.'.format(hex_or_square, multiple, max_spot))
    
    even = 2 * multiple
    if max_spot % even != 0:
        print('Warning: The design is not divisable by {} as its legnth is currently {}. Therefore if you place the seam on the center it will fall not on a crossover point'.format(even, max_spot))

def find_max(shape_outline):
    """Given a shape_ouline, finds the max offset"""
    max_spot = 0
    #for each helix
    for line_outline in shape_outline:
        row_type = line_outline[0]
        lines = line_outline[1]
        for j in range(row_type + 1):
            line = lines[j]
            if line[1] > max_spot:
                max_spot = line[1]

    return max_spot

def find_min(shape_outline):
    """Finds the min offset of a given shape outline"""
    min_spot = np.inf

    #for each helix
    for line_outline in shape_outline:
        row_type = line_outline[0]
        lines = line_outline[1]
        for j in range(row_type + 1):
            line = lines[j]
            if line[0] < min_spot:
                min_spot = line[0]

    return min_spot

def find_center(shape_outline):
    """Finds the center spot of a given shape outline"""
    center = int((find_max(shape_outline) - find_min(shape_outline))/ 2) + find_min(shape_outline)
    return center

def find_pattern_center(seam_locations, helix, shape_outline):
    """Given a seam_locations list and the helix number, returns the center of the crossover pattern for that helix"""
    if helix == 0:
        i = 0
        while True:
            if (i == len(seam_locations)) or (i == -1*len(seam_locations)):
                center = find_center(shape_outline)
                break
            seams = seam_locations[i]
            if seams != 'no seam':
                j = 0
                while True:
                    if seams[j] != 'no seam':
                        center = seams[j]
                        break
                    else:
                        j += 1
                break
            else:
                i += 1
    else:
        i = helix
        while True:
            if (i == len(seam_locations)) or (i == -1*len(seam_locations)):
                center = find_center(shape_outline)
                break
            seams = seam_locations[i]
            if seams != 'no seam':
                j = 0
                while True:
                    if seams[j] != 'no seam':
                        center = seams[j]
                        break
                    else:
                        j += 1
                break
            else:
                i -= 1
    return center

def find_seq_pairs(seq):
    """Given a sequence, returns the base pair sequence"""
    seq_pair = ''
    for letter in seq:
        if letter == 'A':
            seq_pair += 'T'
        elif letter == 'T':
            seq_pair += 'A'
        elif letter == 'C':
            seq_pair += 'G'
        elif letter == 'G':
            seq_pair += 'C'
        else:
            print('Error: seq letter other than ATGC')
    
    return seq_pair