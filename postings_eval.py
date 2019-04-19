import math

def evaluate_and(postings_1, postings_2):

    return list_intersection_with_skips(postings_1, postings_2)


def list_intersection_with_skips(list_1, list_2):
    answer = []
    index_1 = 0
    index_2 = 0

    list_1_skip_ptr_len = int(math.sqrt(len(list_1)))
    list_2_skip_ptr_len = int(math.sqrt(len(list_2)))

    while index_1 != len(list_1) and index_2 != len(list_2):
        elem_1 = list_1[index_1]
        elem_2 = list_2[index_2]

        if elem_1 == elem_2:
            answer.append(elem_1)
            index_1 += 1
            index_2 += 1
        
        elif elem_1 < elem_2:
            skip_index = index_1 + list_1_skip_ptr_len
            if skip_index < len(list_1) and list_1[skip_index] <= elem_2:
                index_1 = skip_index
            else:
                index_1 += 1
        else:
            skip_index = index_2 + list_2_skip_ptr_len
            if skip_index < len(list_2) and list_2[skip_index] <= elem_1:
                index_2 = skip_index
            else:
                index_2 += 1

    return answer