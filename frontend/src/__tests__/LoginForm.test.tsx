import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../test-utils'
import { LoginForm } from '../components/LoginForm'

// Mock the useAuth hook
const mockLogin = vi.fn()
const mockClearError = vi.fn()

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    clearError: mockClearError,
    authState: {
      isLoading: false,
      error: null,
    },
  }),
}))

describe('LoginForm Component', () => {
  const mockOnSuccess = vi.fn()
  const mockOnSwitchToRegister = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form correctly', () => {
    render(<LoginForm onSuccess={mockOnSuccess} onSwitchToRegister={mockOnSwitchToRegister} />)
    
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in to z2/i })).toBeInTheDocument()
  })

  it('has proper accessibility labels', () => {
    render(<LoginForm />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in to z2/i })
    
    expect(usernameInput).toHaveAttribute('required')
    expect(passwordInput).toHaveAttribute('required')
    expect(submitButton).toHaveAttribute('type', 'submit')
  })

  it('handles form input changes', () => {
    render(<LoginForm />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass' } })
    
    expect(usernameInput).toHaveValue('testuser')
    expect(passwordInput).toHaveValue('testpass')
  })

  it('handles remember me checkbox', () => {
    render(<LoginForm />)
    
    const rememberMeCheckbox = screen.getByRole('checkbox', { name: /remember me/i })
    
    expect(rememberMeCheckbox).not.toBeChecked()
    
    fireEvent.click(rememberMeCheckbox)
    expect(rememberMeCheckbox).toBeChecked()
  })

  it('toggles password visibility', () => {
    render(<LoginForm />)
    
    const passwordInput = screen.getByLabelText(/password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')
    
    // Find and click the password visibility toggle button
    const toggleButton = passwordInput.parentElement?.querySelector('button[type="button"]')
    expect(toggleButton).toBeInTheDocument()
    
    if (toggleButton) {
      fireEvent.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'text')
      
      fireEvent.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'password')
    }
  })

  it('submits form with correct data', async () => {
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in to z2/i })
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass' } })
    
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockClearError).toHaveBeenCalled()
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpass',
        remember_me: false,
      })
    })
  })

  it('calls onSuccess when login is successful', async () => {
    mockLogin.mockResolvedValueOnce(undefined)
    
    render(<LoginForm onSuccess={mockOnSuccess} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in to z2/i })
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } })
    fireEvent.change(passwordInput, { target: { value: 'testpass' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('shows register link when onSwitchToRegister is provided', () => {
    render(<LoginForm onSwitchToRegister={mockOnSwitchToRegister} />)
    
    const registerLink = screen.getByRole('button', { name: /create your account/i })
    expect(registerLink).toBeInTheDocument()
    
    fireEvent.click(registerLink)
    expect(mockOnSwitchToRegister).toHaveBeenCalled()
  })

  it('does not show register link when onSwitchToRegister is not provided', () => {
    render(<LoginForm />)
    
    const registerLink = screen.queryByRole('button', { name: /create your account/i })
    expect(registerLink).not.toBeInTheDocument()
  })

  it('has proper form structure for keyboard navigation', () => {
    render(<LoginForm />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const rememberCheckbox = screen.getByRole('checkbox', { name: /remember me/i })
    const submitButton = screen.getByRole('button', { name: /sign in to z2/i })
    
    // Test tab order
    usernameInput.focus()
    expect(usernameInput).toHaveFocus()
    
    // All form elements should be focusable
    expect(usernameInput).toHaveAttribute('id')
    expect(passwordInput).toHaveAttribute('id')
    expect(rememberCheckbox).toHaveAttribute('id')
    expect(submitButton).toHaveAttribute('type', 'submit')
  })
})