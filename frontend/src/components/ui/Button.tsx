import { ReactNode, ButtonHTMLAttributes } from 'react';
import { 
  cn, 
  INTERACTIVE, 
  COLOR_VARIANTS, 
  SIZE_VARIANTS,
  type ColorVariant,
  type SizeVariant 
} from '../../utils/design-system';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ColorVariant | 'ghost';
  size?: SizeVariant;
  children: ReactNode;
  loading?: boolean;
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  loading = false,
  disabled,
  className,
  ...props 
}: ButtonProps) {
  const getVariantClasses = () => {
    if (variant === 'ghost') {
      return 'text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:ring-gray-500';
    }
    
    const colors = COLOR_VARIANTS[variant as ColorVariant];
    return cn(
      colors.bg,
      colors.bgHover,
      'text-white',
      `focus:ring-${colors.ring.split('-')[1]}-500`
    );
  };
  
  return (
    <button
      className={cn(
        INTERACTIVE.button,
        getVariantClasses(),
        SIZE_VARIANTS[size].padding,
        SIZE_VARIANTS[size].text,
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg 
          className="w-4 h-4 mr-2 animate-spin" 
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
}