'use client';
import{useState,useRef,useEffect}from'react';

const MODELS=[
  {id:'daniela',label:'Daniela'},
];

export default function Chat(){
  const[msgs,setMsgs]=useState([]);
  const[input,setInput]=useState('');
  const[loading,setLoading]=useState(false);
  const[sidebarOpen,setSidebarOpen]=useState(false);
  const bottomRef=useRef(null);
  const textareaRef=useRef(null);

  useEffect(()=>{
    bottomRef.current?.scrollIntoView({behavior:'smooth'});
  },[msgs,loading]);

  useEffect(()=>{
    const ta=textareaRef.current;
    if(!ta)return;
    ta.style.height='auto';
    ta.style.height=Math.min(ta.scrollHeight,200)+'px';
  },[input]);

  async function send(){
    const text=input.trim();
    if(!text||loading)return;
    const userMsg={role:'user',content:text};
    const newMsgs=[...msgs,userMsg];
    setMsgs(newMsgs);
    setInput('');
    setLoading(true);
    try{
      const res=await fetch('/api/ia-chat',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({messages:newMsgs,model:'daniela'})
      });
      const data=await res.json();
      const reply=data.reply||data.error||'Erro desconhecido';
      setMsgs(prev=>[...prev,{role:'assistant',content:reply}]);
    }catch(e){
      setMsgs(prev=>[...prev,{role:'assistant',content:'❌ Erro de conexão: '+e.message}]);
    }
    setLoading(false);
  }

  function handleKey(e){
    if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}
  }

  function newChat(){setMsgs([]);setInput('');}

  function copyMsg(text){navigator.clipboard.writeText(text);}

  function renderContent(text){
    // Basic markdown: bold, code blocks, inline code
    const lines=text.split('\n');
    const result=[];
    let inCode=false;
    let codeLines=[];
    let codeLang='';
    for(let i=0;i<lines.length;i++){
      const line=lines[i];
      if(line.startsWith('```')){
        if(!inCode){inCode=true;codeLang=line.slice(3).trim();codeLines=[];}
        else{
          result.push(
            <div key={i} className="code-block">
              <div className="code-header">
                <span className="code-lang">{codeLang||'code'}</span>
                <button className="code-copy" onClick={()=>copyMsg(codeLines.join('\n'))}>Copiar</button>
              </div>
              <pre><code>{codeLines.join('\n')}</code></pre>
            </div>
          );
          inCode=false;codeLines=[];codeLang='';
        }
        continue;
      }
      if(inCode){codeLines.push(line);continue;}
      // Process inline
      let processed=line
        .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
        .replace(/\*(.+?)\*/g,'<em>$1</em>')
        .replace(/`(.+?)`/g,'<code class="inline-code">$1</code>')
        .replace(/^### (.+)/,'<h3>$1</h3>')
        .replace(/^## (.+)/,'<h2>$1</h2>')
        .replace(/^# (.+)/,'<h1>$1</h1>')
        .replace(/^- (.+)/,'<li>$1</li>');
      result.push(<p key={i} dangerouslySetInnerHTML={{__html:processed||'&nbsp;'}}/>);
    }
    return result;
  }

  const isEmpty=msgs.length===0;

  return(
    <div className="app">
      {/* Sidebar */}
      <aside className={`sidebar${sidebarOpen?' open':''}`}>
        <div className="sidebar-top">
          <button className="sidebar-btn new-chat" onClick={newChat}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg>
            Novo chat
          </button>
        </div>
        <div className="sidebar-section">
          <div className="sidebar-label">Hoje</div>
          {msgs.length>0&&(
            <div className="sidebar-item active">
              {msgs[0]?.content?.slice(0,40)||'Chat'}...
            </div>
          )}
        </div>
        <div className="sidebar-bottom">
          <div className="user-info">
            <div className="user-avatar">D</div>
            <div className="user-name">Daniela Coelho</div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        {/* Header */}
        <header className="header">
          <button className="menu-btn" onClick={()=>setSidebarOpen(o=>!o)}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
          <div className="model-selector">
            <span>Daniela</span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
          <div className="header-actions">
            <button className="icon-btn" title="Novo chat" onClick={newChat}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
          </div>
        </header>

        {/* Messages */}
        <div className="messages">
          {isEmpty&&(
            <div className="welcome">
              <div className="welcome-logo">
                <svg width="48" height="48" viewBox="0 0 100 100" fill="none">
                  <circle cx="50" cy="50" r="48" fill="#c05621" opacity="0.15"/>
                  <path d="M30 65 Q50 20 70 65" stroke="#c05621" strokeWidth="6" fill="none" strokeLinecap="round"/>
                  <circle cx="50" cy="50" r="8" fill="#c05621"/>
                </svg>
              </div>
              <h1 className="welcome-title">Como posso ajudar?</h1>
              <div className="suggestions">
                {['Explique a teoria do apego','Como lidar com ansiedade?','O que é inteligência emocional?','Técnicas de mindfulness'].map(s=>(
                  <button key={s} className="suggestion" onClick={()=>{setInput(s);}}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {msgs.map((m,i)=>(
            <div key={i} className={`msg-row ${m.role}`}>
              {m.role==='assistant'&&(
                <div className="avatar assistant-avatar">D</div>
              )}
              <div className="msg-bubble">
                <div className="msg-content">
                  {m.role==='assistant'?renderContent(m.content):<p>{m.content}</p>}
                </div>
                <div className="msg-actions">
                  <button className="action-btn" onClick={()=>copyMsg(m.content)} title="Copiar">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  </button>
                </div>
              </div>
              {m.role==='user'&&(
                <div className="avatar user-avatar">U</div>
              )}
            </div>
          ))}

          {loading&&(
            <div className="msg-row assistant">
              <div className="avatar assistant-avatar">D</div>
              <div className="msg-bubble">
                <div className="typing">
                  <span/><span/><span/>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef}/>
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              ref={textareaRef}
              className="input-box"
              placeholder="Mensagem para Daniela..."
              value={input}
              onChange={e=>setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
            />
            <div className="input-actions">
              <button
                className={`send-btn${input.trim()&&!loading?' active':''}`}
                onClick={send}
                disabled={!input.trim()||loading}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
          <div className="input-note">Daniela pode cometer erros. Verifique informações importantes.</div>
        </div>
      </main>

      <style>{`
        *{box-sizing:border-box;margin:0;padding:0;}
        :root{
          --bg:#1a1a1a;
          --surface:#2a2a2a;
          --surface2:#333;
          --border:#3a3a3a;
          --text:#ececec;
          --text2:#9a9a9a;
          --accent:#c05621;
          --accent2:#e07843;
          --user-bg:#2d2d2d;
          --radius:12px;
        }
        body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
        .app{display:flex;height:100vh;overflow:hidden;background:var(--bg);}
        
        /* Sidebar */
        .sidebar{width:260px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;transition:transform .3s;flex-shrink:0;}
        .sidebar-top{padding:16px 12px;}
        .new-chat{width:100%;display:flex;align-items:center;gap:8px;background:transparent;border:1px solid var(--border);color:var(--text);padding:10px 14px;border-radius:8px;cursor:pointer;font-size:14px;transition:background .2s;}
        .new-chat:hover{background:var(--surface2);}
        .sidebar-section{flex:1;overflow-y:auto;padding:8px 12px;}
        .sidebar-label{font-size:12px;color:var(--text2);padding:8px 8px 4px;font-weight:500;}
        .sidebar-item{padding:10px 10px;border-radius:8px;cursor:pointer;font-size:14px;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;transition:background .2s;}
        .sidebar-item:hover,.sidebar-item.active{background:var(--surface2);color:var(--text);}
        .sidebar-bottom{padding:12px;border-top:1px solid var(--border);}
        .user-info{display:flex;align-items:center;gap:10px;padding:8px;border-radius:8px;cursor:pointer;}
        .user-info:hover{background:var(--surface2);}
        .user-avatar{width:32px;height:32px;background:var(--accent);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:#fff;}
        .user-name{font-size:14px;font-weight:500;}
        
        /* Main */
        .main{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden;}
        
        /* Header */
        .header{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--border);background:var(--bg);}
        .menu-btn,.icon-btn{background:transparent;border:none;color:var(--text2);cursor:pointer;padding:6px;border-radius:6px;display:flex;align-items:center;justify-content:center;transition:background .2s;}
        .menu-btn:hover,.icon-btn:hover{background:var(--surface2);color:var(--text);}
        .model-selector{display:flex;align-items:center;gap:6px;background:transparent;border:none;color:var(--text);cursor:pointer;padding:6px 10px;border-radius:8px;font-size:15px;font-weight:600;transition:background .2s;}
        .model-selector:hover{background:var(--surface2);}
        .header-actions{margin-left:auto;display:flex;gap:4px;}
        
        /* Messages */
        .messages{flex:1;overflow-y:auto;padding:24px 0;display:flex;flex-direction:column;gap:0;}
        .messages::-webkit-scrollbar{width:6px;}
        .messages::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
        
        /* Welcome */
        .welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px 24px;text-align:center;}
        .welcome-logo{margin-bottom:20px;}
        .welcome-title{font-size:28px;font-weight:700;color:var(--text);margin-bottom:32px;}
        .suggestions{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;max-width:640px;}
        .suggestion{background:var(--surface);border:1px solid var(--border);color:var(--text2);padding:10px 16px;border-radius:20px;cursor:pointer;font-size:14px;transition:all .2s;}
        .suggestion:hover{background:var(--surface2);color:var(--text);border-color:var(--accent);}
        
        /* Messages */
        .msg-row{display:flex;align-items:flex-start;gap:12px;padding:16px max(calc((100%-800px)/2),24px);transition:background .2s;}
        .msg-row:hover{background:rgba(255,255,255,0.02);}
        .msg-row.user{flex-direction:row-reverse;}
        .avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0;}
        .assistant-avatar{background:var(--accent);color:#fff;}
        .user-avatar{background:#5865f2;color:#fff;}
        .msg-bubble{flex:1;min-width:0;max-width:700px;}
        .msg-row.user .msg-bubble{align-items:flex-end;}
        .msg-content{font-size:15px;line-height:1.7;color:var(--text);}
        .msg-content p{margin-bottom:8px;}
        .msg-content p:last-child{margin-bottom:0;}
        .msg-content h1,.msg-content h2,.msg-content h3{margin:16px 0 8px;font-weight:700;}
        .msg-content h1{font-size:20px;}
        .msg-content h2{font-size:18px;}
        .msg-content h3{font-size:16px;}
        .msg-content li{margin-left:20px;margin-bottom:4px;}
        .msg-content strong{font-weight:700;color:#fff;}
        .msg-content em{font-style:italic;color:var(--text2);}
        .inline-code{background:var(--surface2);border:1px solid var(--border);border-radius:4px;padding:1px 5px;font-family:'JetBrains Mono','Fira Code',monospace;font-size:13px;color:#e2a96b;}
        .code-block{background:#1e1e2e;border:1px solid var(--border);border-radius:10px;overflow:hidden;margin:12px 0;}
        .code-header{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;background:#252535;border-bottom:1px solid var(--border);}
        .code-lang{font-size:12px;color:var(--text2);font-family:monospace;text-transform:uppercase;}
        .code-copy{background:transparent;border:none;color:var(--text2);cursor:pointer;font-size:12px;padding:2px 8px;border-radius:4px;transition:all .2s;}
        .code-copy:hover{background:var(--surface2);color:var(--text);}
        .code-block pre{padding:16px;overflow-x:auto;}
        .code-block code{font-family:'JetBrains Mono','Fira Code',monospace;font-size:13px;line-height:1.6;color:#cdd6f4;}
        .msg-row.user .msg-content{background:var(--user-bg);padding:12px 16px;border-radius:18px 18px 4px 18px;}
        .msg-actions{display:flex;gap:4px;margin-top:6px;opacity:0;transition:opacity .2s;}
        .msg-row:hover .msg-actions{opacity:1;}
        .action-btn{background:transparent;border:none;color:var(--text2);cursor:pointer;padding:5px;border-radius:5px;display:flex;align-items:center;transition:all .2s;}
        .action-btn:hover{background:var(--surface2);color:var(--text);}
        
        /* Typing */
        .typing{display:flex;gap:5px;align-items:center;padding:8px 2px;}
        .typing span{width:8px;height:8px;background:var(--text2);border-radius:50%;animation:bounce 1.2s infinite;}
        .typing span:nth-child(2){animation-delay:.2s;}
        .typing span:nth-child(3){animation-delay:.4s;}
        @keyframes bounce{0%,60%,100%{transform:translateY(0);}30%{transform:translateY(-8px);}}
        
        /* Input */
        .input-area{padding:16px;background:var(--bg);border-top:1px solid var(--border);}
        .input-container{max-width:800px;margin:0 auto;background:var(--surface);border:1px solid var(--border);border-radius:16px;display:flex;align-items:flex-end;gap:8px;padding:12px 14px;transition:border-color .2s;}
        .input-container:focus-within{border-color:var(--accent);}
        .input-box{flex:1;background:transparent;border:none;outline:none;color:var(--text);font-size:15px;line-height:1.5;resize:none;max-height:200px;font-family:inherit;}
        .input-box::placeholder{color:var(--text2);}
        .input-actions{display:flex;gap:6px;align-items:center;}
        .send-btn{width:34px;height:34px;border-radius:8px;border:none;background:var(--surface2);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;}
        .send-btn.active{background:var(--accent);color:#fff;}
        .send-btn:disabled{cursor:not-allowed;opacity:0.5;}
        .send-btn:not(:disabled):hover.active{background:var(--accent2);}
        .input-note{text-align:center;font-size:12px;color:var(--text2);margin-top:8px;max-width:800px;margin-left:auto;margin-right:auto;}
        
        /* Responsive */
        @media(max-width:768px){
          .sidebar{position:fixed;left:0;top:0;height:100%;z-index:100;transform:translateX(-100%);}
          .sidebar.open{transform:translateX(0);}
          .msg-row{padding:16px 16px;}
          .welcome-title{font-size:22px;}
        }
      `}</style>
    </div>
  );
}
