from datetime import date
from pathlib import Path
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from pandas.testing import assert_frame_equal
from streamlit.testing.v1 import AppTest

import reservation as r


HEADERS = [
    '예약 ID', '공간명', '이용일', '시작 시간', '종료 시간',
    '신청 인원', '예약자명', '예약 상태',
]
SPACES = """space_id,name,type,capacity
S01,회의실 A,회의실,4
S02,회의실 B,회의실,8
S03,세미나실,회의실,20
S04,밴드 연습실,연습실,6
S05,댄스 연습실,연습실,12
"""
RESERVATIONS = """reservation_id,space_id,date,start_time,end_time,people,reserver,status
R0001,S02,2026-11-20,10:00,12:00,6,김가상,확정
R0002,S04,2026-11-20,14:00,16:00,5,이가상,확정
R0003,S01,2026-11-21,09:00,10:00,3,박가상,취소
R0004,S03,2026-11-02,13:00,15:00,8,최가상,확정
"""


class ReservationTableTest(unittest.TestCase):
    def setUp(self):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.spaces_path = directory / 'spaces.csv'
        self.reservations_path = directory / 'reservations.csv'
        self.spaces_path.write_text(SPACES, encoding='utf-8')
        self.reservations_path.write_text(RESERVATIONS, encoding='utf-8')
        self.enterContext(patch.multiple(
            r, DATA=directory, SPACES=self.spaces_path, RESERVATIONS=self.reservations_path,
        ))

    def test_display_preserves_rows_and_original_records(self):
        self.reservations_path.write_text(
            RESERVATIONS
            + 'R0005,S02,2026-11-20,12:00,13:00,2,가상 사용자,확정\n'
            + 'R0006,S99,2026-11-20,13:00,14:00,1,가상 사용자,확정\n',
            encoding='utf-8',
        )
        records = r.staff_view('2026-11-20')
        original_records = records.copy(deep=True)
        rooms = r.spaces()
        original_rooms = rooms.copy(deep=True)
        display = r.reservation_table(records, rooms)
        self.assertEqual(list(display.columns), HEADERS)
        self.assertEqual(display['예약 ID'].tolist(), ['R0001', 'R0005', 'R0002', 'R0006'])
        self.assertEqual(display['공간명'].tolist(), [
            '회의실 B', '회의실 B', '밴드 연습실', '알 수 없는 공간 (S99)',
        ])
        assert_frame_equal(records, original_records)
        assert_frame_equal(rooms, original_rooms)

        record = r.lookup('R0003', '박가상')
        original_record = record.copy()
        r.reservation_table([record], rooms)
        self.assertEqual(record, original_record)

    def test_staff_and_customer_tables(self):
        # Keep the display test independent of Ollama and fail if it is called.
        chatbot = ModuleType('chatbot')
        chatbot.ChatError = RuntimeError
        chatbot.answer = self.fail
        self.enterContext(patch.dict('sys.modules', {'chatbot': chatbot}))
        app = AppTest.from_file(str(Path(__file__).with_name('app.py')), default_timeout=10)
        app.run()
        app.sidebar.radio[0].set_value('운영 직원 예약 현황').run()
        app.date_input[0].set_value(date(2026, 11, 20))
        app.button[0].click().run()
        self.assertFalse(app.exception)
        staff = app.dataframe[0].value
        self.assertEqual(list(staff.columns), HEADERS)
        self.assertEqual(staff['예약 ID'].tolist(), ['R0001', 'R0002'])
        self.assertEqual(staff['공간명'].tolist(), ['회의실 B', '밴드 연습실'])

        app.selectbox[0].set_value('S04')
        app.button[0].click().run()
        self.assertEqual(app.dataframe[0].value['예약 ID'].tolist(), ['R0002'])

        app.date_input[0].set_value(date(2026, 11, 22))
        app.button[0].click().run()
        self.assertFalse(app.dataframe)
        self.assertEqual(app.info[0].value, '해당 날짜의 예약이 없습니다.')

        app.sidebar.radio[0].set_value('내 예약 조회 · AI 챗봇').run()
        app.text_input[0].set_value('R0003')
        app.text_input[1].set_value('박가상')
        app.button[0].click().run()
        self.assertFalse(app.exception)
        customer = app.table[0].value
        self.assertEqual(list(customer.columns), HEADERS)
        self.assertEqual(customer.iloc[0].to_dict(), dict(zip(HEADERS, [
            'R0003', '회의실 A', '2026-11-21', '09:00', '10:00', '3', '박가상', '취소',
        ])))


if __name__ == '__main__':
    unittest.main()
