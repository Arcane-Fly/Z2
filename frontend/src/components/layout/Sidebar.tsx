import { NavLink } from 'react-router-dom'
import { cn } from '../../utils'
import { usePermissions } from '../../hooks/usePermissions'
import {
  HomeIcon,
  CpuChipIcon,
  Cog6ToothIcon,
  RectangleGroupIcon,
  ChartBarIcon,
  UsersIcon,
  ServerStackIcon,
} from '@heroicons/react/24/outline'

const baseNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Agents', href: '/agents', icon: CpuChipIcon },
  { name: 'Workflows', href: '/workflows', icon: RectangleGroupIcon },
  { name: 'Models', href: '/models', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

const adminNavigation = [
  { name: 'User Management', href: '/admin/users', icon: UsersIcon },
  { name: 'System Admin', href: '/admin/system', icon: ServerStackIcon },
]

export function Sidebar() {
  const { isSuperuser, canManageUsers } = usePermissions();
  
  // Add admin navigation items for superusers or users who can manage users
  const navigation = [...baseNavigation];
  if (isSuperuser || canManageUsers()) {
    navigation.push(...adminNavigation);
  }

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="flex-1 flex flex-col min-h-0 bg-gray-900">
        <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-4">
            <h1 className="text-white text-xl font-bold">Z2 Platform</h1>
            {isSuperuser && (
              <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-500 text-white">
                ADMIN
              </span>
            )}
          </div>
          <nav className="mt-5 flex-1 px-2 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md'
                  )
                }
              >
                <item.icon
                  className="mr-3 flex-shrink-0 h-6 w-6"
                  aria-hidden="true"
                />
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </div>
  )
}