// app/api/setup/route.js — one-shot Vercel project creator
import{NextResponse}from'next/server';
const VTK=process.env.VERCEL_TOKEN;
const TEAM='team_zr9vAef0Zz3njNAiGm3v5Y3h';
const GK=process.env.GROQ_API_KEY,GEK=process.env.GEMINI_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;

export async function GET(){
  if(!VTK)return NextResponse.json({error:'VERCEL_TOKEN not configured'},{status:400});
  
  const results={};
  
  // 1. Create Vercel project
  const pr=await fetch(`https://api.vercel.com/v10/projects?teamId=${TEAM}`,{
    method:'POST',
    headers:{Authorization:`Bearer ${VTK}`,'Content-Type':'application/json'},
    body:JSON.stringify({name:'daniela-ia',gitRepository:{type:'github',repo:'tafita81/daniela-ia'},framework:'nextjs'})
  });
  const pd=await pr.json();
  results.project={status:pr.status,id:pd.id,name:pd.name,url:pd.alias?.[0]||'daniela-ia.vercel.app'};
  
  const projectId=pd.id;
  if(!projectId){return NextResponse.json({error:'Project creation failed',detail:pd});}
  
  // 2. Add env vars
  const envVars=[
    {key:'GROQ_API_KEY',value:GK||''},
    {key:'GEMINI_API_KEY',value:GEK||''},
    {key:'GH_PAT',value:PAT||''},
    {key:'NEXT_PUBLIC_SUPABASE_URL',value:SBU||''},
    {key:'SUPABASE_SERVICE_KEY',value:SBK||''},
    {key:'VERCEL_TOKEN',value:VTK},
    {key:'VERCEL_TEAM_ID',value:TEAM}
  ].filter(e=>e.value);
  
  const envResults=[];
  for(const env of envVars){
    const er=await fetch(`https://api.vercel.com/v10/projects/${projectId}/env?teamId=${TEAM}`,{
      method:'POST',
      headers:{Authorization:`Bearer ${VTK}`,'Content-Type':'application/json'},
      body:JSON.stringify({key:env.key,value:env.value,type:'encrypted',target:['production','preview']})
    });
    envResults.push({key:env.key,status:er.status});
  }
  results.envVars=envResults;
  
  // 3. Trigger deployment
  const dr=await fetch(`https://api.vercel.com/v13/deployments?teamId=${TEAM}`,{
    method:'POST',
    headers:{Authorization:`Bearer ${VTK}`,'Content-Type':'application/json'},
    body:JSON.stringify({name:'daniela-ia',gitSource:{type:'github',repo:'tafita81/daniela-ia',ref:'main'},projectId})
  });
  const dd=await dr.json();
  results.deployment={status:dr.status,id:dd.id,url:dd.url};
  
  return NextResponse.json({ok:true,...results,live_url:'https://daniela-ia.vercel.app'});
}
