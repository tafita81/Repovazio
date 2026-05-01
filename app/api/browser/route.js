import{NextResponse}from'next/server';

export const maxDuration=30;
export const dynamic='force-dynamic';

async function getBrowser(){
  // Tenta puppeteer-core + chromium no Vercel
  try{
    const chromium=await import('@sparticuz/chromium');
    const puppeteer=await import('puppeteer-core');
    return await puppeteer.default.launch({
      args:chromium.default.args,
      defaultViewport:chromium.default.defaultViewport,
      executablePath:await chromium.default.executablePath(),
      headless:chromium.default.headless,
    });
  }catch{
    try{
      const puppeteer=await import('puppeteer');
      return await puppeteer.default.launch({headless:'new',args:['--no-sandbox','--disable-setuid-sandbox']});
    }catch(e){throw new Error('Browser não disponível: '+e.message);}
  }
}
