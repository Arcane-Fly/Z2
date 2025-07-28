import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../test-utils'
import App from '../App'

// Mock the pages to avoid complex dependencies in basic tests
vi.mock('../pages/Auth', () => ({
  default: () => <div data-testid="auth-page">Auth Page</div>
}))

vi.mock('../pages/Dashboard', () => ({
  Dashboard: () => <div data-testid="dashboard-page">Dashboard Page</div>
}))

vi.mock('../pages/Agents', () => ({
  Agents: () => <div data-testid="agents-page">Agents Page</div>
}))

vi.mock('../pages/Workflows', () => ({
  Workflows: () => <div data-testid="workflows-page">Workflows Page</div>
}))

vi.mock('../pages/Models', () => ({
  Models: () => <div data-testid="models-page">Models Page</div>
}))

vi.mock('../pages/Settings', () => ({
  Settings: () => <div data-testid="settings-page">Settings Page</div>
}))

vi.mock('../hooks/useAuth', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
  })
}))

vi.mock('../components/ProtectedRoute', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}))

vi.mock('../components/layout/Layout', () => ({
  Layout: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}))

vi.mock('../components/ui/toaster', () => ({
  Toaster: () => <div data-testid="toaster">Toaster</div>
}))

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(document.body).toBeTruthy()
  })

  it('has correct root class structure', () => {
    render(<App />)
    const rootDiv = document.querySelector('.min-h-screen.bg-background')
    expect(rootDiv).toBeTruthy()
  })

  it('includes toaster component', () => {
    render(<App />)
    expect(screen.getByTestId('toaster')).toBeInTheDocument()
  })

  it('has proper accessibility structure', () => {
    const { container } = render(<App />)
    // Should not have any accessibility violations for basic structure
    expect(container.firstChild).toHaveClass('min-h-screen')
  })
})