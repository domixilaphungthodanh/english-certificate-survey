from pathlib import Path
import csv,json,re,collections,statistics,hashlib,os,html,unicodedata
ROOT=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
MULTI={6,8,10,30,31}
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('đ','d').strip()
def main():
    raw=ROOT/'data/raw/responses.csv'; rows=list(csv.DictReader(raw.open(encoding='utf-8-sig',newline=''))); cols=list(rows[0]); n=len(rows)
    out=ROOT/'reports'; out.mkdir(exist_ok=True); (out/'figures').mkdir(exist_ok=True)
    allfreq=[]; likert=[]; catalog=[]; sections=[]; checks=[]
    def save(name,records):
        if not records:return
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    for q in range(1,33):
        col=cols[q]; vals=[r[col].strip() for r in rows]; valid=[v for v in vals if v]; kind='likert' if 11<=q<=27 else 'multiple' if q in MULTI else 'text' if q==32 else 'single'
        catalog.append({'question':q,'title':col,'type':kind,'answered':len(valid),'missing':n-len(valid)})
        section=f'## Câu {q}: {col}\n\nSố trả lời: **{len(valid)}/{n}**.\n\n'
        if kind=='text':
            no={'khong','khong co','ko','ko co','k','n/a','hong co','khong a','khong biet','oke','….','...'}
            substantive=[v for v in valid if norm(v) not in no]
            section+=f'Có {len(valid)} phản hồi không rỗng; {len(substantive)} phản hồi còn lại sau khi loại các câu không có góp ý theo danh sách quy tắc. Đây là phân loại hỗ trợ, cần đọc lại thủ công. Không tự coi 51 câu trả lời là 51 góp ý có nội dung.\n\n'
            section+='Không công khai nguyên văn góp ý để bảo vệ thông tin người trả lời.\n'
        else:
            freq=collections.Counter(t.strip() for v in valid for t in (v.split(',') if kind=='multiple' else [v]) if t.strip())
            if kind=='likert':
                bad=[v for v in valid if v not in {'1','2','3','4','5'}]; assert not bad,(q,bad)
                nums=[int(v) for v in valid]; med=statistics.median(nums); mean=statistics.mean(nums); top=sum(v>=4 for v in nums)/len(nums)
                likert.append({'question':q,'title':col,'n':len(nums),'mean':mean,'median':med,'top2_pct':top*100})
                freq=collections.Counter({str(i):freq[str(i)] for i in range(1,6)})
                section+=f'Trung bình **{mean:.2f}/5**, trung vị **{med:g}**, chọn mức 4–5 **{top:.1%}**. Trung bình là mô tả bổ sung cho thang thứ bậc.\n\n'
            section+='| Lựa chọn | Số người/lượt chọn | % người trả lời câu |\n|---|---:|---:|\n'
            for val,count in freq.items():
                allfreq.append({'question':q,'option':val,'count':count,'answered':len(valid),'pct_respondents':100*count/len(valid)})
                section+=f'| {val} | {count} | {100*count/len(valid):.2f}% |\n'
            if kind=='multiple':section+='\nCâu nhiều lựa chọn: tỷ lệ chia cho số người trả lời câu; tổng tỷ lệ có thể vượt 100%. Tách theo dấu phẩy của Google Forms; giữ nhãn trống/khác trong dữ liệu gốc để rà soát.\n'
            checks.append({'check':f'Q{q}_counts','pass':sum(freq.values())==len(valid) if kind!='multiple' else all(c<=len(valid) for c in freq.values())})
            fig,ax=plt.subplots(figsize=(11,max(3,len(freq)*.32)))
            labels=list(freq); counts=list(freq.values()); ax.barh(labels,counts,color='#167d9a');ax.invert_yaxis();ax.set_xlabel('Số lượt chọn / người');ax.set_title(f'Câu {q} (n={len(valid)})')
            ax.bar_label(ax.containers[0],padding=3);ax.set_xlim(0,max(counts)*1.2+1);fig.tight_layout();fig.savefig(out/'figures'/f'q{q:02}.png',dpi=120);plt.close(fig)
            section+=f'\n![Câu {q}](figures/q{q:02}.png)\n'
        sections.append(section)
    save('question_catalog.csv',catalog);save('frequencies.csv',allfreq);save('likert_summary.csv',likert)
    # Quy tắc chuẩn hoá khoa tường minh, không đoán nhãn Khoa T.
    mapping={}
    for v in set(r[cols[3]] for r in rows):
        k=norm(v)
        mapped='Khoa Toán - Thống kê' if 'thong ke' in k or k=='toan' else 'Khoa Công nghệ thông tin' if k in {'cong nghe thong tin','khoa cong nghe thong tin'} else 'Khoa Quản trị kinh doanh' if k in {'quan tri kinh doanh','khoa quan tri kinh doanh'} else v
        mapping[v]=mapped
    save('faculty_mapping.csv',[{'raw':k,'normalized':v} for k,v in sorted(mapping.items())])
    issues=[]
    for i,r in enumerate(rows,1):
        tokens={x.strip() for x in r[cols[6]].split(',') if x.strip()}
        if r[cols[5]]=='Chưa từng' and tokens-{'Chưa thi chứng chỉ nào'}:issues.append({'row':i,'issue':'Q5 chưa từng nhưng Q6 có chứng chỉ'})
        if 'Chưa thi chứng chỉ nào' in tokens and len(tokens)>1:issues.append({'row':i,'issue':'Q6 vừa chưa thi vừa chọn chứng chỉ'})
        tokens30={x.strip() for x in r[cols[30]].split(',') if x.strip()}
        if 'Không gặp khó khăn' in tokens30 and len(tokens30)>1:issues.append({'row':i,'issue':'Q30 vừa không khó khăn vừa chọn khó khăn'})
    save('consistency_flags.csv',issues)
    cross=collections.Counter((r[cols[2]],r[cols[7]]) for r in rows)
    save('year_by_intended_certificate.csv',[{'year':a,'certificate':b,'count':c} for (a,b),c in sorted(cross.items())])
    checks += [{'check':'89_source_responses','pass':n==89},{'check':'32_questions','pass':len(catalog)==32},{'check':'17_likert_items','pass':len(likert)==17}]
    (out/'quality.json').write_text(json.dumps(checks,indent=2),encoding='utf-8');assert all(c['pass'] for c in checks)
    manifest={'source_form':'User-provided survey; private source link omitted','exported_local_date':'2026-11-04','responses':n,'scope':'snapshot; not a live sync'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    intro=f'''# Khảo sát lựa chọn chứng chỉ tiếng Anh — sinh viên Tôn Đức Thắng

Tổng hợp toàn bộ **32 câu hỏi**, **{n} phản hồi** tại thời điểm xuất dữ liệu 04/11/2026. Dữ liệu thực xuất từ bảng phản hồi liên kết Google Forms; không tạo dữ liệu giả.

## Phát hiện chính

- 60/89 sinh viên năm ba (67,42%): mẫu tập trung vào một nhóm năm học; chưa có thiết kế lấy mẫu nên không suy rộng toàn trường.
- Dự định thi IELTS: 33/89 (37,08%); chưa quyết định: 21/89 (23,60%).
- Kênh thông tin mạng xã hội/Internet: 71/89 (79,78%).
- Nhu cầu lộ trình học và ôn thi: 50/89 (56,18%).
- Có **{len(issues)} cờ mâu thuẫn** theo quy tắc đã nêu; một người có thể mang nhiều cờ. Chỉ đánh dấu, không tự xoá.

## Phương pháp và giới hạn

Tần số câu đơn chia cho số trả lời không rỗng. Câu nhiều lựa chọn tính theo người trả lời câu, tổng % có thể vượt 100%. Giữ phân phối Likert 1–5, trung vị, trung bình và tỷ lệ mức 4–5. Chưa gán nhãn ý nghĩa từng mức khi chưa đối chiếu hướng dẫn thang đo gốc. Không gọi trung bình cao là tác động nhân quả; không chạy hồi quy/EFA hoặc Cronbach một cách tự động chỉ để có kết quả. Các mục có thể đo các khía cạnh khác nhau.

Tên khoa chỉ chuẩn hoá theo bảng mapping có thể kiểm tra. Khoa T giữ nguyên vì chưa đủ thông tin. Trình bày tần số nguyên trạng cho Q3; mapping là bảng bổ sung. Không tái nhận diện người trả lời. CSV gốc gồm thời gian và cột email nên giữ cục bộ; không tự công khai dữ liệu cá nhân lên GitHub.

## Đề xuất

Ưu tiên tài liệu so sánh chứng chỉ, lộ trình ôn thi và tư vấn theo trình độ/mục tiêu. Đối chiếu yêu cầu chuẩn đầu ra với quy định chính thức hiện hành trước khi tư vấn; khảo sát không xác minh quy định. Kiểm tra lại các câu mâu thuẫn nếu còn liên hệ được người trả lời theo quy trình khảo sát của bạn.

'''
    report=intro+'\n\n'.join(sections);(out/'findings.md').write_text(report,encoding='utf-8')
    # HTML tự chứa, mở offline; escape toàn bộ nội dung do người dùng nhập.
    import base64
    htmlparts=['<!doctype html><meta charset="utf-8"><title>Khảo sát chứng chỉ tiếng Anh</title><style>body{max-width:1100px;margin:40px auto;font:16px/1.65 Arial;color:#183044}img{max-width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}section{border-top:1px solid #ccc;padding-top:20px}</style>']
    htmlparts.append('<pre>'+html.escape(intro)+'</pre>')
    for q,s in enumerate(sections,1):
        htmlparts.append('<section><pre>'+html.escape(re.sub(r'!\[.*?\]\(.*?\)','',s))+'</pre>')
        p=out/'figures'/f'q{q:02}.png'
        if p.exists():htmlparts.append('<img src="data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()+'">')
        htmlparts.append('</section>')
    (out/'report.html').write_text('\n'.join(htmlparts),encoding='utf-8')
    print(json.dumps({'responses':n,'questions':len(catalog),'charts':31,'checks_pass':len(checks),'consistency_flags':len(issues)}))
if __name__=='__main__':main()

