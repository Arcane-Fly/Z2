/**
 * Enhanced Card Component with better visual hierarchy and animations
 * Refactored to use unified design system utilities
 */

import React from 'react';
import { 
  cn, 
  INTERACTIVE, 
  SPACING, 
  SHADOWS, 
  TRANSITIONS
} from '../../utils/design-system';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outline' | 'filled';
  size?: keyof typeof SPACING.component;
  hover?: boolean;
  interactive?: boolean;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  size = 'md',
  hover = false,
  interactive = false,
  className,
  onClick
}) => {
  const variantClasses = {
    default: cn(INTERACTIVE.card),
    elevated: cn('bg-white border-0', SHADOWS.lg),
    outline: 'bg-transparent border-2 border-gray-300 rounded-lg',
    filled: 'bg-gray-50 border border-gray-200 rounded-lg'
  };

  const interactiveClasses = interactive || onClick ? cn(
    'cursor-pointer',
    'hover:shadow-md',
    TRANSITIONS.default
  ) : '';

  const hoverClasses = hover ? cn(
    'hover:scale-105',
    TRANSITIONS.transform
  ) : '';
  
  const CardComponent = onClick ? 'button' : 'div';
  
  return (
    <CardComponent
      className={cn(
        variantClasses[variant],
        SPACING.component[size],
        interactiveClasses,
        hoverClasses,
        className
      )}
      onClick={onClick}
      type={onClick ? 'button' : undefined}
    >
      {children}
    </CardComponent>
  );
};

/**
 * Metric Card Component for dashboard statistics
 */
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: {
    value: string;
    trend: 'up' | 'down' | 'stable';
  };
  icon?: React.ReactNode;
  description?: string;
  status?: 'good' | 'warning' | 'error';
  loading?: boolean;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  icon,
  description,
  status = 'good',
  loading = false,
  className
}) => {
  const statusClasses = {
    good: 'border-green-200 bg-green-50',
    warning: 'border-yellow-200 bg-yellow-50',
    error: 'border-red-200 bg-red-50'
  };

  const changeClasses = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-600'
  };

  if (loading) {
    return (
      <Card className={cn('relative', className)}>
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-2">
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            <div className="h-6 w-6 bg-gray-200 rounded"></div>
          </div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-full"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      variant="default" 
      hover
      className={cn(
        'relative overflow-hidden',
        statusClasses[status],
        className
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">{title}</h3>
        {icon && (
          <div className="text-gray-400">
            {icon}
          </div>
        )}
      </div>
      
      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold text-gray-900">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
        {change && (
          <span className={cn(
            'text-sm font-medium flex items-center',
            changeClasses[change.trend]
          )}>
            {change.trend === 'up' && '↗'}
            {change.trend === 'down' && '↘'}
            {change.trend === 'stable' && '→'}
            {change.value}
          </span>
        )}
      </div>
      
      {description && (
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      )}

      {/* Status indicator */}
      <div className={cn(
        'absolute top-0 left-0 w-1 h-full',
        status === 'good' && 'bg-green-500',
        status === 'warning' && 'bg-yellow-500',
        status === 'error' && 'bg-red-500'
      )} />
    </Card>
  );
};

/**
 * Activity Feed Card
 */
interface ActivityItemProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'warning' | 'error' | 'info';
}

export const ActivityItem: React.FC<ActivityItemProps> = ({
  icon,
  title,
  description,
  timestamp,
  status
}) => {
  const statusClasses = {
    success: 'text-green-600 bg-green-100',
    warning: 'text-yellow-600 bg-yellow-100',
    error: 'text-red-600 bg-red-100',
    info: 'text-blue-600 bg-blue-100'
  };

  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div className={cn(
        'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
        statusClasses[status]
      )}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{title}</p>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      <div className="flex-shrink-0">
        <span className="text-xs text-gray-400">{timestamp}</span>
      </div>
    </div>
  );
};

/**
 * Stats Grid Container
 */
interface StatsGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  className?: string;
}

export const StatsGrid: React.FC<StatsGridProps> = ({
  children,
  columns = 4,
  className
}) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className={cn(
      'grid gap-4',
      gridClasses[columns],
      className
    )}>
      {children}
    </div>
  );
};