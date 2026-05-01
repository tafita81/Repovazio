import{NextResponse}from'next/server';
export async function GET(){return NextResponse.json({status:'browser-disabled',msg:'Puppeteer nao disponivel no Vercel free tier'});}
export async function POST(){return NextResponse.json({status:'browser-disabled',msg:'Puppeteer nao disponivel no Vercel free tier'});}
