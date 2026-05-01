// app/api/ia-chat/route.js — DANIELA EXECUTOR V9D + BROWSER
import{NextResponse}from'next/server';
const GK=process.env.GROQ_API_KEY,TK=process.env.TOGETHER_API_KEY,GEK=process.env.GEMINI_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;
const REPO='tafita81/Repovazio',VER='V9D-BROWSER-2026-05-01';
const BASE_URL=process.env.NEXT_PUBLIC_BASE_URL||'https://repovazio.vercel.app';

const TOOLS=[
  {type:'function',function:{name:'github_read_file',description:'Lê arquivo do repo GitHub tafita81/Repovazio',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_list_dir',description:'Lista arquivos/dirs do repo GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_write_file',description:'Cria/atualiza arquivo no GitHub + deploy automático Vercel',parameters:{type:'object',properties:{path:{type:'string'},content:{type:'string'},message:{type:'string'},repo:{type:'string'}},required:['path','content','message']}}},
  {type:'function',function:{name:'github_create_repo',description:'Cria novo repositório GitHub do zero',parameters:{type:'object',properties:{name:{type:'string'},description:{type:'string'},private:{type:'boolean'}},required:['name']}}},
  {type:'function',function:{name:'supabase_select',description:'SELECT em tabela Supabase',parameters:{type:'object',properties:{table:{type:'string'},filter:{type:'string'},limit:{type:'number'}},required:['table']}}},
  {type:'function',function:{name:'supabase_sql',description:'Executa SQL no Supabase: CREATE TABLE, INSERT, UPDATE etc',parameters:{type:'object',properties:{sql:{type:'string'}},required:['sql']}}},
  {type:'function',function:{name:'web_fetch',description:'Busca conteúdo de qualquer URL da internet',parameters:{type:'object',properties:{url:{type:'string'}},required:['url']}}}];

function b64e(s){return Buffer.from(s,'utf-8').toString('base64');}
function b64d(s){return Buffer.from(s.replace(/\n/g,''),'base64').toString('utf-8');}
