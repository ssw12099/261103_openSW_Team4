from datetime import datetime, date, time
from pathlib import Path
import os
import tempfile
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
SPACES = DATA / 'spaces.csv'
RESERVATIONS = DATA / 'reservations.csv'
SPACE_COLUMNS = ['space_id', 'name', 'type', 'capacity']
COLUMNS = ['reservation_id', 'space_id', 'date', 'start_time', 'end_time', 'people', 'reserver', 'status']
# 운영 시간/예약 단위는 제안서에 구체적 수치가 없어 시연용 기본값을 사용합니다.
OPEN_HOUR, CLOSE_HOUR, STEP_MINUTES = 9, 22, 30

class ReservationError(Exception):
    pass

def _load(path, columns):
    if not path.exists():
        if path == RESERVATIONS:
            DATA.mkdir(exist_ok=True)
            pd.DataFrame(columns=columns).to_csv(path, index=False, encoding='utf-8-sig')
        else:
            raise ReservationError('공간 데이터 파일이 없습니다.')
    try:
        df = pd.read_csv(path, dtype=str, encoding='utf-8-sig', keep_default_na=False)
    except Exception as exc:
        raise ReservationError(f'{path.name} 파일을 읽을 수 없습니다.') from exc
    if not set(columns).issubset(df.columns):
        raise ReservationError(f'{path.name}의 필수 컬럼이 누락되었습니다.')
    return df[columns].copy()

def spaces():
    df = _load(SPACES, SPACE_COLUMNS)
    if df['space_id'].duplicated().any():
        raise ReservationError('공간 ID가 중복되었습니다.')
    try:
        df['capacity'] = pd.to_numeric(df['capacity'], errors='raise').astype(int)
    except Exception as exc:
        raise ReservationError('공간 수용 인원 데이터가 잘못되었습니다.') from exc
    if (df['capacity'] <= 0).any():
        raise ReservationError('공간 수용 인원은 양수여야 합니다.')
    return df

def reservations():
    df = _load(RESERVATIONS, COLUMNS)
    if df['reservation_id'].duplicated().any() or not df['status'].isin(['확정','취소']).all():
        raise ReservationError('예약 데이터의 ID 또는 상태가 잘못되었습니다.')
    return df

def _minutes(t):
    try:
        parsed = datetime.strptime(str(t), '%H:%M')
    except ValueError as exc:
        raise ReservationError('시간 형식은 HH:MM이어야 합니다.') from exc
    return parsed.hour * 60 + parsed.minute

def validate(day, start, end, people):
    try:
        d = date.fromisoformat(str(day))
    except ValueError as exc:
        raise ReservationError('이용일이 올바르지 않습니다.') from exc
    s, e = _minutes(start), _minutes(end)
    if s < OPEN_HOUR*60 or e > CLOSE_HOUR*60 or s >= e:
        raise ReservationError(f'이용 시간은 {OPEN_HOUR:02d}:00~{CLOSE_HOUR:02d}:00이며 종료 시각이 시작보다 늦어야 합니다.')
    if s % STEP_MINUTES or e % STEP_MINUTES:
        raise ReservationError(f'예약은 {STEP_MINUTES}분 단위로 입력하세요.')
    if not isinstance(people, int) or people < 1:
        raise ReservationError('이용 인원은 1명 이상이어야 합니다.')
    if datetime.combine(d, time(s//60, s%60)) <= datetime.now():
        raise ReservationError('지난 시각에는 예약할 수 없습니다.')
    return s,e

def available(day, start, end, people, kind='전체'):
    s,e=validate(day,start,end,people)
    rooms=spaces()
    rooms=rooms[rooms['capacity']>=people]
    if kind!='전체': rooms=rooms[rooms['type']==kind]
    booked=reservations()
    booked=booked[(booked['date']==str(day)) & (booked['status']=='확정')]
    unavailable=set()
    for _,r in booked.iterrows():
        if s < _minutes(r['end_time']) and e > _minutes(r['start_time']):
            unavailable.add(r['space_id'])
    return rooms[~rooms['space_id'].isin(unavailable)].sort_values(['capacity','space_id']).reset_index(drop=True)

def _save(df):
    DATA.mkdir(exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA, suffix='.csv')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as f:
            df.to_csv(f,index=False)
        os.replace(tmp, RESERVATIONS)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def book(space_id,day,start,end,people,reserver):
    reserver=reserver.strip()
    if not reserver or len(reserver)>60:
        raise ReservationError('예약자명은 1~60자로 입력하세요.')
    room=available(day,start,end,people)
    if space_id not in room['space_id'].values:
        raise ReservationError('선택한 공간을 예약할 수 없습니다. 조건을 다시 조회하세요.')
    # 로컬 단일 사용자 순차 처리: 저장 직전 CSV를 다시 읽고 중복을 검사합니다.
    df=reservations()
    s,e=_minutes(start),_minutes(end)
    for _,r in df.iterrows():
        if r['space_id']==space_id and r['date']==str(day) and r['status']=='확정':
            if s < _minutes(r['end_time']) and e > _minutes(r['start_time']):
                raise ReservationError('기존 확정 예약과 시간이 겹칩니다.')
    ids=[int(v[1:]) for v in df['reservation_id'] if len(v)>1 and v.startswith('R') and v[1:].isdigit()]
    new_id=f'R{max(ids,default=0)+1:04d}'
    new=pd.DataFrame([[new_id,space_id,str(day),start,end,str(people),reserver,'확정']],columns=COLUMNS)
    _save(pd.concat([df,new],ignore_index=True))
    return new.iloc[0].to_dict()

def lookup(reservation_id,reserver):
    df=reservations()
    match=df[(df['reservation_id']==reservation_id.strip()) & (df['reserver']==reserver.strip())]
    if len(match)!=1: raise ReservationError('예약 정보가 일치하지 않습니다')
    return match.iloc[0].to_dict()

def can_cancel(record):
    if record['status']=='취소': return False,'이미 취소된 예약입니다.'
    when=datetime.combine(date.fromisoformat(record['date']),datetime.strptime(record['start_time'],'%H:%M').time())
    if when<=datetime.now(): return False,'이용 시작 시각이 지나 취소할 수 없습니다.'
    return True,'취소할 수 있습니다.'

def cancel(reservation_id,reserver):
    record=lookup(reservation_id,reserver)
    allowed,reason=can_cancel(record)
    if not allowed: raise ReservationError(reason)
    df=reservations()
    mask=(df['reservation_id']==reservation_id.strip()) & (df['reserver']==reserver.strip())
    df.loc[mask,'status']='취소'
    _save(df)
    return lookup(reservation_id,reserver)

def staff_view(day,space_id='전체'):
    df=reservations()
    df=df[df['date']==str(day)]
    if space_id!='전체': df=df[df['space_id']==space_id]
    return df.sort_values(['space_id','start_time']).reset_index(drop=True)
