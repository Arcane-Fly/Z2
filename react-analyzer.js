#!/usr/bin/env node
/**
 * React/TypeScript Project Analyzer for Architectural Optimization
 */

const fs = require('fs');
const path = require('path');

class ReactTypeScriptAnalyzer {
  constructor(projectPath) {
    this.projectPath = path.resolve(projectPath);
    this.packageJson = null;
    this.tsConfig = null;
    this.sourceFiles = [];
  }

  async analyze() {
    console.log(`🔍 Analyzing React/TypeScript project at: ${this.projectPath}`);
    
    await this.loadProjectConfig();
    await this.analyzeFileStructure();
    
    const architectureAssessment = this.assessArchitecture();
    const optimizationOpportunities = this.identifyOptimizationOpportunities();
    const migrationPlan = this.generateMigrationPlan(optimizationOpportunities);
    const validationChecklist = this.createValidationChecklist();
    
    return {
      issues_headline: this.generateIssuesHeadline(optimizationOpportunities),
      architecture_assessment: architectureAssessment,
      optimization_opportunities: optimizationOpportunities,
      executable_migration_plan: migrationPlan,
      validation_checklist: validationChecklist
    };
  }

  async loadProjectConfig() {
    try {
      const packagePath = path.join(this.projectPath, 'package.json');
      if (fs.existsSync(packagePath)) {
        this.packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      }
      
      const tsconfigPath = path.join(this.projectPath, 'tsconfig.json');
      if (fs.existsSync(tsconfigPath)) {
        this.tsConfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
      }
      
      console.log('✅ Project configuration loaded');
    } catch (error) {
      console.warn('⚠️  Error loading project configuration:', error);
    }
  }

  async analyzeFileStructure() {
    this.sourceFiles = this.collectSourceFiles(this.projectPath);
    console.log(`📁 Found ${this.sourceFiles.length} source files`);
  }

