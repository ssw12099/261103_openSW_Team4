from datetime import date, timedelta
from reservation import spaces, available, book, lookup, cancel, reservations, ReservationError
from pathlib import Path
import tempfile
import reservation as r

with tempfile.TemporaryDirectory() as temp:
    r.DATA=Path(temp)
    r.SPACES=r.DATA/'spaces.csv'
    r.RESERVATIONS=r.DATA/'reservations.csv'
    r.SPACES.write_text('space_id,name,type,capacity\nS001,회의실 A,회의실,4\n',encoding='utf-8')
    day=(date.today()+timedelta(days=1)).isoformat()
    assert len(available(day,'10:00','11:00',2))==1
    saved=book('S001',day,'10:00','11:00',2,'테스트')
    assert saved['reservation_id']=='R0001'
    assert len(available(day,'10:30','11:30',2))==0
    assert len(available(day,'11:00','12:00',2))==1
    try:
        lookup('R0001','다른사람')
        raise AssertionError('본인 확인 실패')
    except ReservationError: pass
    assert cancel('R0001','테스트')['status']=='취소'
    assert len(available(day,'10:00','11:00',2))==1
    assert reservations().iloc[0]['status']=='취소'
print('예약 핵심 테스트 통과')
