class Word:
    def __init__(self, value, start, end, type):
        self.value = value
        self.start = start
        self.end = end
        self.type = type

class AssistantParameter:
    def __init__(self):
        self.res_msg = {
            -1: 'Momo xin lỗi, Momo chưa hiểu câu trả lời của bạn. Bạn có thể lặp lại giúp Momo được không',
            0: 'Vui lòng cho Momo biết khoa bạn muốn khám được không hoặc bạn có thể chọn trên màn hình',
            1: 'Vậy bạn có thể cho Momo biết bạn bị đau hoặc cảm thấy khó chịu ở chỗ nào được không? Để Momo có thể giúp bạn tìm khoa phù hợp.',
            2: 'Momo đã chọn cho bạn khoa {dep_name}. Vui lòng xác nhận để tiếp tục ạ.',
            3: "Bạn có thể miêu tả triệu chứng cho momo được không",
            4: 'Bái baiii.',
            5: 'Cảm ơn bạn đã cung cấp thông tin cho Momo. Vui lòng đợi một lát, Momo sẽ phân tích và trả lời bạn kết quả',
            6: 'Hì hì. Momo chào bạn.',
            7: 'Huhu (~.~). Momo rất tiếc vì không thể giúp được bạn.',
            8: 'Hì hì, Momo đang nghe đây',
            9: "Hì hì. Để Momo nói lại cho bạn nghe ha",
            10: 'Momo xin lỗi, nhưng bạn có thể cho Momo biết lại là bạn khó chịu chỗ nào được không',
            11: 'Bạn có thể miêu tả kỹ hơn cho Momo biết mình không khoẻ ở đâu không.',
            12: 'Momo đã biết rồi ạ. Vui lòng đợi một lát, Momo sẽ phân tích và trả lời bạn kết quả',
            13: 'Momo xin lỗi bạn, hiện tại bệnh viện chưa có {dep_name}. Bạn vui lòng chọn khoa khác trên màn hình ạ.',
            14: 'Momo xin lỗi bạn, hiện tại {dep_name} của bệnh viện chưa hoạt động ạ. Bạn vui lòng chọn khoa khác trên màn hình.',
            15: 'Momo xin lỗi bạn, hiện tại Momo gặp lỗi khi phân tích khoa cho bạn. Bạn vui lòng chọn khoa khác trên màn hình ạ.'
        }

        self.msg_for_states = {1: self.res_msg[3], 2: self.res_msg[0], 3: self.res_msg[1]}

        # 'khoa thần kinh':     0
        # 'khoa sản':           1
        # 'khoa nội tổng quát': 2
        # 'khoa mắt':           3
        # 'khoa tai mũi họng':  4
        # 'khoa răng hàm mặt':  5
        # 'khoa da liễu':       6
        # 'khoa xương khớp':    7
        # 'khoa tiêu hoá':      8

        self.department = [
            'khoa thần kinh',
            'khoa sản',
            'khoa nội tổng quát',
            'khoa mắt',
            'khoa tai mũi họng',
            'khoa răng hàm mặt',
            'khoa da liễu',
            'khoa xương khớp',
            'khoa tiêu hoá'
        ]

        self.list_department = {
            0: ['khoa thần kinh' , 'thần kinh'],
            1: ['khoa sản', 'khoa phụ khoa', 'khoa thai sản', 'phụ khoa', 'thai sản', 'sản'],
            2: ['khoa tổng quát', 'khoa nội tổng quát', 'tổng quát', 'nội tổng quát'],
            3: ['mắt', 'khoa mắt'],
            4: ['khoa tai mũi họng' ,'tai mũi họng', 'mũi họng', 'tai mũi', 'tai', 'mũi', 'họng'],
            5: ['răng hàm mặt', 'khoa răng hàm mặt', 'răng', 'hàm', 'mặt', 'răng hàm', 'hàm mặt'],
            6: ['da liễu', 'khoa da liễu', 'da'],
            7: ['khoa xương khớp', 'xương khớp', 'khớp', 'xương'],
            8: ['khoa tiêu hoá', 'tiêu hoá']
        }

        self.list_composite_words = [
            'da đầu', 'da mặt', 'da tay', 'da chân',
            'da lưng', 'da đùi', 'da mông', 'da bụng',
            'bắp tay', 'bắp đùi', 'bắp chân', 'bắp thịt',
            'cổ tay', 'cổ chân',
            'khớp chân', 'khớp tay',
            'móng tay', 'móng chân',
            'mắt chân'
        ]

        self.dict_synonym_part_body = {
            'mí': 'mắt',
            'mí mắt': 'mắt',
            'mi mắt': 'mắt',
            'mi': 'mắt',
            'lông mi': 'mắt',
            'mống mắt': 'mắt',
            'con ngươi': 'mắt',

            'ngón tay': 'tay',
            'ngón trỏ': 'tay',
            'ngón giữa': 'tay',
            'ngón đeo nhẫn': 'tay',
            'ngón út': 'tay',
            'ngón cái': 'tay',
            'cẳng tay': 'tay',
            'khuỷu tay': 'tay',
            'bàn tay': 'tay',

            'ngón chân': 'chân',
            'đầu gối': 'chân',
            'cẳng chân': 'chân',
            'gót chân': 'chân',
            'bàn chân': 'chân',

            'mồm': 'miệng',
            'lưỡi': 'miệng',
            'môi': 'miệng',

            'nướu': 'răng',
            'lợi': 'răng',

            'cuống họng': 'họng',
            'khí quản': 'họng',
            'thực quản': 'họng',

            'tim': 'nội tạng',
            'gan': 'nội tạng',
            'phổi': 'nội tạng',
            'ruột': 'nội tạng',
            'tĩnh mạch': 'nội tạng',
            'động mạch': 'nội tạng',
            'cật': 'nội tạng',
            'tuyến tụy': 'nội tạng',
            'bọng đái': 'nội tạng',
            'dương vật': 'nội tạng',
            'âm đạo': 'nội tạng',

            'dú': 'vú',

            'da đầu': 'da',
            'da mặt': 'da',
            'da tay': 'da',
            'da chân': 'da',
            'da lưng': 'da',
            'da đùi': 'da',
            'da mông': 'da',
            'da bụng': 'da',
            'bắp tay': 'bắp',
            'bắp đùi': 'bắp',
            'bắp chân': 'bắp',
            'bắp thịt': 'bắp',
            'cổ tay': 'khớp',
            'cổ chân': 'khớp',
            'khớp chân': 'khớp',
            'khớp tay': 'khớp',
            'móng tay': 'móng',
            'móng chân': 'móng',
            'mắt chân': 'khớp'
        }

        self.dict_synonym_problem = {
            'lở': 'lở loét',
            'loét': 'lở loét',

            'xót': 'rát',

            'khó chịu' : 'không ổn',
            'không okay' : 'không ổn',
            'không khoẻ' : 'không ổn',
            'không bình thường' : 'không ổn',
            'không được ổn' : 'không ổn',
            'không đươc okay' : 'không ổn',
            'không được khoẻ' : 'không ổn',
            'không được bình thường' : 'không ổn',

            'táo bón': 'bón',
            'tiêu chảy': 'bón',

            'nhức': 'nhói',

            'buồn nôn': 'nôn',
            'mắc ói': 'nôn',
            'ói': 'nôn',

            'mệt mỏi': 'mệt',
            'đừ': 'mệt',
            'uể oải': 'mệt',
            'kiệt sức': 'mệt',

            'ợ': 'tieu_hoa',
            'chua': 'tieu_hoa',
            'đắng': 'tieu_hoa',

            'tê': 'than_kinh',
            'quên': 'than_kinh',
            'căng thẳng': 'than_kinh',

            'rách': 'noi',
            'co rút': 'noi',
            'chuột rút': 'noi',

            'nổi ban': 'noi_da_lieu',
            'phát ban': 'noi_da_lieu',
            'nổi chấm đỏ': 'noi_da_lieu',

            'ho': 'tai_mui_hong_noi',
            'hạch': 'tai_mui_hong_noi',

            'ù': 'tai_mui_hong',
            'sổ': 'tai_mui_hong',
            'thở': 'tai_mui_hong',
            'vướng': 'tai_mui_hong',
            'hắt xì': 'tai_mui_hong',
            'chảy nước': 'tai_mui_hong',

            'bón': 'tieu_hoa_noi',
            'nôn': 'tieu_hoa_noi',
            'chướng': 'tieu_hoa_noi',
            'nấc cụt': 'tieu_hoa_noi',
            'đầy hơi': 'tieu_hoa_noi',
            'khó tiêu': 'tieu_hoa_noi',
            'đi cầu': 'tieu_hoa_noi',
            'đi ngoài': 'tieu_hoa_noi',

            'mệt': 'noi_than_kinh',

            'ngủ': 'than_kinh_noi',
            'chóng': 'than_kinh_noi',
            'stress': 'than_kinh_noi',
            'co giật': 'than_kinh_noi',
            'động kinh': 'than_kinh_noi',

            'rát': 'da_lieu',
            'ngứa': 'da_lieu',
            'dị ứng': 'da_lieu',
            'nổi mẩn': 'da_lieu',
            'nổi mụn': 'da_lieu',
            'vảy nến': 'da_lieu',
            'nổi mề đay': 'da_lieu'
        }