% Yarn Constraints for Z2 Workspace
% Based on Railway + Yarn 4.9.2+ Master Cheat Sheet

% Enforce Node.js 20+ across all workspaces
gen_enforced_field(WorkspaceCwd, 'engines.node', '>=20.0.0').

% Enforce Yarn 4.9.2+ across all workspaces
gen_enforced_field(WorkspaceCwd, 'engines.yarn', '>=4.9.2').

% Enforce workspace protocol for internal dependencies
gen_enforced_dependency(WorkspaceCwd, DependencyIdent, 'workspace:*', DependencyType) :-
  workspace_has_dependency(WorkspaceCwd, DependencyIdent, _, DependencyType),
  workspace_ident(_, DependencyIdent).

% Ensure consistent dependency versions across workspaces
gen_enforced_dependency(WorkspaceCwd, DependencyIdent, DependencyRange2, DependencyType) :-
  workspace_has_dependency(WorkspaceCwd, DependencyIdent, DependencyRange, DependencyType),
  workspace_has_dependency(OtherWorkspaceCwd, DependencyIdent, DependencyRange2, DependencyType2),
  DependencyRange \= DependencyRange2.

% Enforce MIT license across all workspaces
gen_enforced_field(WorkspaceCwd, 'license', 'MIT') :-
  \+ workspace_field(WorkspaceCwd, 'private', true).
