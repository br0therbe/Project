const BOOKED_STATUS = 2;
const BOOK_STATUS = 1;
const NO_BOOK_STATUS = 0;

// point_array： 二维数组
function seat_rule(point_array) {
    for (i = 0; i < point_array.length; i++) {
        var row_point_list = point_array[i];
        var status_list = [];
        var row_length = row_point_list.length;
        var row_book_list = [];
        var row_booked_list = [];
        for (index = 0; index < row_length; index++) {
            var row_point = row_point_list[index];
            if (row_point[2] == BOOK_STATUS) {
                row_book_list.push(row_point[1]);
            } else if (row_point[2] == BOOKED_STATUS) {
                row_booked_list.push(row_point[1]);
            }
        }
        if (row_book_list.length > 0) {
            for (index = 0; index < row_length; index++) {
                if (row_book_list.includes(index)) {
                    status_list.push(BOOK_STATUS);
                } else if (row_booked_list.includes(index)) {
                    status_list.push(BOOKED_STATUS);
                } else {
                    status_list.push(NO_BOOK_STATUS)
                }
            }
            status_str = status_list.join('');
            console.log(status_str);
            // 座位规则
            // 判断是否符合第一条规则
            first_ban_rule = BOOK_STATUS.toString() + NO_BOOK_STATUS.toString() + BOOK_STATUS.toString();
            if (status_str.includes(first_ban_rule)) {
                console.log('ERROR MESSAGE: 101');
                return false
            } else {
                // 判断是否符合第二条规则
                var non_booked_point_list = status_str.split(BOOKED_STATUS.toString());
                for (index = 0; index < non_booked_point_list.length; index++) {
                    var non_booked_point = non_booked_point_list[index];
                    if (non_booked_point && non_booked_point.includes(BOOK_STATUS.toString())) {
                        var no_book_point_list = non_booked_point.split(BOOK_STATUS.toString());
                        if (no_book_point_list.includes(NO_BOOK_STATUS.toString()) && non_booked_point.split(NO_BOOK_STATUS.toString()).length > 2) {
                            // console.log(print(no_book_point_list));
                            console.log('ERROR MESSAGE: 01 or 10');
                            return false
                        }
                    }
                }
            }
            console.log(true);
        }
    }
    return true;
}

function create_three_dimensional_matrix() {
    var point_array = [];
    for (x = 0; x < 10; x++) {
        var row_point_list = [];
        var random_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1];
        for (y = 0; y < 8; y++) {
            z = random_array[Math.floor((Math.random() * random_array.length))];
            row_point_list.push([x, y, z]);
        }
        //console.log(row_point_list);
        point_array.push(row_point_list);
    }
    return point_array
}

for (index = 0; index < 10; index++) {
    var point_array = create_three_dimensional_matrix();
    // console.log(a);
    seat_rule(point_array);
    console.log();
}
