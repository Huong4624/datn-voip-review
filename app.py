"""Private Community Cloud review page. File upload is historical, never called live."""
import json
import pandas as pd
import streamlit as st
st.set_page_config(page_title='VoIP · Báo cáo MON',layout='wide')
st.title('VoIP QoS · Báo cáo KNN từ MON-HQ')
st.warning('CHẾ ĐỘ LỊCH SỬ · Dữ liệu từ file đã xuất. Trang này không kết nối trực tiếp với GNS3 và không phải live feed.')
uploaded=st.file_uploader('Chọn Day28_web_snapshot_….json',type=['json'])
if uploaded:
    try:
        if uploaded.size>20_000_000:raise ValueError('File quá lớn; xuất từng giai đoạn dưới 20 MB.')
        data=json.loads(uploaded.getvalue())
        if data.get('schema')!='D28_WEB_SNAPSHOT_V1' or data.get('live') is not False:raise ValueError('Không đúng định dạng snapshot Day28.')
        st.caption(f"Xuất lúc {data['exported_local']} · Model {data['model_id']}")
        calls=data['calls']
        if calls:
            call=st.selectbox('Lượt đã lưu',calls,format_func=lambda c:c['run_id'])
            st.write(f"Mode {call['mode']} · tải yêu cầu {call['load_kbps']} kbps · {call['purpose']}")
            st.caption('Bản xuất ghi nhận đã đối chiếu tại máy lab; trang này không kiểm chứng lại MON đang hoạt động.')
            st.code(call['mon_digest']);events=call['events']
            rows=sorted([e['data'] for e in events if e['kind']=='PREDICTION'],key=lambda r:(r.get('window_start_epoch',0),r.get('direction','')))
            if rows:
                df=pd.DataFrame(rows);fields=['direction','window_start_epoch','rule_label','label','observed_loss_pct','jitter_rfc3550_p95_ms','tap_delay_p95_ms']
                st.dataframe(df[[k for k in fields if k in df]],hide_index=True,width='stretch')
                df['time']=pd.to_datetime(df.window_start_epoch,unit='s',utc=True)
                for name in fields[-3:]:st.write(name);st.line_chart(df.pivot_table(index='time',columns='direction',values=name,aggfunc='first'))
            st.write('Cảnh báo đã lưu');st.dataframe(pd.DataFrame(sorted([e['data'] for e in events if e['kind']=='ALERT'],key=lambda r:r.get('window_start_epoch',0))),width='stretch',hide_index=True)
        else:st.info('Snapshot chưa có cuộc gọi đã đối chiếu MON.')
    except (ValueError,KeyError,TypeError) as e:st.error(str(e))
else:st.info('Tại máy lab: chạy .\\go.ps1 web-export. Tải file vừa xuất lên đây để xem từ xa.')
st.caption('Tốt / Trung bình / Kém là nhãn tham chiếu chất lượng truyền tải. Không phải MOS hoặc đánh giá người nghe.')
