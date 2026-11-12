from datetime import date, timedelta, datetime
import streamlit as st
from reservation import (ReservationError, spaces, available, book, lookup, can_cancel, cancel, staff_view, OPEN_HOUR, CLOSE_HOUR, STEP_MINUTES)
from chatbot import answer, ChatError

st.set_page_config(page_title='모아공간 예약 관리',page_icon='📅',layout='wide')
st.title('모아공간 회의실·연습실 예약 관리')
st.caption('로컬 시연용 시스템 · 예약/취소 내역은 CSV 파일에 보관됩니다.')
menu=st.sidebar.radio('메뉴',['공간 조회 및 예약','내 예약 조회 · AI 챗봇','예약 취소','운영 직원 예약 현황'])

def show_error(e): st.error(str(e))
def details(r):
    labels={'reservation_id':'예약 ID','space_id':'공간 ID','date':'이용일','start_time':'시작','end_time':'종료','people':'인원','reserver':'예약자명','status':'상태'}
    st.table({labels.get(k,k):[v] for k,v in r.items()})

if menu=='공간 조회 및 예약':
    st.subheader('F-01 공간 조회 / F-02 예약 신청')
    with st.form('search'):
        day=st.date_input('이용일',min_value=date.today(),value=date.today()+timedelta(days=1))
        c1,c2=st.columns(2)
        slots=[f'{h:02d}:{m:02d}' for h in range(OPEN_HOUR,CLOSE_HOUR+1) for m in (0,30) if h<CLOSE_HOUR or m==0]
        start=c1.selectbox('시작 시각',slots,index=0)
        end=c2.selectbox('종료 시각',slots,index=2)
        people=st.number_input('이용 인원',min_value=1,value=2,step=1)
        kind=st.selectbox('공간 유형',['전체','회의실','연습실'])
        searched=st.form_submit_button('이용 가능 공간 조회')
    if searched:
        try:
            result=available(day,start,end,int(people),kind)
            st.session_state['search_result']={'day':str(day),'start':start,'end':end,'people':int(people),'kind':kind,'ids':result['space_id'].tolist()}
        except ReservationError as exc:
            st.session_state.pop('search_result',None);show_error(exc)
    q=st.session_state.get('search_result')
    if q:
        try:
            rooms=spaces()
            filtered=rooms[rooms['space_id'].isin(q['ids'])]
            st.caption(f"조회 조건: {q['day']} {q['start']}~{q['end']} / {q['people']}명 / {q['kind']}")
            if filtered.empty: st.info('조건에 맞는 이용 가능 공간이 없습니다.')
            else:
                st.dataframe(filtered.rename(columns={'space_id':'공간 ID','name':'공간명','type':'유형','capacity':'수용 인원'}),hide_index=True,use_container_width=True)
                with st.form('booking'):
                    selected=st.selectbox('예약할 공간',q['ids'],format_func=lambda x: f"{x} · {rooms.loc[rooms.space_id==x,'name'].iloc[0]}")
                    reserver=st.text_input('예약자명')
                    submitted=st.form_submit_button('예약 확정')
                if submitted:
                    try:
                        saved=book(selected,q['day'],q['start'],q['end'],q['people'],reserver)
                        st.success('예약이 확정되었습니다. 예약 ID를 보관하세요.')
                        details(saved)
                        st.session_state.pop('search_result',None)
                    except ReservationError as exc: show_error(exc)
        except ReservationError as exc: show_error(exc)

elif menu=='내 예약 조회 · AI 챗봇':
    st.subheader('F-04 내 예약 조회 / F-05 AI 챗봇')
    with st.form('verify'):
        rid=st.text_input('예약 ID',placeholder='R0001')
        name=st.text_input('예약자명')
        verify=st.form_submit_button('예약 조회 및 본인 확인')
    if verify:
        st.session_state.pop('verified',None)
        try: st.session_state['verified']=lookup(rid,name)
        except ReservationError as exc: show_error(exc)
    record=st.session_state.get('verified')
    if record:
        try:
            record=lookup(record['reservation_id'],record['reserver'])
            st.session_state['verified']=record
            details(record)
            allowed,reason=can_cancel(record)
            st.info(reason)
            st.caption('챗봇에는 본인 확인된 예약 1건만 전달합니다. 예약·취소는 수행하지 않습니다.')
            with st.form('ask'):
                question=st.text_input('예약에 관해 질문하세요',placeholder='내 예약 몇 시야?')
                ask=st.form_submit_button('질문 전송')
            if ask:
                try:
                    with st.spinner('Ollama 응답 생성 중...'): st.write(answer(record,question))
                except ChatError as exc:
                    show_error(exc);st.info('기본 예약 조회 기능은 계속 사용할 수 있습니다.')
        except ReservationError as exc:
            st.session_state.pop('verified',None);show_error(exc)
    else: st.info('예약 ID와 예약자명으로 본인 확인을 완료해야 챗봇을 사용할 수 있습니다.')

elif menu=='예약 취소':
    st.subheader('F-03 예약 취소')
    with st.form('cancel_check'):
        rid=st.text_input('예약 ID',placeholder='R0001')
        name=st.text_input('예약자명')
        check=st.form_submit_button('예약 확인')
    if check:
        st.session_state.pop('cancel_target',None)
        try: st.session_state['cancel_target']=lookup(rid,name)
        except ReservationError as exc: show_error(exc)
    target=st.session_state.get('cancel_target')
    if target:
        try:
            target=lookup(target['reservation_id'],target['reserver'])
            details(target)
            allowed,reason=can_cancel(target)
            st.info(reason)
            if allowed and st.button('취소 확정',type='primary'):
                canceled=cancel(target['reservation_id'],target['reserver'])
                st.session_state.pop('cancel_target',None)
                st.success('예약이 취소되었습니다.')
                details(canceled)
        except ReservationError as exc: show_error(exc)

else:
    st.subheader('F-04 운영 직원 예약 현황')
    st.caption('제안서 범위에 따라 로그인 없이 로컬 PC에서 사용하는 직원용 화면입니다.')
    try:
        rooms=spaces()
        day=st.date_input('조회 날짜',value=date.today(),key='staff_date')
        choice=st.selectbox('공간 필터',['전체']+rooms['space_id'].tolist(),format_func=lambda x: '전체' if x=='전체' else f"{x} · {rooms.loc[rooms.space_id==x,'name'].iloc[0]}")
        if st.button('예약 조회'):
            df=staff_view(day,choice)
            if df.empty: st.info('해당 날짜의 예약이 없습니다.')
            else: st.dataframe(df,hide_index=True,use_container_width=True)
    except ReservationError as exc: show_error(exc)
