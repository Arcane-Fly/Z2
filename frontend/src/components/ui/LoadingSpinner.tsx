/**
 * Enhanced Loading Spinner Component
 * Provides multiple loading states with smooth animations
 */

import React from 'react';
import { clsx } from 'clsx';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'accent';
  text?: string;
  overlay?: boolean;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  text,
  overlay = false,
  className
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const variantClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    accent: 'text-purple-600'
  };

  const spinner = (
    <div className={clsx(
      'flex flex-col items-center justify-center gap-2',
      overlay && 'fixed inset-0 bg-black/20 backdrop-blur-sm z-50',
      className
    )}>
      <div className={clsx(
        'animate-spin rounded-full border-2 border-current border-t-transparent',
        sizeClasses[size],
        variantClasses[variant]
      )} />
      {text && (
        <p className={clsx(
          'text-sm font-medium',
          variantClasses[variant]
        )}>
          {text}
        </p>
      )}
    </div>
  );

  return spinner;
};

/**
 * Skeleton Loader Component for better perceived performance
 */
interface SkeletonProps {
  className?: string;
  rows?: number;
  variant?: 'text' | 'circular' | 'rectangular';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  rows = 1,
  variant = 'text'
}) => {
  const baseClasses = 'animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%]';
  
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md'
  };

  if (rows === 1) {
    return (
      <div className={clsx(
        baseClasses,
        variantClasses[variant],
        className
      )} />
    );
  }

  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className={clsx(
            baseClasses,
            variantClasses[variant],
            className,
            index === rows - 1 && 'w-3/4' // Last row is shorter
          )}
        />
      ))}
    </div>
  );
};

/**
 * Progress Bar Component
 */
interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  className
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const variantClasses = {
    primary: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-red-600'
  };

  return (
    <div className={clsx('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={clsx(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        sizeClasses[size]
      )}>
        <div
          className={clsx(
            'transition-all duration-300 ease-out rounded-full',
            sizeClasses[size],
            variantClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

/**
 * Pulse Animation Component for live indicators
 */
interface PulseIndicatorProps {
  active?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'green' | 'blue' | 'red' | 'yellow';
  className?: string;
}

export const PulseIndicator: React.FC<PulseIndicatorProps> = ({
  active = true,
  size = 'md',
  color = 'green',
  className
}) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const colorClasses = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500'
  };

  return (
    <div className={clsx('relative', className)}>
      <div className={clsx(
        'rounded-full',
        sizeClasses[size],
        colorClasses[color],
        active && 'animate-pulse'
      )} />
      {active && (
        <div className={clsx(
          'absolute inset-0 rounded-full animate-ping',
          sizeClasses[size],
          colorClasses[color],
          'opacity-75'
        )} />
      )}
    </div>
  );
};