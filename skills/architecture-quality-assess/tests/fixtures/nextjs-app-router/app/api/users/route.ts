import { NextResponse } from 'next/server'

export async function GET() {
  const users = [
    { id: 1, name: 'John' },
    { id: 2, name: 'Jane' },
  ]
  return NextResponse.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  return NextResponse.json({ id: 3, ...body })
}
