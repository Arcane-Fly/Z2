import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../hooks/usePermissions';

export function Header() {
  const { authState, logout } = useAuth();
  const { isSuperuser } = usePermissions();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              AI Workforce Platform
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            {authState.isAuthenticated && authState.user ? (
              <>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Welcome,</span>
                  <span className="text-sm font-medium text-gray-900">
                    {authState.user.username}
                  </span>
                  {isSuperuser && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Superuser
                    </span>
                  )}
                  <span className="text-xs text-gray-400 capitalize">
                    ({authState.user.user_type})
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  Logout
                </button>
              </>
            ) : (
              <div className="text-sm text-gray-500">
                Welcome to Z2
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}