  collectSourceFiles(dirPath, files = []) {
    try {
      const entries = fs.readdirSync(dirPath);
      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !this.shouldIgnoreDirectory(entry)) {
          this.collectSourceFiles(fullPath, files);
        } else if (stat.isFile() && this.isSourceFile(entry)) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      // Skip directories we can't read
    }
    return files;
  }

  shouldIgnoreDirectory(name) {
    return ['node_modules', '.git', 'dist', 'build', '.next', 'coverage', '.yarn', '.cache', 'tmp'].includes(name);
  }

  isSourceFile(name) {
    return /\.(ts|tsx|js|jsx)$/.test(name);
  }

  assessArchitecture() {
    const srcPath = this.findSrcDirectory();
    return {
      current_patterns: {
        folder_structure_type: this.analyzeFolderStructure(srcPath),
        component_organization: this.analyzeComponentOrganization(),
        typescript_usage_depth: this.analyzeTypeScriptUsage(),
        domain_modeling_score: this.calculateDomainModelingScore(),
        coupling_analysis: this.analyzeCoupling()
      },
      modernization_readiness: {
        monorepo_score: this.calculateMonorepoScore(),
        micro_frontend_readiness: this.calculateMicroFrontendReadiness(),
        tree_shaking_optimization: this.calculateTreeShakingScore(),
        performance_optimization: this.calculatePerformanceScore()
      }
    };
  }

  findSrcDirectory() {
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

  analyzeFolderStructure(srcPath) {
    if (!fs.existsSync(srcPath)) return 'technical';
    
    const directories = fs.readdirSync(srcPath, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    
    const technicalDirs = ['components', 'hooks', 'utils', 'services', 'types', 'pages'];
    const featureDirs = ['features', 'modules', 'domains'];
    
    const hasTechnicalDirs = technicalDirs.some(dir => directories.includes(dir));
    const hasFeatureDirs = featureDirs.some(dir => directories.includes(dir));
    
    if (hasFeatureDirs && !hasTechnicalDirs) return 'feature-based';
    if (hasTechnicalDirs && !hasFeatureDirs) return 'technical';
    return 'mixed';
  }

  analyzeComponentOrganization() {
    const componentFiles = this.sourceFiles.filter(file => file.endsWith('.tsx'));
    let coLocatedCount = 0;
    
    for (const componentFile of componentFiles) {
      const dir = path.dirname(componentFile);
      const baseName = path.basename(componentFile, path.extname(componentFile));
      
      const hasTest = fs.existsSync(path.join(dir, `${baseName}.test.tsx`));
      const hasIndex = fs.existsSync(path.join(dir, 'index.ts'));
      
      if (hasTest || hasIndex) coLocatedCount++;
    }
    
    const ratio = coLocatedCount / componentFiles.length;
    if (ratio > 0.7) return 'co-located';
    if (ratio < 0.3) return 'scattered';
    return 'mixed';
  }

  analyzeTypeScriptUsage() {
    if (!this.tsConfig) return 'basic';
    
    const options = this.tsConfig.compilerOptions || {};
    let score = 0;
    
    if (options.strict) score += 20;
    if (options.noUnusedLocals) score += 10;
    if (options.paths) score += 15;
    if (options.moduleResolution === 'bundler') score += 10;
    
    if (score >= 40) return 'advanced';
    if (score >= 20) return 'intermediate';
    return 'basic';
  }

  calculateDomainModelingScore() {
    const typesFiles = this.sourceFiles.filter(file => 
      file.includes('/types/') || file.endsWith('.types.ts')
    );
    return Math.min(typesFiles.length * 15, 100);
  }

  analyzeCoupling() {
    return []; // Simplified for now
  }

  calculateMonorepoScore() {
    let score = 0;
    if (this.packageJson?.workspaces) score += 40;
    if (fs.existsSync(path.join(this.projectPath, 'nx.json'))) score += 30;
    if (this.packageJson?.packageManager?.includes('yarn')) score += 15;
    return Math.min(score, 100);
  }

  calculateMicroFrontendReadiness() {
    let score = 0;
    const srcPath = this.findSrcDirectory();
    if (fs.existsSync(path.join(srcPath, 'features'))) score += 30;
    if (fs.existsSync(path.join(srcPath, 'shared'))) score += 20;
    return Math.min(score, 100);
  }

  calculateTreeShakingScore() {
    let score = 50;
    if (fs.existsSync(path.join(this.projectPath, 'vite.config.ts'))) score += 10;
    return score;
  }

  calculatePerformanceScore() {
    return 60; // Default score
  }

  identifyOptimizationOpportunities() {
    const p0Issues = [];
    const p1Issues = [];
    const p2Issues = [];
    
    if (this.assessArchitecture().current_patterns.folder_structure_type === 'technical') {
      p0Issues.push({
        title: 'Technical Folder Structure Anti-Pattern',
        description: 'Current structure groups files by technical role rather than business features.',
        impact: 'high',
        complexity: 'high',
        affected_files: ['src/components/*', 'src/hooks/*', 'src/services/*'],
        migration_effort_hours: 16
      });
    }
    
    if (!this.tsConfig?.compilerOptions?.strict) {
      p0Issues.push({
        title: 'TypeScript Strict Mode Disabled',
        description: 'Strict mode is not enabled, reducing type safety.',
        impact: 'high',
        complexity: 'medium',
        affected_files: ['tsconfig.json'],
        migration_effort_hours: 8
      });
    }
    
    if (this.assessArchitecture().current_patterns.component_organization === 'scattered') {
      p1Issues.push({
        title: 'Component Co-location Missing',
        description: 'Components are not co-located with their tests and related files.',
        impact: 'medium',
        complexity: 'medium',
        affected_files: this.sourceFiles.filter(f => f.endsWith('.tsx')),
        migration_effort_hours: 12
      });
    }
    
    return { p0_foundation: p0Issues, p1_enhancement: p1Issues, p2_optimization: p2Issues };
  }

  generateMigrationPlan(opportunities) {
    const phase1 = [];
    const phase2 = [];
    const phase3 = [];
    
    opportunities.p0_foundation.forEach(issue => {
      if (issue.title.includes('Technical Folder Structure')) {
        phase1.push({
          step: 'Migrate to Feature-Based Architecture',
          description: 'Reorganize codebase from technical grouping to feature-based domains',
          commands: [
            'mkdir -p src/features/{auth,dashboard,agents,workflows,models}',
            'mkdir -p src/shared/{components,hooks,utils,types}',
            'mv src/components/LoginForm.tsx src/features/auth/components/',
            'mv src/components/ui/* src/shared/components/ui/'
          ],
          validation: ['npm run build', 'npm run test'],
          rollback_strategy: 'Git revert to restore original structure'
        });
      }
    });
    
    return {
      phase_1_foundation: phase1,
      phase_2_enhancement: phase2, 
      phase_3_optimization: phase3
    };
  }

  generateIssuesHeadline(opportunities) {
    const totalIssues = opportunities.p0_foundation.length + 
                       opportunities.p1_enhancement.length + 
                       opportunities.p2_optimization.length;
    
    const criticalIssues = opportunities.p0_foundation.filter(issue => issue.impact === 'high').length;
    const summary = criticalIssues > 0 
      ? `${criticalIssues} critical architectural issues found requiring immediate attention.`
      : `${totalIssues} optimization opportunities identified.`;
    
    return {
      summary,
      total_issues: totalIssues,
      p0_count: opportunities.p0_foundation.length,
      p1_count: opportunities.p1_enhancement.length,
      p2_count: opportunities.p2_optimization.length
    };
  }

  createValidationChecklist() {
    return [
      '✅ All tests pass after migration (npm run test)',
      '✅ TypeScript compilation successful (npm run type-check)',
      '✅ Application builds without errors (npm run build)',
      '✅ Development server starts correctly (npm run dev)',
      '✅ Core user flows work correctly in browser',
      '✅ ESLint passes with no errors (npm run lint)'
    ];
  }
}

async function main() {
  const projectPath = process.argv[2] || process.cwd();
  
  if (!fs.existsSync(projectPath)) {
    console.error(`❌ Project path does not exist: ${projectPath}`);
    process.exit(1);
  }
  
  console.log('🚀 React/TypeScript Project Analyzer v1.0.0');
  
  try {
    const analyzer = new ReactTypeScriptAnalyzer(projectPath);
    const result = await analyzer.analyze();
    
    console.log('\n📊 Analysis Complete!\n');
    console.log(JSON.stringify(result, null, 2));
    
    const outputPath = path.join(projectPath, 'architecture-analysis.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`\n💾 Results saved to: ${outputPath}`);
    
  } catch (error) {
    console.error('❌ Analysis failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { ReactTypeScriptAnalyzer };