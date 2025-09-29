#!/bin/bash
set -euo pipefail

# Phase 2: Implement Component Co-location Pattern
# This script co-locates components with their tests, stories, and related files

echo "🚀 Phase 2: Implementing Component Co-location Pattern"
echo "====================================================="

cd frontend/src

echo "📦 Creating backup..."
cp -r . ../src-backup-phase2-$(date +%Y%m%d-%H%M%S)

echo "🏗️  Co-locating UI components..."

# Function to co-locate a component
colocate_component() {
  local component_path=$1
  local component_name=$(basename "$component_path" .tsx)
  local component_dir=$(dirname "$component_path")
  local new_dir="$component_dir/$component_name"
  
  if [ -f "$component_path" ]; then
    echo "📁 Co-locating $component_name..."
    
    # Create component directory
    mkdir -p "$new_dir"
    
    # Move the component file
    mv "$component_path" "$new_dir/"
    
    # Move test file if it exists
    for test_pattern in "__tests__/${component_name}.test.tsx" "${component_dir}/${component_name}.test.tsx" "__tests__/${component_name}.test.ts"; do
      if [ -f "$test_pattern" ]; then
        mv "$test_pattern" "$new_dir/"
        echo "  ✅ Moved test file"
        break
      fi
    done
    
    # Move story file if it exists
    if [ -f "${component_dir}/${component_name}.stories.tsx" ]; then
      mv "${component_dir}/${component_name}.stories.tsx" "$new_dir/"
      echo "  ✅ Moved story file"
    fi
    
    # Create index.ts barrel export
    cat > "$new_dir/index.ts" << EOF
export { ${component_name} } from './${component_name}';
EOF
    echo "  ✅ Created barrel export"
  fi
}

# Co-locate shared UI components
if [ -d "shared/components/ui" ]; then
  cd shared/components/ui
  
  for component in Button.tsx Modal.tsx Card.tsx Table.tsx Badge.tsx LoadingSpinner.tsx Form.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update ui/index.ts to use new structure
  cat > index.ts << 'EOF'
// UI Components - Co-located exports
export { Button } from './Button';
export { Modal } from './Modal';
export { Input, Textarea, Select } from './Form';
export { Table } from './Table';
export { Badge } from './Badge';
export { Card, MetricCard, ActivityItem, StatsGrid } from './Card';
export { LoadingSpinner, Skeleton, ProgressBar, PulseIndicator } from './LoadingSpinner';
export { Toaster } from './toaster';
EOF
  
  cd ../../..
fi

# Co-locate shared layout components
if [ -d "shared/components/layout" ]; then
  cd shared/components/layout
  
  for component in Header.tsx Sidebar.tsx Layout.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update layout/index.ts
  cat > index.ts << 'EOF'
// Layout Components - Co-located exports
export { Header } from './Header';
export { Sidebar } from './Sidebar'; 
export { Layout } from './Layout';
EOF
  
  cd ../../..
fi

echo "🔧 Co-locating feature components..."

# Co-locate auth feature components
if [ -d "features/auth/components" ]; then
  cd features/auth/components
  
  for component in LoginForm.tsx RegisterForm.tsx ProtectedRoute.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update components index
  cat > index.ts << 'EOF'
// Auth Components - Co-located exports
export { LoginForm } from './LoginForm';
export { RegisterForm } from './RegisterForm';
export { ProtectedRoute } from './ProtectedRoute';
EOF
  
  cd ../../..
fi

# Co-locate dashboard feature components  
if [ -d "features/dashboard/components" ]; then
  cd features/dashboard/components
  
  for component in Dashboard.tsx DashboardChart.tsx EnhancedMCPDashboard.tsx MCPControlPanel.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update components index
  cat > index.ts << 'EOF'
// Dashboard Components - Co-located exports
export { Dashboard } from './Dashboard';
export { DashboardChart } from './DashboardChart';
export { EnhancedMCPDashboard } from './EnhancedMCPDashboard';
export { MCPControlPanel } from './MCPControlPanel';
EOF
  
  cd ../../..
fi

# Co-locate agents feature components
if [ -d "features/agents/components" ]; then
  cd features/agents/components
  
  for component in Agents.tsx CreateAgentModal.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update components index
  cat > index.ts << 'EOF'
// Agents Components - Co-located exports
export { Agents } from './Agents';
export { CreateAgentModal } from './CreateAgentModal';
EOF
  
  cd ../../..
fi

# Co-locate workflows feature components
if [ -d "features/workflows/components" ]; then
  cd features/workflows/components
  
  for component in Workflows.tsx CreateWorkflowModal.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update components index  
  cat > index.ts << 'EOF'
// Workflows Components - Co-located exports
export { Workflows } from './Workflows';
export { CreateWorkflowModal } from './CreateWorkflowModal';
EOF
  
  cd ../../..
fi

# Co-locate models feature components
if [ -d "features/models/components" ]; then
  cd features/models/components
  
  for component in Models.tsx; do
    if [ -f "$component" ]; then
      colocate_component "$component"
    fi
  done
  
  # Update components index
  cat > index.ts << 'EOF'
// Models Components - Co-located exports  
export { Models } from './Models';
EOF
  
  cd ../../..
fi

echo "📝 Creating component templates for missing tests..."

# Function to create test template
create_test_template() {
  local component_dir=$1
  local component_name=$(basename "$component_dir")
  
  if [ ! -f "$component_dir/${component_name}.test.tsx" ]; then
    cat > "$component_dir/${component_name}.test.tsx" << EOF
import { render, screen } from '@testing-library/react';
import { ${component_name} } from './${component_name}';

describe('${component_name}', () => {
  it('renders without crashing', () => {
    render(<${component_name} />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  // Add more specific tests here
});
EOF
    echo "  ✅ Created test template for $component_name"
  fi
}

# Create test templates for components that don't have tests
find shared/components features/*/components -name "*.tsx" -not -path "*/index.ts" | while read -r component_file; do
  component_dir=$(dirname "$component_file")
  component_name=$(basename "$component_file" .tsx)
  
  if [ -d "$component_dir/$component_name" ]; then
    create_test_template "$component_dir/$component_name"
  fi
done

echo "🔧 Updating import statements in component files..."

# Function to update imports in a file
update_component_imports() {
  local file_path=$1
  
  if [ -f "$file_path" ]; then
    # Update relative imports to use barrel exports
    sed -i "s|from '\.\./\.\./shared/components/ui/\([^']*\)'|from '@/shared/components/ui'|g" "$file_path"
    sed -i "s|from '\.\./shared/components/ui/\([^']*\)'|from '@/shared/components/ui'|g" "$file_path"
    sed -i "s|from '\./components/ui/\([^']*\)'|from '@/shared/components/ui'|g" "$file_path"
  fi
}

# Update imports in all component files
find . -name "*.tsx" -not -path "./node_modules/*" | while read -r file; do
  update_component_imports "$file"
done

echo "✅ Phase 2 migration completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Run 'npm run build' to check for compilation errors"
echo "2. Run 'npm run test' to ensure all tests pass"
echo "3. Review component co-location structure"
echo "4. Add missing tests using the generated templates"
echo ""
echo "🔄 Rollback: If issues occur, restore from backup:"
echo "   cd src && rm -rf * && cp -r ../src-backup-phase2-* ."
echo ""