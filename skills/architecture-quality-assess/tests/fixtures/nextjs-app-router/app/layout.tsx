import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Test App',
  description: 'Test fixture for Next.js App Router',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
