import random

BOOKED_STATUS = 2
BOOK_STATUS = 1
NO_BOOK_STATUS = 0


# 猫眼电影选座规则
# 1、两座之间不能只有一个空座
# 2、座位左右不能一端有一个空座，另一端有空座

def seat_rule(point_list: list):
    for row_point_list in point_list:
        status_list = []
        row_length = len(row_point_list)
        row_book_set = {row_point[1] for row_point in row_point_list if row_point[2] == BOOK_STATUS}
        row_booked_set = {row_point[1] for row_point in row_point_list if row_point[2] == BOOKED_STATUS}
        if row_book_set:
            for index in range(row_length):
                if index in row_book_set:
                    status_list.append(BOOK_STATUS)
                elif index in row_booked_set:
                    status_list.append(BOOKED_STATUS)
                else:
                    status_list.append(NO_BOOK_STATUS)
            status_str = ''.join([str(point) for point in status_list])
            print(status_str, end='     ')
            # 座位规则
            # 判断是否符合第一条规则
            if f'{BOOK_STATUS}{NO_BOOK_STATUS}{BOOK_STATUS}' in status_str:
                print('ERROR MESSAGE: 101')
                return False
            else:
                # 判断是否符合第二条规则
                for non_booked_point in status_str.split(f'{BOOKED_STATUS}'):
                    if non_booked_point and f'{BOOK_STATUS}' in non_booked_point:
                        no_book_point_list = non_booked_point.split(f'{BOOK_STATUS}')
                        if f'{NO_BOOK_STATUS}' in no_book_point_list and non_booked_point.count(f'{NO_BOOK_STATUS}') > 1:
                            print(no_book_point_list)
                            print('ERROR MESSAGE: 01 or 10')
                            return False
            print(True)
    return True


def create_three_dimensional_matrix():
    point_list = []
    for x in range(10):
        row_point_list = []
        for y in range(8):
            z = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1])
            row_point_list.append((x, y, z))
        # print(' '.join([str(i[2]) for i in row_point_list]))
        point_list.append(row_point_list)
    return point_list


if __name__ == '__main__':
    for _ in range(10):
        print(seat_rule(create_three_dimensional_matrix()))
        print()
