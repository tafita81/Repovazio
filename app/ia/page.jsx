'use client';
import{useState,useRef,useEffect,useCallback}from'react';

export default function Chat(){
  const[msgs,setMsgs]=useState([]);
  const[input,setInput]=useState('');
  const[loading,setLoading]=useState(false);
  const[streamingText,setStreamingText]=useState('');
  const[toolStatus,setToolStatus]=useState('');
  const[uploadedFile,setUploadedFile]=useState(null);
  const[sessions,setSessions]=useState([]);
  const[sessionId]=useState(()=>Date.now().toString(36));
  const bottomRef=useRef(null);
  const taRef=useRef(null);
  const fileRef=useRef(null);
  const abortRef=useRef(null);

  useEffect(()=>{bottomRef.current?.scrollIntoView({behavior:'smooth'});},[msgs,streamingText]);
  useEffect(()=>{if(taRef.current){taRef.current.style.height='auto';taRef.current.style.height=Math.min(taRef.current.scrollHeight,200)+'px';}},[input]);

  // Load sessions from localStorage
  useEffect(()=>{
    try{const s=JSON.parse(localStorage.getItem('daniela_sessions')||'[]');setSessions(s);}catch(e){}
  },[]);

  function saveSession(newMsgs){
    if(!newMsgs.length)return;
    const s={id:sessionId,title:newMsgs[0]?.content?.substring(0,40)||'Chat',msgs:newMsgs,ts:Date.now()};
    const prev=JSON.parse(localStorage.getItem('daniela_sessions')||'[]').filter(x=>x.id!==sessionId);
    const updated=[s,...prev].slice(0,20);
    localStorage.setItem('daniela_sessions',JSON.stringify(updated));
    setSessions(updated);
  }

  function loadSession(s){setMsgs(s.msgs);setInput('');}
  function newChat(){setMsgs([]);setInput('');setUploadedFile(null);}

  async function handleFile(e){
    const file=e.target.files[0];if(!file)return;
    const reader=new FileReader();
    reader.onload=(ev)=>{
      setUploadedFile({name:file.name,type:file.type,data:ev.target.result,preview:file.type.startsWith('image/')?ev.target.result:null});
    };
    reader.readAsDataURL(file);
  }

  async function send(){
    const text=input.trim();
    if((!text&&!uploadedFile)||loading)return;
    const userContent=text+(uploadedFile?`\n\n📎 ${uploadedFile.name}`:'');
    const userMsg={role:'user',content:userContent};
    const newMsgs=[...msgs,userMsg];
    setMsgs(newMsgs);setInput('');setStreamingText('');setToolStatus('');setLoading(true);

    const fileData=uploadedFile?.data;
    setUploadedFile(null);

    abortRef.current=new AbortController();
    let accumulated='';

    try{
      const res=await fetch('/api/ia-chat',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({messages:newMsgs,stream:true,image:fileData,session_id:sessionId}),
        signal:abortRef.current.signal
      });

      if(!res.ok||!res.body){
        const d=await res.json().catch(()=>({reply:'Erro de conexão'}));
        const finalMsgs=[...newMsgs,{role:'assistant',content:d.reply}];
        setMsgs(finalMsgs);saveSession(finalMsgs);
        setLoading(false);return;
      }

      const reader=res.body.getReader();
      const dec=new TextDecoder();

      while(true){
        const{done,value}=await reader.read();
        if(done)break;
        const chunk=dec.decode(value);
        const lines=chunk.split('\n');
        for(const line of lines){
          if(!line.startsWith('data:'))continue;
          try{
            const ev=JSON.parse(line.slice(5).trim());
            if(ev.type==='text'){accumulated+=ev.content;setStreamingText(accumulated);}
            else if(ev.type==='tool_start'){setToolStatus(`🔧 Usando: ${ev.tools?.join(', ')}...`);}
            else if(ev.type==='tool_running'){setToolStatus(`⚙️ Executando ${ev.tool}...`);}
            else if(ev.type==='tool_result'){setToolStatus(`✅ ${ev.tool} concluído`);}
            else if(ev.type==='done'){
              const finalMsgs=[...newMsgs,{role:'assistant',content:accumulated}];
              setMsgs(finalMsgs);setStreamingText('');setToolStatus('');
              saveSession(finalMsgs);
            }
            else if(ev.type==='error'){accumulated+=`\n❌ ${ev.message}`;}
          }catch(e){}
        }
      }
    }catch(e){
      if(e.name!=='AbortError'){
        const finalMsgs=[...newMsgs,{role:'assistant',content:`❌ Erro: ${e.message}`}];
        setMsgs(finalMsgs);saveSession(finalMsgs);
      }
    }
    setLoading(false);setStreamingText('');setToolStatus('');
  }

  function stopGeneration(){abortRef.current?.abort();setLoading(false);if(streamingText){setMsgs(p=>[...p,{role:'assistant',content:streamingText}]);setStreamingText('');}}

  function handleKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}

  function md(text){
    const lines=text.split('\n');const out=[];let inCode=false;let codeLines=[];let codeLang='';
    for(let i=0;i<lines.length;i++){
      const line=lines[i];
      if(line.startsWith('```')){
        if(!inCode){inCode=true;codeLang=line.slice(3).trim()||'code';codeLines=[];}
        else{out.push(<div key={i} className="cb"><div className="ch"><span className="cl">{codeLang}</span><button className="cc" onClick={()=>navigator.clipboard.writeText(codeLines.join('\n'))}>Copiar</button></div><pre><code>{codeLines.join('\n')}</code></pre></div>);inCode=false;codeLines=[];codeLang='';}
        continue;
      }
      if(inCode){codeLines.push(line);continue;}
      // Image markdown
      const imgMatch=line.match(/!\[([^\]]*)\]\(([^)]+)\)/);
      if(imgMatch){out.push(<img key={i} src={imgMatch[2]} alt={imgMatch[1]} className="ai-img"/>);continue;}
      let p=line.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/\*(.+?)\*/g,'<em>$1</em>').replace(/`([^`]+)`/g,'<code class="ic">$1</code>').replace(/^### (.+)/,'<h3>$1</h3>').replace(/^## (.+)/,'<h2>$1</h2>').replace(/^# (.+)/,'<h1>$1</h1>').replace(/^[\-\*] (.+)/,'<li>$1</li>').replace(/^\d+\. (.+)/,'<li>$1</li>').replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" class="link">$1</a>');
      out.push(<p key={i} dangerouslySetInnerHTML={{__html:p||'&nbsp;'}}/>);
    }
    return out;
  }

  const empty=msgs.length===0&&!streamingText;
  const SUGGEST=['O que é síndrome do impostor?','Como lidar com ansiedade social?','Pesquise últimas notícias de psicologia','Navegue em https://psychology.org e me dê um resumo','Crie um código Python que analisa emoções em textos'];

  return(
    <div className="app">
      <aside className="sidebar">
        <div className="sb-top">
          <button className="nb" onClick={newChat}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg>
            Novo chat
          </button>
        </div>
        <div className="sb-list">
          {sessions.map(s=>(
            <div key={s.id} className={`si${s.id===sessionId?' active':''}`} onClick={()=>loadSession(s)}>
              {s.title}
            </div>
          ))}
        </div>
        <div className="sb-bot">
          <div className="ui"><div className="ua">D</div><div className="un">Daniela Coelho</div></div>
        </div>
      </aside>

      <main className="main">
        <header className="hdr">
          <div className="hm"><div className="ha">D</div><span>Daniela</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg></div>
          <button className="ib" onClick={newChat} title="Novo chat"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>
        </header>

        <div className="msgs">
          {empty&&(
            <div className="welcome">
              <div className="wl">
                <svg width="52" height="52" viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="#7c3aed" opacity="0.2"/><path d="M25 70 Q50 15 75 70" stroke="#7c3aed" strokeWidth="7" fill="none" strokeLinecap="round"/><circle cx="50" cy="50" r="9" fill="#7c3aed"/></svg>
              </div>
              <h1>Como posso ajudar?</h1>
              <div className="sugs">
                {SUGGEST.map(s=><button key={s} className="sug" onClick={()=>setInput(s)}>{s}</button>)}
              </div>
            </div>
          )}

          {msgs.map((m,i)=>(
            <div key={i} className={`mr ${m.role}`}>
              {m.role==='assistant'&&<div className="av as">D</div>}
              <div className="mb">
                <div className={`mc${m.role==='user'?' ub':''}`}>
                  {m.role==='assistant'?md(m.content):<p>{m.content}</p>}
                </div>
                <div className="ma">
                  <button onClick={()=>navigator.clipboard.writeText(m.content)} className="ab" title="Copiar">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  </button>
                </div>
              </div>
              {m.role==='user'&&<div className="av us">U</div>}
            </div>
          ))}

          {(loading||streamingText)&&(
            <div className="mr assistant">
              <div className="av as">D</div>
              <div className="mb">
                {toolStatus&&<div className="ts">{toolStatus}</div>}
                <div className="mc">
                  {streamingText?md(streamingText):<div className="typing"><span/><span/><span/></div>}
                  {streamingText&&<span className="cursor"/>}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef}/>
        </div>

        <div className="ia">
          {uploadedFile&&(
            <div className="fp">
              {uploadedFile.preview?<img src={uploadedFile.preview} className="fp-img" alt="preview"/>:<div className="fp-file">📎 {uploadedFile.name}</div>}
              <button onClick={()=>setUploadedFile(null)} className="fp-x">✕</button>
            </div>
          )}
          <div className="ic">
            <button className="ub2" onClick={()=>fileRef.current?.click()} title="Anexar arquivo">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            </button>
            <input ref={fileRef} type="file" accept="image/*,application/pdf,.txt,.js,.py,.ts,.jsx,.tsx,.json,.csv" onChange={handleFile} style={{display:'none'}}/>
            <textarea ref={taRef} className="it" placeholder="Mensagem para Daniela... (Shift+Enter para nova linha)" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={handleKey} rows={1}/>
            {loading?(
              <button className="sb stop" onClick={stopGeneration} title="Parar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
              </button>
            ):(
              <button className={`sb${input.trim()||uploadedFile?' active':''}`} onClick={send} disabled={!input.trim()&&!uploadedFile}>
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            )}
          </div>
          <div className="in">Daniela pode cometer erros. Verifique informações importantes.</div>
        </div>
      </main>

      <style>{`
        *{box-sizing:border-box;margin:0;padding:0;}
        :root{--bg:#0f0f0f;--s1:#1a1a1a;--s2:#242424;--s3:#2e2e2e;--br:#333;--t1:#f0f0f0;--t2:#888;--acc:#7c3aed;--acc2:#9461fd;--r:12px;}
        body{background:var(--bg);color:var(--t1);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:15px;}
        .app{display:flex;height:100vh;overflow:hidden;}
        .sidebar{width:250px;background:var(--s1);border-right:1px solid var(--br);display:flex;flex-direction:column;flex-shrink:0;}
        .sb-top{padding:12px 10px;}
        .nb{width:100%;display:flex;align-items:center;gap:8px;background:transparent;border:1px solid var(--br);color:var(--t1);padding:9px 14px;border-radius:8px;cursor:pointer;font-size:14px;transition:.2s;}
        .nb:hover{background:var(--s2);}
        .sb-list{flex:1;overflow-y:auto;padding:4px 8px;}
        .si{padding:9px 10px;border-radius:7px;cursor:pointer;font-size:13px;color:var(--t2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:.2s;margin-bottom:2px;}
        .si:hover,.si.active{background:var(--s2);color:var(--t1);}
        .sb-bot{padding:10px;border-top:1px solid var(--br);}
        .ui{display:flex;align-items:center;gap:9px;padding:7px;border-radius:7px;cursor:pointer;}
        .ui:hover{background:var(--s2);}
        .ua{width:30px;height:30px;background:var(--acc);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:#fff;flex-shrink:0;}
        .un{font-size:13px;font-weight:500;}
        .main{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden;}
        .hdr{display:flex;align-items:center;padding:12px 16px;border-bottom:1px solid var(--br);gap:10px;}
        .hm{display:flex;align-items:center;gap:8px;font-size:15px;font-weight:600;cursor:pointer;padding:5px 8px;border-radius:7px;}
        .hm:hover{background:var(--s2);}
        .ha{width:28px;height:28px;background:var(--acc);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;}
        .ib{margin-left:auto;background:transparent;border:none;color:var(--t2);cursor:pointer;padding:6px;border-radius:6px;display:flex;}
        .ib:hover{background:var(--s2);color:var(--t1);}
        .msgs{flex:1;overflow-y:auto;padding:20px 0;}
        .msgs::-webkit-scrollbar{width:5px;}
        .msgs::-webkit-scrollbar-thumb{background:var(--br);border-radius:3px;}
        .welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 24px;text-align:center;min-height:60%;}
        .wl{margin-bottom:20px;}
        .welcome h1{font-size:26px;font-weight:700;margin-bottom:28px;}
        .sugs{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:700px;}
        .sug{background:var(--s1);border:1px solid var(--br);color:var(--t2);padding:9px 14px;border-radius:20px;cursor:pointer;font-size:13px;transition:.2s;text-align:left;}
        .sug:hover{background:var(--s2);color:var(--t1);border-color:var(--acc);}
        .mr{display:flex;align-items:flex-start;gap:11px;padding:14px max(calc((100% - 820px)/2),20px);transition:.15s;}
        .mr:hover{background:rgba(255,255,255,0.02);}
        .mr.user{flex-direction:row-reverse;}
        .av{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0;}
        .as{background:var(--acc);color:#fff;}
        .us{background:#5865f2;color:#fff;}
        .mb{flex:1;min-width:0;max-width:740px;}
        .mc{font-size:15px;line-height:1.75;color:var(--t1);}
        .mc p{margin-bottom:8px;}
        .mc p:last-child{margin-bottom:0;}
        .mc h1{font-size:20px;margin:16px 0 8px;font-weight:700;}
        .mc h2{font-size:18px;margin:14px 0 6px;font-weight:700;}
        .mc h3{font-size:16px;margin:12px 0 5px;font-weight:600;}
        .mc li{margin-left:20px;margin-bottom:4px;}
        .mc strong{font-weight:700;color:#fff;}
        .mc em{font-style:italic;color:var(--t2);}
        .ic{background:var(--s2);border:1px solid var(--br);border-radius:4px;padding:2px 5px;font-family:monospace;font-size:13px;color:#e2a96b;}
        .link{color:var(--acc2);text-decoration:none;}
        .link:hover{text-decoration:underline;}
        .ai-img{max-width:100%;border-radius:8px;margin:8px 0;}
        .cb{background:#141420;border:1px solid var(--br);border-radius:10px;overflow:hidden;margin:10px 0;}
        .ch{display:flex;justify-content:space-between;align-items:center;padding:7px 13px;background:#1c1c2e;border-bottom:1px solid var(--br);}
        .cl{font-size:11px;color:var(--t2);font-family:monospace;text-transform:uppercase;}
        .cc{background:transparent;border:none;color:var(--t2);cursor:pointer;font-size:11px;padding:2px 7px;border-radius:3px;}
        .cc:hover{background:var(--s3);color:var(--t1);}
        .cb pre{padding:14px;overflow-x:auto;}
        .cb code{font-family:'JetBrains Mono','Fira Code',monospace;font-size:13px;line-height:1.6;color:#cdd6f4;}
        .ub{background:var(--s3);padding:11px 16px;border-radius:16px 16px 4px 16px;display:inline-block;}
        .ts{background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);border-radius:8px;padding:8px 12px;font-size:13px;color:var(--acc2);margin-bottom:10px;}
        .cursor{display:inline-block;width:2px;height:16px;background:var(--acc);animation:blink .8s infinite;vertical-align:text-bottom;margin-left:2px;}
        @keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
        .ma{display:flex;gap:3px;margin-top:5px;opacity:0;transition:.2s;}
        .mr:hover .ma{opacity:1;}
        .ab{background:transparent;border:none;color:var(--t2);cursor:pointer;padding:4px;border-radius:4px;display:flex;}
        .ab:hover{background:var(--s2);color:var(--t1);}
        .typing{display:flex;gap:5px;align-items:center;padding:8px 2px;}
        .typing span{width:7px;height:7px;background:var(--t2);border-radius:50%;animation:bounce 1.2s infinite;}
        .typing span:nth-child(2){animation-delay:.2s;}
        .typing span:nth-child(3){animation-delay:.4s;}
        @keyframes bounce{0%,60%,100%{transform:translateY(0);}30%{transform:translateY(-7px);}}
        .ia{padding:12px 16px;background:var(--bg);border-top:1px solid var(--br);}
        .fp{display:flex;align-items:center;gap:8px;padding:8px 14px;background:var(--s1);border:1px solid var(--br);border-radius:10px;margin-bottom:8px;max-width:820px;margin-left:auto;margin-right:auto;}
        .fp-img{width:50px;height:50px;object-fit:cover;border-radius:6px;}
        .fp-file{font-size:13px;color:var(--t2);}
        .fp-x{margin-left:auto;background:transparent;border:none;color:var(--t2);cursor:pointer;font-size:16px;padding:2px 6px;}
        .ic{max-width:820px;margin:0 auto;background:var(--s1);border:1px solid var(--br);border-radius:14px;display:flex;align-items:flex-end;gap:6px;padding:10px 12px;transition:.2s;}
        .ic:focus-within{border-color:var(--acc);}
        .ub2{background:transparent;border:none;color:var(--t2);cursor:pointer;padding:5px;border-radius:6px;display:flex;flex-shrink:0;transition:.2s;}
        .ub2:hover{background:var(--s2);color:var(--t1);}
        .it{flex:1;background:transparent;border:none;outline:none;color:var(--t1);font-size:15px;line-height:1.5;resize:none;max-height:200px;font-family:inherit;}
        .it::placeholder{color:var(--t2);}
        .sb{width:33px;height:33px;border-radius:8px;border:none;background:var(--s2);color:var(--t2);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:.2s;}
        .sb.active{background:var(--acc);color:#fff;}
        .sb.stop{background:rgba(239,68,68,0.2);color:#ef4444;border:1px solid rgba(239,68,68,0.3);}
        .sb:disabled{cursor:not-allowed;opacity:.4;}
        .in{text-align:center;font-size:11px;color:var(--t2);margin-top:7px;max-width:820px;margin-left:auto;margin-right:auto;}
        @media(max-width:768px){.sidebar{display:none;}.mr{padding:14px 14px;}}
      `}</style>
    </div>
  );
}
