import{NextResponse}from'next/server';
export async function GET(){
  return NextResponse.json({version:'MONITOR-V2',status:'ok',ts:new Date().toISOString()});
}
