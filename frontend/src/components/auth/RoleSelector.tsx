import { useState } from 'react';

interface RoleSelectorProps {
  value: string;
  onChange: (role: string) => void;
  error?: string;
  disabled?: boolean;
}

const ROLES = [
  { 
    value: 'developer', 
    label: 'Developer', 
    description: 'Build and deploy AI agents, create workflows', 
    icon: '🧑‍💻' 
  },
  { 
    value: 'operator', 
    label: 'Operator', 
    description: 'Use pre-built solutions, monitor operations', 
    icon: '👨‍💼' 
  },
  { 
    value: 'admin', 
    label: 'Admin', 
    description: 'Manage users, configure systems, full access', 
    icon: '⚙️' 
  }
];

export function RoleSelector({ value, onChange, error, disabled = false }: RoleSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedRole = ROLES.find(r => r.value === value);

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        User Role <span className="text-red-500">*</span>
      </label>
      
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-3 py-2 text-left border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
          error 
            ? 'border-red-500 bg-red-50' 
            : disabled 
            ? 'border-gray-200 bg-gray-50 cursor-not-allowed text-gray-400'
            : 'border-gray-300 bg-white hover:border-gray-400'
        }`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {selectedRole ? (
              <>
                <span className="text-lg">{selectedRole.icon}</span>
                <div>
                  <div className="font-medium text-gray-900">{selectedRole.label}</div>
                  <div className="text-sm text-gray-500">{selectedRole.description}</div>
                </div>
              </>
            ) : (
              <span className="text-gray-500">Select a role...</span>
            )}
          </div>
          <svg 
            className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      
      {isOpen && !disabled && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {ROLES.map(role => (
              <button
                key={role.value}
                type="button"
                onClick={() => {
                  onChange(role.value);
                  setIsOpen(false);
                }}
                className={`w-full px-3 py-3 text-left hover:bg-gray-50 focus:outline-none focus:bg-gray-50 transition-colors ${
                  value === role.value ? 'bg-blue-50 text-blue-900' : ''
                }`}
                role="option"
                aria-selected={value === role.value}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{role.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{role.label}</div>
                    <div className="text-sm text-gray-600">{role.description}</div>
                  </div>
                  {value === role.value && (
                    <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </button>
            ))}
          </div>
        </>
      )}
      
      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}