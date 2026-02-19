import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">
          Django + Next.js JWT RBAC
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Secure authentication with Role-Based Access Control
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
          >
            Register
          </Link>
        </div>
        
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">JWT Authentication</h3>
            <p className="text-gray-600">
              Secure token-based authentication with refresh tokens and blacklist support
            </p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">RBAC</h3>
            <p className="text-gray-600">
              Role-Based Access Control with Admin, Manager, and User roles
            </p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Production Ready</h3>
            <p className="text-gray-600">
              Docker, HTTPS, CORS, and security headers configured
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
