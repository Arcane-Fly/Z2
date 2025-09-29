#!/usr/bin/env node
/**
 * React/TypeScript Project Analyzer for Architectural Optimization
 * 
 * Analyzes React/TypeScript projects for modernization opportunities and generates
 * executable plans aligned with 2025 best practices.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// Types for analysis results
interface AnalysisResult {
  issues_headline: {
    summary: string;
    total_issues: number;
    p0_count: number;
    p1_count: number;
    p2_count: number;
  };
  architecture_assessment: {
    current_patterns: {
      folder_structure_type: 'technical' | 'feature-based' | 'mixed';
      component_organization: 'scattered' | 'co-located' | 'mixed';
      typescript_usage_depth: 'basic' | 'intermediate' | 'advanced';
      domain_modeling_score: number;
      coupling_analysis: string[];
    };
    modernization_readiness: {
      monorepo_score: number;
      micro_frontend_readiness: number;
      tree_shaking_optimization: number;
      performance_optimization: number;
    };
  };
  optimization_opportunities: {
    p0_foundation: Issue[];
    p1_enhancement: Issue[];
    p2_optimization: Issue[];
  };
  executable_migration_plan: {
    phase_1_foundation: MigrationStep[];
    phase_2_enhancement: MigrationStep[];
    phase_3_optimization: MigrationStep[];
  };
  validation_checklist: string[];
}

interface Issue {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  complexity: 'low' | 'medium' | 'high';
  affected_files: string[];
  migration_effort_hours: number;
}

interface MigrationStep {
  step: string;
  description: string;
  commands: string[];
  config_diffs?: ConfigDiff[];
  validation: string[];
  rollback_strategy: string;
}

interface ConfigDiff {
  file: string;
  changes: {
    before: string;
    after: string;
  };
}

interface FileStructure {
  path: string;
  isDirectory: boolean;
  children?: FileStructure[];
  extension?: string;
  size?: number;
}

interface PackageJson {
  name?: string;
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
  scripts?: Record<string, string>;
  workspaces?: string[];
  type?: string;
  packageManager?: string;
  sideEffects?: boolean | string[];
  [key: string]: any;
}

interface TsConfig {
  compilerOptions?: {
    strict?: boolean;
    target?: string;
    module?: string;
    moduleResolution?: string;
    baseUrl?: string;
    paths?: Record<string, string[]>;
    [key: string]: any;
  };
  include?: string[];
  exclude?: string[];
}

class ReactTypeScriptAnalyzer {
  private projectPath: string;
  private packageJson: PackageJson | null = null;
  private tsConfig: TsConfig | null = null;
  private fileStructure: FileStructure | null = null;
  private sourceFiles: string[] = [];
  
  constructor(projectPath: string) {
    this.projectPath = path.resolve(projectPath);
  }

  async analyze(): Promise<AnalysisResult> {
    console.log(`🔍 Analyzing React/TypeScript project at: ${this.projectPath}`);
    
    // Load project configuration
    await this.loadProjectConfig();
    
    // Analyze file structure
    await this.analyzeFileStructure();
    
    // Assess architecture patterns
    const architectureAssessment = this.assessArchitecture();
    
    // Identify optimization opportunities
    const optimizationOpportunities = this.identifyOptimizationOpportunities();
    
    // Generate migration plan
    const migrationPlan = this.generateMigrationPlan(optimizationOpportunities);
    
    // Create validation checklist
    const validationChecklist = this.createValidationChecklist();
    
    const result: AnalysisResult = {
      issues_headline: this.generateIssuesHeadline(optimizationOpportunities),
      architecture_assessment: architectureAssessment,
      optimization_opportunities: optimizationOpportunities,
      executable_migration_plan: migrationPlan,
      validation_checklist: validationChecklist
    };
    
    return result;
  }

  private async loadProjectConfig(): Promise<void> {
    try {
      // Load package.json
      const packagePath = path.join(this.projectPath, 'package.json');
      if (fs.existsSync(packagePath)) {
        this.packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      }
      
      // Load tsconfig.json
      const tsconfigPath = path.join(this.projectPath, 'tsconfig.json');
      if (fs.existsSync(tsconfigPath)) {
        this.tsConfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
      }
      
      console.log('✅ Project configuration loaded');
    } catch (error) {
      console.warn('⚠️  Error loading project configuration:', error);
    }
  }

  private async analyzeFileStructure(): Promise<void> {
    this.fileStructure = this.buildFileStructure(this.projectPath);
    this.sourceFiles = this.collectSourceFiles(this.fileStructure);
    console.log(`📁 Found ${this.sourceFiles.length} source files`);
  }

  private buildFileStructure(dirPath: string, maxDepth: number = 5, currentDepth: number = 0): FileStructure {
    const stats = fs.statSync(dirPath);
    const name = path.basename(dirPath);
    
    if (stats.isDirectory()) {
      const children: FileStructure[] = [];
      
      if (currentDepth < maxDepth && !this.shouldIgnoreDirectory(name)) {
        try {
          const entries = fs.readdirSync(dirPath);
          for (const entry of entries) {
            const entryPath = path.join(dirPath, entry);
            children.push(this.buildFileStructure(entryPath, maxDepth, currentDepth + 1));
          }
        } catch (error) {
          // Permission or other errors - skip directory
        }
      }
      
      return {
        path: dirPath,
        isDirectory: true,
        children: children
      };
    } else {
      return {
        path: dirPath,
        isDirectory: false,
        extension: path.extname(dirPath),
        size: stats.size
      };
    }
  }

  private shouldIgnoreDirectory(name: string): boolean {
    const ignorePatterns = [
      'node_modules', '.git', 'dist', 'build', '.next', 
      'coverage', '.yarn', '.cache', 'tmp'
    ];
    return ignorePatterns.includes(name);
  }

  private collectSourceFiles(structure: FileStructure): string[] {
    const sourceFiles: string[] = [];
    const sourceExtensions = ['.ts', '.tsx', '.js', '.jsx'];
    
    const traverse = (node: FileStructure) => {
      if (node.isDirectory && node.children) {
        node.children.forEach(traverse);
      } else if (node.extension && sourceExtensions.includes(node.extension)) {
        sourceFiles.push(node.path);
      }
    };
    
    if (structure) {
      traverse(structure);
    }
    
    return sourceFiles;
  }

  private assessArchitecture() {
    const srcPath = this.findSrcDirectory();
    const folderStructureType = this.analyzeFolderStructure(srcPath);
    const componentOrganization = this.analyzeComponentOrganization(srcPath);
    const typescriptUsage = this.analyzeTypeScriptUsage();
    const domainModelingScore = this.calculateDomainModelingScore();
    const couplingAnalysis = this.analyzeCoupling();
    
    return {
      current_patterns: {
        folder_structure_type: folderStructureType,
        component_organization: componentOrganization,
        typescript_usage_depth: typescriptUsage,
        domain_modeling_score: domainModelingScore,
        coupling_analysis: couplingAnalysis
      },
      modernization_readiness: {
        monorepo_score: this.calculateMonorepoScore(),
        micro_frontend_readiness: this.calculateMicroFrontendReadiness(),
        tree_shaking_optimization: this.calculateTreeShakingScore(),
        performance_optimization: this.calculatePerformanceScore()
      }
    };
  }

  private findSrcDirectory(): string {
    // Look for src directory in project root or frontend subdirectory
    const candidates = [
      path.join(this.projectPath, 'src'),
      path.join(this.projectPath, 'frontend', 'src'),
      path.join(this.projectPath, 'app', 'src')
    ];
    
    for (const candidate of candidates) {
      if (fs.existsSync(candidate)) {
        return candidate;
      }
    }
    
    return this.projectPath;
  }

  private analyzeFolderStructure(srcPath: string): 'technical' | 'feature-based' | 'mixed' {
    if (!fs.existsSync(srcPath)) {
      return 'technical';
    }
    
    const directories = fs.readdirSync(srcPath, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    
    const technicalDirs = ['components', 'hooks', 'utils', 'services', 'types', 'pages'];
    const featureDirs = ['features', 'modules', 'domains'];
    
    const hasTechnicalDirs = technicalDirs.some(dir => directories.includes(dir));
    const hasFeatureDirs = featureDirs.some(dir => directories.includes(dir));
    
    if (hasFeatureDirs && !hasTechnicalDirs) {
      return 'feature-based';
    } else if (hasTechnicalDirs && !hasFeatureDirs) {
      return 'technical';
    } else {
      return 'mixed';
    }
  }

  private analyzeComponentOrganization(srcPath: string): 'scattered' | 'co-located' | 'mixed' {
    const componentFiles = this.sourceFiles.filter(file => 
      file.includes('component') || file.endsWith('.tsx')
    );
    
    let coLocatedCount = 0;
    let scatteredCount = 0;
    
    for (const componentFile of componentFiles) {
      const dir = path.dirname(componentFile);
      const baseName = path.basename(componentFile, path.extname(componentFile));
      
      // Check for co-location patterns
      const hasTest = fs.existsSync(path.join(dir, `${baseName}.test.tsx`)) ||
                     fs.existsSync(path.join(dir, `${baseName}.test.ts`));
      const hasStory = fs.existsSync(path.join(dir, `${baseName}.stories.tsx`));
      const hasIndex = fs.existsSync(path.join(dir, 'index.ts')) ||
                      fs.existsSync(path.join(dir, 'index.tsx'));
      
      if (hasTest || hasStory || hasIndex) {
        coLocatedCount++;
      } else {
        scatteredCount++;
      }
    }
    
    const coLocationRatio = coLocatedCount / (coLocatedCount + scatteredCount);
    
    if (coLocationRatio > 0.7) {
      return 'co-located';
    } else if (coLocationRatio < 0.3) {
      return 'scattered';
    } else {
      return 'mixed';
    }
  }

  private analyzeTypeScriptUsage(): 'basic' | 'intermediate' | 'advanced' {
    if (!this.tsConfig) {
      return 'basic';
    }
    
    const options = this.tsConfig.compilerOptions || {};
    let score = 0;
    
    // Strict mode configuration
    if (options.strict) score += 20;
    if (options.noUnusedLocals) score += 10;
    if (options.noUnusedParameters) score += 10;
    if (options.noImplicitAny) score += 10;
    
    // Advanced TypeScript features
    if (options.paths) score += 15;
    if (options.baseUrl) score += 10;
    if (options.moduleResolution === 'bundler') score += 10;
    
    // Check for branded types and advanced patterns in source files
    const advancedPatterns = this.checkForAdvancedTypeScriptPatterns();
    score += advancedPatterns * 5;
    
    if (score >= 70) return 'advanced';
    if (score >= 40) return 'intermediate';
    return 'basic';
  }

  private checkForAdvancedTypeScriptPatterns(): number {
    let patternCount = 0;
    const patterns = [
      'type.*=.*&.*{',  // Intersection types
      'type.*=.*\\|.*{', // Union types
      'interface.*extends.*<', // Generic interfaces
      'const.*=.*<.*>.*\\(', // Generic functions
      'keyof typeof', // Keyof typeof pattern
      'Record<.*,.*>', // Record types
      'Partial<.*>', // Utility types
      'Pick<.*,.*>', // Pick utility type
    ];
    
    for (const file of this.sourceFiles.slice(0, 20)) { // Sample first 20 files
      try {
        const content = fs.readFileSync(file, 'utf8');
        for (const pattern of patterns) {
          if (new RegExp(pattern).test(content)) {
            patternCount++;
          }
        }
      } catch (error) {
        // Skip files that can't be read
      }
    }
    
    return Math.min(patternCount, 10); // Cap at 10
  }

  private calculateDomainModelingScore(): number {
    // Analyze types directory and interface definitions
    const typesFiles = this.sourceFiles.filter(file => 
      file.includes('/types/') || file.endsWith('.types.ts')
    );
    
    let score = Math.min(typesFiles.length * 10, 50); // Base score from type files
    
    // Check for domain-specific type organization
    for (const file of typesFiles) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('interface') && content.includes('export')) {
          score += 5;
        }
        // Check for branded types
        if (content.includes('& { __brand:')) {
          score += 10;
        }
      } catch (error) {
        // Skip files that can't be read
      }
    }
    
    return Math.min(score, 100);
  }

  private analyzeCoupling(): string[] {
    const couplingIssues: string[] = [];
    
    // Check for direct imports between business domains
    const imports = this.extractImportStatements();
    
    // Analyze cross-domain dependencies
    const domains = ['auth', 'dashboard', 'agent', 'workflow', 'model'];
    for (const domain1 of domains) {
      for (const domain2 of domains) {
        if (domain1 !== domain2) {
          const crossImports = imports.filter(imp => 
            imp.fromFile.includes(domain1) && imp.toPath.includes(domain2)
          );
          if (crossImports.length > 2) {
            couplingIssues.push(`High coupling between ${domain1} and ${domain2} domains (${crossImports.length} imports)`);
          }
        }
      }
    }
    
    return couplingIssues;
  }

  private extractImportStatements(): Array<{fromFile: string, toPath: string}> {
    const imports: Array<{fromFile: string, toPath: string}> = [];
    
    for (const file of this.sourceFiles.slice(0, 50)) { // Sample files for performance
      try {
        const content = fs.readFileSync(file, 'utf8');
        const importRegex = /import.*from\s+['"]([^'"]+)['"]/g;
        let match;
        
        while ((match = importRegex.exec(content)) !== null) {
          imports.push({
            fromFile: file,
            toPath: match[1]
          });
        }
      } catch (error) {
        // Skip files that can't be read
      }
    }
    
    return imports;
  }

  private calculateMonorepoScore(): number {
    let score = 0;
    
    // Check for monorepo indicators
    if (this.packageJson?.workspaces) score += 40;
    if (fs.existsSync(path.join(this.projectPath, 'nx.json'))) score += 30;
    if (fs.existsSync(path.join(this.projectPath, 'turbo.json'))) score += 30;
    if (fs.existsSync(path.join(this.projectPath, 'lerna.json'))) score += 25;
    
    // Check for yarn workspaces configuration
    if (this.packageJson?.packageManager?.includes('yarn')) score += 15;
    
    // Multiple package.json files indicate workspace structure
    const packageJsons = this.sourceFiles.filter(file => file.endsWith('package.json'));
    if (packageJsons.length > 1) score += 20;
    
    return Math.min(score, 100);
  }

  private calculateMicroFrontendReadiness(): number {
    let score = 0;
    
    // Module federation configuration
    if (fs.existsSync(path.join(this.projectPath, 'module-federation.config.js'))) score += 50;
    
    // Feature-based architecture
    const srcPath = this.findSrcDirectory();
    if (fs.existsSync(path.join(srcPath, 'features'))) score += 30;
    
    // Shared component library
    if (fs.existsSync(path.join(srcPath, 'shared'))) score += 20;
    
    // Independent routing
    const routerFiles = this.sourceFiles.filter(file => 
      file.includes('router') || file.includes('routes')
    );
    if (routerFiles.length > 0) score += 15;
    
    // API abstraction
    const serviceFiles = this.sourceFiles.filter(file => 
      file.includes('/services/') || file.includes('/api/')
    );
    if (serviceFiles.length > 2) score += 10;
    
    return Math.min(score, 100);
  }

  private calculateTreeShakingScore(): number {
    let score = 50; // Base score
    
    // Check for barrel exports
    const barrelFiles = this.sourceFiles.filter(file => 
      file.endsWith('index.ts') || file.endsWith('index.tsx')
    );
    
    for (const barrel of barrelFiles.slice(0, 10)) {
      try {
        const content = fs.readFileSync(barrel, 'utf8');
        // Named exports are better for tree-shaking than default exports
        const namedExports = (content.match(/export\s*{[^}]*}/g) || []).length;
        const reExports = (content.match(/export\s*\*\s*from/g) || []).length;
        
        if (namedExports > reExports) {
          score += 5;
        } else if (reExports > namedExports) {
          score -= 5;
        }
      } catch (error) {
        // Skip files that can't be read
      }
    }
    
    // Check build configuration for optimization
    if (fs.existsSync(path.join(this.projectPath, 'vite.config.ts'))) {
      score += 10;
    }
    
    return Math.max(0, Math.min(score, 100));
  }

  private calculatePerformanceScore(): number {
    let score = 40; // Base score
    
    // Code splitting indicators
    const dynamicImports = this.countDynamicImports();
    score += Math.min(dynamicImports * 10, 30);
    
    // Bundle size optimization
    const buildConfig = this.analyzeBuildConfig();
    if (buildConfig.hasManualChunks) score += 15;
    if (buildConfig.hasTreeShaking) score += 15;
    if (buildConfig.hasMinification) score += 10;
    
    return Math.min(score, 100);
  }

  private countDynamicImports(): number {
    let count = 0;
    
    for (const file of this.sourceFiles.slice(0, 30)) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        const dynamicImportRegex = /import\s*\(/g;
        const matches = content.match(dynamicImportRegex);
        if (matches) count += matches.length;
      } catch (error) {
        // Skip files that can't be read
      }
    }
    
    return count;
  }

  private analyzeBuildConfig(): {hasManualChunks: boolean, hasTreeShaking: boolean, hasMinification: boolean} {
    const result = { hasManualChunks: false, hasTreeShaking: false, hasMinification: false };
    
    const configFiles = [
      'vite.config.ts', 'vite.config.js',
      'webpack.config.js', 'webpack.config.ts'
    ];
    
    for (const configFile of configFiles) {
      const configPath = path.join(this.projectPath, configFile);
      if (fs.existsSync(configPath)) {
        try {
          const content = fs.readFileSync(configPath, 'utf8');
          if (content.includes('manualChunks')) result.hasManualChunks = true;
          if (content.includes('treeshake') || content.includes('sideEffects')) result.hasTreeShaking = true;
          if (content.includes('minif') || content.includes('terser')) result.hasMinification = true;
        } catch (error) {
          // Skip files that can't be read
        }
      }
    }
    
    return result;
  }

  private identifyOptimizationOpportunities() {
    const p0Issues: Issue[] = [];
    const p1Issues: Issue[] = [];
    const p2Issues: Issue[] = [];
    
    // P0 - Foundation Issues
    if (this.assessArchitecture().current_patterns.folder_structure_type === 'technical') {
      p0Issues.push({
        title: 'Technical Folder Structure Anti-Pattern',
        description: 'Current structure groups files by technical role (components/, hooks/, etc.) rather than business features. This creates high coupling and poor maintainability.',
        impact: 'high',
        complexity: 'high',
        affected_files: ['src/components/*', 'src/hooks/*', 'src/services/*'],
        migration_effort_hours: 16
      });
    }
    
    if (!this.tsConfig?.compilerOptions?.strict) {
      p0Issues.push({
        title: 'TypeScript Strict Mode Disabled',
        description: 'Strict mode is not enabled, reducing type safety and potential runtime errors.',
        impact: 'high',
        complexity: 'medium',
        affected_files: ['tsconfig.json'],
        migration_effort_hours: 8
      });
    }
    
    // P1 - Enhancement Issues
    if (this.assessArchitecture().current_patterns.component_organization === 'scattered') {
      p1Issues.push({
        title: 'Component Co-location Missing',
        description: 'Components are not co-located with their tests, stories, and related files, reducing maintainability.',
        impact: 'medium',
        complexity: 'medium',
        affected_files: this.sourceFiles.filter(f => f.endsWith('.tsx')),
        migration_effort_hours: 12
      });
    }
    
    const treeShakingScore = this.calculateTreeShakingScore();
    if (treeShakingScore < 60) {
      p1Issues.push({
        title: 'Suboptimal Tree-Shaking Configuration',
        description: 'Bundle size could be reduced through better tree-shaking optimization and barrel export patterns.',
        impact: 'medium',
        complexity: 'medium',
        affected_files: this.sourceFiles.filter(f => f.endsWith('index.ts')),
        migration_effort_hours: 6
      });
    }
    
    // P2 - Optimization Issues
    const monorepoScore = this.calculateMonorepoScore();
    if (monorepoScore < 30 && this.sourceFiles.length > 50) {
      p2Issues.push({
        title: 'Monorepo Migration Opportunity',
        description: 'Project size and complexity suggest benefits from monorepo architecture for better code sharing and build optimization.',
        impact: 'low',
        complexity: 'high',
        affected_files: ['package.json', 'tsconfig.json'],
        migration_effort_hours: 24
      });
    }
    
    const performanceScore = this.calculatePerformanceScore();
    if (performanceScore < 60) {
      p2Issues.push({
        title: 'Bundle Optimization Opportunities',
        description: 'Application bundle size and loading performance could be improved through code splitting and optimization.',
        impact: 'medium',
        complexity: 'medium',
        affected_files: ['vite.config.ts', 'src/App.tsx'],
        migration_effort_hours: 8
      });
    }
    
    return {
      p0_foundation: p0Issues,
      p1_enhancement: p1Issues,
      p2_optimization: p2Issues
    };
  }

  private generateMigrationPlan(opportunities: any) {
    const phase1: MigrationStep[] = [];
    const phase2: MigrationStep[] = [];
    const phase3: MigrationStep[] = [];
    
    // Phase 1: Foundation (P0 Issues)
    opportunities.p0_foundation.forEach((issue: Issue) => {
      if (issue.title.includes('Technical Folder Structure')) {
        phase1.push({
          step: 'Migrate to Feature-Based Architecture',
          description: 'Reorganize codebase from technical grouping to feature-based domains',
          commands: [
            'mkdir -p src/features/{auth,dashboard,agents,workflows,models}',
            'mkdir -p src/shared/{components,hooks,utils,types}',
            '# Move domain-specific components to feature directories',
            'mv src/components/LoginForm.tsx src/features/auth/components/',
            'mv src/components/RegisterForm.tsx src/features/auth/components/',
            'mv src/hooks/useAuth.tsx src/features/auth/hooks/',
            'mv src/services/auth.ts src/features/auth/services/',
            '# Move shared components to shared directory',
            'mv src/components/ui/* src/shared/components/ui/',
            'mv src/components/layout/* src/shared/components/layout/'
          ],
          config_diffs: [{
            file: 'tsconfig.json',
            changes: {
              before: '"paths": {\n      "@/*": ["./src/*"]\n    }',
              after: '"paths": {\n      "@/*": ["./src/*"],\n      "@/features/*": ["./src/features/*"],\n      "@/shared/*": ["./src/shared/*"]\n    }'
            }
          }],
          validation: [
            'npm run build',
            'npm run test',
            'npm run type-check'
          ],
          rollback_strategy: 'Git revert to previous commit, restore original folder structure'
        });
      }
      
      if (issue.title.includes('TypeScript Strict Mode')) {
        phase1.push({
          step: 'Enable TypeScript Strict Mode',
          description: 'Enable strict type checking for better type safety',
          commands: [
            '# Update tsconfig.json incrementally',
            'npm run type-check 2>&1 | tee type-errors.log',
            '# Fix type errors systematically'
          ],
          config_diffs: [{
            file: 'tsconfig.json',
            changes: {
              before: '"strict": false',
              after: '"strict": true,\n    "noUncheckedIndexedAccess": true,\n    "exactOptionalPropertyTypes": true'
            }
          }],
          validation: [
            'npm run type-check',
            'npm run test'
          ],
          rollback_strategy: 'Revert tsconfig.json changes and fix types gradually'
        });
      }
    });
    
    // Phase 2: Enhancement (P1 Issues)
    opportunities.p1_enhancement.forEach((issue: Issue) => {
      if (issue.title.includes('Component Co-location')) {
        phase2.push({
          step: 'Implement Component Co-location Pattern',
          description: 'Co-locate component files with tests and related assets',
          commands: [
            '# Create component directories with co-location',
            'for component in Button Modal Card; do',
            '  mkdir -p src/shared/components/ui/$component',
            '  mv src/shared/components/ui/$component.tsx src/shared/components/ui/$component/',
            '  mv src/__tests__/$component.test.tsx src/shared/components/ui/$component/ 2>/dev/null || true',
            '  echo "export { $component } from \'./$component\';" > src/shared/components/ui/$component/index.ts',
            'done'
          ],
          validation: [
            'npm run build',
            'npm run test'
          ],
          rollback_strategy: 'Flatten component structure back to single files'
        });
      }
      
      if (issue.title.includes('Tree-Shaking')) {
        phase2.push({
          step: 'Optimize Tree-Shaking and Barrel Exports',
          description: 'Improve bundle size through better tree-shaking patterns',
          commands: [
            '# Update barrel exports to use named exports only',
            'find src -name "index.ts" -exec sed -i "s/export \\* from/export { default as ComponentName } from/g" {} \\;',
            '# Add sideEffects: false to package.json'
          ],
          config_diffs: [{
            file: 'package.json',
            changes: {
              before: '"type": "module"',
              after: '"type": "module",\n  "sideEffects": false'
            }
          }],
          validation: [
            'npm run build',
            'npm run bundle-analyzer'
          ],
          rollback_strategy: 'Revert barrel export changes and remove sideEffects flag'
        });
      }
    });
    
    // Phase 3: Optimization (P2 Issues)
    opportunities.p2_optimization.forEach((issue: Issue) => {
      if (issue.title.includes('Bundle Optimization')) {
        phase3.push({
          step: 'Implement Advanced Bundle Optimization',
          description: 'Add code splitting and performance optimizations',
          commands: [
            '# Add lazy loading for routes',
            'npm install @loadable/component',
            '# Update routing to use code splitting'
          ],
          config_diffs: [{
            file: 'vite.config.ts',
            changes: {
              before: 'rollupOptions: {\n      output: {\n        manualChunks: undefined,\n      },\n    }',
              after: 'rollupOptions: {\n      output: {\n        manualChunks: {\n          vendor: [\'react\', \'react-dom\'],\n          router: [\'react-router-dom\'],\n          ui: [\'@heroicons/react\']\n        },\n      },\n    }'
            }
          }],
          validation: [
            'npm run build',
            'npm run preview',
            'lighthouse --chrome-flags="--headless" http://localhost:4173'
          ],
          rollback_strategy: 'Remove code splitting and revert to single bundle'
        });
      }
    });
    
    return {
      phase_1_foundation: phase1,
      phase_2_enhancement: phase2,
      phase_3_optimization: phase3
    };
  }

  private generateIssuesHeadline(opportunities: any) {
    const totalIssues = opportunities.p0_foundation.length + 
                       opportunities.p1_enhancement.length + 
                       opportunities.p2_optimization.length;
    
    const criticalIssues = opportunities.p0_foundation.filter((issue: Issue) => issue.impact === 'high').length;
    const summary = criticalIssues > 0 
      ? `${criticalIssues} critical architectural issues found requiring immediate attention. Project uses technical folder structure anti-pattern and lacks strict TypeScript configuration.`
      : totalIssues > 0 
      ? `${totalIssues} optimization opportunities identified. Project has solid foundation but can benefit from modern architectural patterns.`
      : 'Project follows modern React/TypeScript best practices. Minor optimization opportunities available.';
    
    return {
      summary,
      total_issues: totalIssues,
      p0_count: opportunities.p0_foundation.length,
      p1_count: opportunities.p1_enhancement.length,
      p2_count: opportunities.p2_optimization.length
    };
  }

  private createValidationChecklist(): string[] {
    return [
      '✅ All tests pass after migration (npm run test)',
      '✅ TypeScript compilation successful (npm run type-check)',
      '✅ Application builds without errors (npm run build)',
      '✅ Development server starts correctly (npm run dev)',
      '✅ Bundle size analysis shows improvements (npm run bundle-analyzer)',
      '✅ Core user flows work correctly in browser',
      '✅ No console errors or warnings in development',
      '✅ ESLint passes with no errors (npm run lint)',
      '✅ Component co-location pattern implemented correctly',
      '✅ Feature boundaries clearly defined and isolated',
      '✅ Shared components properly exported from barrel files',
      '✅ Performance metrics maintained or improved',
      '✅ Accessibility standards maintained (npm run a11y:test)'
    ];
  }
}

// CLI Interface
async function main() {
  const projectPath = process.argv[2] || process.cwd();
  
  if (!fs.existsSync(projectPath)) {
    console.error(`❌ Project path does not exist: ${projectPath}`);
    process.exit(1);
  }
  
  console.log('🚀 React/TypeScript Project Analyzer v1.0.0');
  console.log('   Analyzing for 2025 architectural best practices\n');
  
  try {
    const analyzer = new ReactTypeScriptAnalyzer(projectPath);
    const result = await analyzer.analyze();
    
    console.log('\n📊 Analysis Complete!\n');
    console.log(JSON.stringify(result, null, 2));
    
    // Write results to file
    const outputPath = path.join(projectPath, 'architecture-analysis.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`\n💾 Results saved to: ${outputPath}`);
    
  } catch (error) {
    console.error('❌ Analysis failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

export { ReactTypeScriptAnalyzer, AnalysisResult };