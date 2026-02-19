'use client'

import { useAuth, User } from './auth-provider'

// Role definitions
export type Role = 'admin' | 'manager' | 'user'

// Permission definitions
export const ROLE_PERMISSIONS: Record<Role, string[]> = {
  admin: [
    'manage_users',
    'manage_roles',
    'view_dashboard',
    'edit_profile',
    'view_profile',
  ],
  manager: [
    'view_dashboard',
    'manage_users',
    'edit_profile',
    'view_profile',
  ],
  user: [
    'view_dashboard',
    'edit_profile',
    'view_profile',
  ],
}

// Check if user has a specific role
export function useHasRole(...roles: Role[]): boolean {
  const { user, isAuthenticated } = useAuth()
  
  if (!isAuthenticated || !user) {
    return false
  }
  
  return roles.includes(user.role as Role)
}

// Check if user has a specific permission
export function useHasPermission(...permissions: string[]): boolean {
  const { user, isAuthenticated } = useAuth()
  
  if (!isAuthenticated || !user) {
    return false
  }
  
  const userPermissions = ROLE_PERMISSIONS[user.role as Role] || []
  
  return permissions.some(permission => userPermissions.includes(permission))
}

// Check if user is admin
export function useIsAdmin(): boolean {
  return useHasRole('admin')
}

// Check if user is manager or admin
export function useIsManager(): boolean {
  return useHasRole('manager', 'admin')
}

// Higher-order component for protected routes
export function withRole<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  allowedRoles: Role[]
): React.FC<P> {
  return function WithRoleComponent(props: P) {
    const { user, isAuthenticated, isLoading } = useAuth()
    
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      )
    }
    
    if (!isAuthenticated) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
      return null
    }
    
    if (!allowedRoles.includes(user?.role as Role)) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
            <p className="mt-2 text-gray-600">You don't have permission to access this page.</p>
          </div>
        </div>
      )
    }
    
    return <WrappedComponent {...props} />
  }
}
