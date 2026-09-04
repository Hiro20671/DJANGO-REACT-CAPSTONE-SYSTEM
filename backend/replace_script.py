import sys
with open('apps/core/templates/teachers/nutrition.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
pattern = re.compile(r'let html = `[\s\S]*?container\.innerHTML \+= html;', re.MULTILINE)
replacement = '''            const notes = record && record.teacher_notes ? `<div style="margin-top:10px; font-size:0.85rem; color:#666; background:#f9f9f9; padding:8px; border-radius:5px; font-style:italic;">"${record.teacher_notes}"</div>` : '';
            
            let html = `
            <div style="border: 1px solid #bbb; border-radius: 10px; padding: 20px; margin-bottom: 15px; background: #fff;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; gap:15px; align-items:center;">
                        <div style="width: 45px; height: 45px; border-radius: 50%; background: #eee; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #555; overflow: hidden;">${avatarHtml}</div>
                        <div>
                            <h4 style="margin: 0; font-size: 1.05rem;">${st.first_name} ${st.last_name}</h4>
                            <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #666;">${st.age} years old</p>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <h3 style="margin:0; font-size: 1.2rem; color: ${color};">${status}</h3>
                        <p style="margin:0; font-size: 0.8rem; color: #888;">Snack Status</p>
                    </div>
                </div>
                ${notes}
            </div>`;
            container.innerHTML += html;'''

new_content = pattern.sub(replacement, content)
with open('apps/core/templates/teachers/nutrition.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done replacing.')
