'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, User } from '@/lib/auth-provider'
import { useIsAdmin, useIsManager } from '@/lib/usePermissions'

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const isAdmin = useIsAdmin()
  const isManager = useIsManager()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">
              {user.email} ({user.role})
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg leading-6 font-medium text-gray-900">
                Welcome, {user.first_name || user.username || user.email}!
              </h2>
              <p className="mt-2 max-w-2xl text-sm text-gray-500">
                Your role: <span className="font-semibold capitalize">{user.role}</span>
              </p>
            </div>
          </div>

          {/* Role-based Content */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* All Users Card */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Dashboard
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  View your personalized dashboard
                </p>
                <button className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                  Open Dashboard
                </button>
              </div>
            </div>

            {/* Admin/Manager: User Management */}
            {(isAdmin || isManager) && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    User Management
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Manage users and their roles
                  </p>
                  <button className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                    Manage Users
                  </button>
                </div>
              </div>
            )}

            {/* Admin Only: System Settings */}
            {isAdmin && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Admin Panel
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    System configuration and settings
                  </p>
                  <button className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                    Admin Panel
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* API Documentation Link */}
          <div className="mt-6 bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                API Documentation
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Access the API documentation and Swagger UI
              </p>
              <a
                href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/docs/`}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-block px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
              >
                Open API Docs
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
